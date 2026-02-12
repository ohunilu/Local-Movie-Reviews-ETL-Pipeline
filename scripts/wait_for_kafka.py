import socket
import time
import sys

def wait_for_kafka():
    print("Waiting for Kafka...")
    for _ in range(60):
        try:
            with socket.create_connection(("kafka", 9092), timeout=5):
                print("Kafka ready!")
                return
        except (OSError, socket.error):
            time.sleep(5)
    
    print("Timeout waiting for Kafka")
    sys.exit(1)

if __name__ == "__main__":
    wait_for_kafka()
