from os import getenv
import logging

from dotenv import load_dotenv
from os.path import realpath, dirname
from kafka import KafkaConsumer
import json

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    root_dir = realpath(dirname(realpath(__file__)) + "/..")
    load_dotenv(dotenv_path=f"{root_dir}/.env")
    logging.basicConfig(level=getenv("LOGLEVEL", "INFO").upper())

    kafka_server = getenv("KAFKA_SERVER", "127.0.0.1:9092")
    kafka_consumer_group_id = getenv("KAFKA_CONSUMER_GROUP_ID", "simple-sub")

    logger.info("Using KAFKA_SERVER='%s'", kafka_server)
    kafka_consumer = KafkaConsumer(
        "detected",
        bootstrap_servers=[kafka_server],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id=kafka_consumer_group_id,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    for message in kafka_consumer:
        message = message.value
        logger.info("Read: %s", message)

