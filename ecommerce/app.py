from flask import Flask, jsonify, request, Response, render_template
import psycopg2, pika, uuid
from prometheus_client import Counter, Histogram, generate_latest
from logging_config import setup_logger

startup_log = setup_logger('startup')
api_log = setup_logger('api')
order_log = setup_logger('order')
app = Flask(__name__)
DB = {'host':'192.168.0.155','database':'shop','user':'shop','password':'shop123'}
MQ = '192.168.0.155'
REQUESTS = Counter('shop_requests_total','Total requests',['endpoint','method'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/product/<int:pid>')
def detail(pid):
    conn = psycopg2.connect(**DB); cur = conn.cursor()
    cur.execute("SELECT id,name,category,price,COALESCE(image,''),stock FROM products WHERE id=%s",(pid,))
    r = cur.fetchone(); conn.close()
    if not r: return "Not found", 404
    p = {'id':r[0],'name':r[1],'category':r[2],'price':float(r[3]),'image':r[4],'stock':r[5]}
    return render_template('product.html', p=p)

@app.route('/orders')
def orders_page():
    return render_template('orders.html')

@app.route('/api/categories')
def categories():
    conn = psycopg2.connect(**DB); cur = conn.cursor()
    cur.execute("SELECT DISTINCT category FROM products ORDER BY category")
    rows = [r[0] for r in cur.fetchall()]; conn.close()
    return jsonify(rows)

@app.route('/api/products')
def products():
    REQUESTS.labels('/api/products','GET').inc()
    pg = int(request.args.get('page',1)); per = int(request.args.get('per',20))
    cat = request.args.get('category',''); s = request.args.get('search','')
    off = (pg-1)*per
    conn = psycopg2.connect(**DB); cur = conn.cursor()
    w=[];a=[]
    if cat: w.append("category=%s");a.append(cat)
    if s: w.append("name ILIKE %s");a.append("%"+s+"%")
    wh = " WHERE "+" AND ".join(w) if w else ""
    cur.execute("SELECT count(*) FROM products"+wh,a); total=cur.fetchone()[0]
    cur.execute("SELECT id,name,category,price,COALESCE(image,''),stock FROM products"+wh+" ORDER BY id LIMIT %s OFFSET %s",a+[per,off])
    rows=cur.fetchall();conn.close()
    return jsonify({'products':[{'id':r[0],'name':r[1],'category':r[2],'price':float(r[3]),'image':r[4],'stock':r[5]} for r in rows],'total':total,'total_pages':(total+per-1)//per})

@app.route('/api/orders', methods=['GET'])
def list_orders():
    conn = psycopg2.connect(**DB); cur = conn.cursor()
    cur.execute("SELECT o.id,o.product_name,o.price,o.status,o.created_at,p.image,p.id as pid FROM orders o LEFT JOIN products p ON p.name=o.product_name ORDER BY o.id DESC LIMIT 50")
    rows=cur.fetchall();conn.close()
    return jsonify([{'id':r[0],'product_name':r[1],'price':float(r[2]),'status':r[3],'created_at':str(r[4]),'image':r[5],'pid':r[6]} for r in rows])

@app.route('/api/orders', methods=['POST'])
def create_order():
    REQUESTS.labels('/api/orders','POST').inc()
    rid = str(uuid.uuid4())[:8]
    pid = request.json['product_id']
    api_log.info("["+rid+"] order "+str(pid))
    conn = psycopg2.connect(**DB); cur = conn.cursor()
    cur.execute('SELECT name,price,stock FROM products WHERE id=%s FOR UPDATE',(pid,))
    p = cur.fetchone()
    if not p or p[2]<=0: conn.close(); return jsonify({'error':'no stock'}),400
    cur.execute('UPDATE products SET stock=stock-1 WHERE id=%s',(pid,))
    cur.execute('INSERT INTO orders (product_id,product_name,price,status) VALUES (%s,%s,%s,%s) RETURNING id',(pid,p[0],p[1],'confirmed'))
    oid=cur.fetchone()[0];conn.commit();conn.close()
    order_log.info("["+rid+"] order #"+str(oid))
    c=pika.BlockingConnection(pika.ConnectionParameters(host=MQ));ch=c.channel();ch.queue_declare(queue='orders')
    ch.basic_publish(exchange='',routing_key='orders',body='{"order_id":'+str(oid)+'}');c.close()
    return jsonify({'order_id':oid}),201

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype='text/plain; version=0.0.4')

if __name__ == '__main__':
    startup_log.info("App starting on 5000")
    app.run(host='0.0.0.0', port=5000)
