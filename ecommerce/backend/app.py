from flask import Flask, jsonify, request, send_from_directory, Response
import psycopg2, json, pika, os, uuid
from prometheus_client import Counter, Histogram, generate_latest
from logging_config import setup_logger

startup_log = setup_logger('startup')
api_log     = setup_logger('api')
order_log   = setup_logger('order')

app = Flask(__name__, static_folder='../frontend')

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'postgres'),
    'database': os.getenv('DB_NAME', 'shop'),
    'user': os.getenv('DB_USER', 'shop'),
    'password': os.getenv('DB_PASSWORD', 'shop123')
}

REQUESTS = Counter('shop_requests_total', 'Total requests', ['endpoint', 'method'])
LATENCY = Histogram('shop_latency_seconds', 'Request latency', ['endpoint'])

def get_db():
    return psycopg2.connect(**DB_CONFIG)

def publish_order(order, request_id):
    conn = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    ch = conn.channel()
    ch.queue_declare(queue='orders')
    body = json.dumps({**order, 'request_id': request_id})
    ch.basic_publish(exchange='', routing_key='orders', body=body)
    conn.close()
    order_log.info(f"[{request_id}] published to RabbitMQ | queue=orders")

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/products')
def products():
    REQUESTS.labels('/api/products', 'GET').inc()
    rid = request.headers.get('X-Request-ID', str(uuid.uuid4())[:8])
    with LATENCY.labels('/api/products').time():
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT id, name, category, price, description, stock FROM products ORDER BY id')
        rows = cur.fetchall()
        conn.close()
        api_log.info(f"[{rid}] GET /api/products | 200 | returned {len(rows)} products")
        return jsonify([{'id': r[0], 'name': r[1], 'category': r[2], 'price': float(r[3]), 'description': r[4], 'stock': r[5]} for r in rows])

@app.route('/api/orders', methods=['POST'])
def create_order():
    REQUESTS.labels('/api/orders', 'POST').inc()
    rid = request.headers.get('X-Request-ID', str(uuid.uuid4())[:8])
    with LATENCY.labels('/api/orders').time():
        data = request.json
        product_id = data.get('product_id', 'MISSING')
        api_log.info(f"[{rid}] POST /api/orders | incoming | product_id={product_id}")
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT name, price FROM products WHERE id = %s', (product_id,))
        product = cur.fetchone()
        if not product:
            api_log.warning(f"[{rid}] POST /api/orders | 404 | product_id={product_id} NOT FOUND")
            return jsonify({'error': 'product not found'}), 404
        cur.execute('INSERT INTO orders (product_id, product_name, price, status) VALUES (%s, %s, %s, %s) RETURNING id',
                    (product_id, product[0], product[1], 'confirmed'))
        order_id = cur.fetchone()[0]
        conn.commit()
        conn.close()
        order_log.info(f"[{rid}] order #{order_id} created | product={product[0]} | EUR {product[1]}")
        order = {'order_id': order_id, 'product': product[0], 'price': float(product[1])}
        publish_order(order, rid)
        return jsonify({**order, 'request_id': rid}), 201

@app.route('/api/orders')
def list_orders():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    offset = (page - 1) * per_page
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM orders')
    total = cur.fetchone()[0]
    cur.execute('SELECT id, product_name, price, status, created_at FROM orders ORDER BY id DESC LIMIT %s OFFSET %s',
                (per_page, offset))
    rows = cur.fetchall()
    conn.close()
    return jsonify({
        'total': total,
        'page': page,
        'per_page': per_page,
        'orders': [{'id': r[0], 'product': r[1], 'price': float(r[2]), 'status': r[3], 'time': r[4].strftime('%Y-%m-%d %H:%M:%S')} for r in rows]
    })

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype='text/plain; version=0.0.4; charset=utf-8')

if __name__ == '__main__':
    startup_log.info("=" * 50)
    startup_log.info("Order API starting on port 5000")
    startup_log.info(f"DB config: host={DB_CONFIG['host']}, db={DB_CONFIG['database']}")
    startup_log.info("Connecting to PostgreSQL...")
    try:
        conn = get_db()
        startup_log.info("PostgreSQL connected OK")
        conn.close()
    except Exception as e:
        startup_log.critical(f"PostgreSQL connection FAILED: {e}")
    startup_log.info("Connecting to RabbitMQ...")
    try:
        conn = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        startup_log.info("RabbitMQ connected OK")
        conn.close()
    except Exception as e:
        startup_log.critical(f"RabbitMQ connection FAILED: {e}")
    startup_log.info("Startup complete, ready to accept requests")
    app.run(host='0.0.0.0', port=5000)
