import os
import time
import logging
import requests
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TFNSW_API_KEY")
API_URL = os.getenv(
    "TFNSW_API_URL", "https://api.transport.nsw.gov.au/v1/gtfs/vehiclepos"
)
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "bus_positions")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "10"))

logging.basicConfig(level=logging.INFO)

if not API_KEY:
    raise RuntimeError("TFNSW_API_KEY not set")

producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)

headers = {"Authorization": f"apikey {API_KEY}"}

while True:
    try:
        resp = requests.get(API_URL, headers=headers, timeout=30)
        resp.raise_for_status()
        producer.send(TOPIC, resp.content)
        logging.info("Published batch %d bytes", len(resp.content))
    except Exception as exc:
        logging.error("Error fetching or publishing: %s", exc)
    time.sleep(POLL_INTERVAL)
