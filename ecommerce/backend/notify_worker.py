import pika, json, time
from logging_config import setup_logger

startup_log = setup_logger('startup')
notify_log  = setup_logger('notify')

def callback(ch, method, properties, body):
    rid = 'NO-RID'
    try:
        msg = json.loads(body)
        rid = msg.get('request_id', 'NO-RID')
        order_id = msg.get('order_id', '?')
        product = msg.get('product', '?')
        price = msg.get('price', 0)

        notify_log.info(f"[{rid}] received order #{order_id} | product={product} | EUR {price}")
        time.sleep(1)
        notify_log.info(f"[{rid}] order #{order_id} | email SENT | customer notified")
        notify_log.info(f"[{rid}] order #{order_id} | pipeline complete | elapsed=1s")

    except Exception as e:
        notify_log.error(f"[{rid}] FAILED | error={e} | body={body[:200]}")

startup_log.info("=" * 50)
startup_log.info("Notify worker starting...")
startup_log.info("Connecting to RabbitMQ...")
try:
    conn = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    startup_log.info("RabbitMQ connected OK")
    ch = conn.channel()
    ch.queue_declare(queue='orders')
    ch.basic_consume(queue='orders', on_message_callback=callback, auto_ack=True)
    startup_log.info("Waiting for messages on queue=orders")
    ch.start_consuming()
except Exception as e:
    startup_log.critical(f"RabbitMQ connection FAILED: {e}")
