import json

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_apscheduler import APScheduler
from os import getenv
import secrets
import logging

from time import sleep

from dotenv import load_dotenv
from os.path import realpath, dirname
import socket
from datetime import datetime
from kafka import KafkaProducer

logger = logging.getLogger(__name__)
root_dir = realpath(dirname(realpath(__file__)) + "/..")
load_dotenv(dotenv_path=f"{root_dir}/.env")
logging.basicConfig(level=getenv("LOGLEVEL", "INFO").upper())

app = Flask(__name__)

scheduler = BackgroundScheduler()
flask_scheduler = APScheduler(scheduler)
flask_scheduler.init_app(app)
logger.info("")

run_port = getenv("RUN_PORT", 80)
run_host = getenv("RUN_HOST", "0.0.0.0")
is_run_debug = getenv('FLASK_DEBUG', "false").lower() in ['true', '1', 't', 'y', 'yes']

kafka_server = getenv("KAFKA_SERVER", "127.0.0.1:9092")
logger.info("Using KAFKA_SERVER='%s'", kafka_server)
kafka_producer = KafkaProducer(
    bootstrap_servers=[kafka_server],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)
hostname = socket.gethostname()


def get_ms_time():
    # microsecond
    return datetime.now().microsecond


@app.get("/")
def home():
    return f"Hello World! Its '{get_ms_time()}' and I am host:'{hostname}'"


def detect():
    # Bias towards 0
    detection_options = [0] + [0] + list(range(0, 8))

    # ===Random numbers like an AI detection===
    # fmt: off
    detections = {
        "car": secrets.choice(detection_options),
        "person": secrets.choice(detection_options),
        "cat": secrets.choice(detection_options),
        "dog": secrets.choice(detection_options)
    }
    # fmt: on

    return detections


def send_detections():
    logger.info("")
    logger.info("send_detections: Starting")

    detections = detect()
    message = {
        "version": "1",
        "detections": detections,
        "host": hostname,
        "at": get_ms_time()
    }
    logger.info("send_detections: Sending detected= '%s'", message)
    kafka_producer.send("detected", value=message)

    sleep_for = secrets.choice(list(range(0, 3)))
    logger.info("send_detections: Sleeping for '%s'", sleep_for)
    sleep(sleep_for)
    logger.info("send_detections: Complete")

    logger.info("")


scheduler.add_job(send_detections, 'interval', seconds=1, max_instances=1)
flask_scheduler.start()

if __name__ == '__main__':
    app.run(debug=is_run_debug, host=run_host, port=run_port)
