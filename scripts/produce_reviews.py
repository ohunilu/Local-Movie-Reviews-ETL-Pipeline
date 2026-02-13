from kafka import KafkaProducer
import json
import time
import random

producer = KafkaProducer(bootstrap_servers='kafka:9092',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

movies = ["Anikulapo", "The Wedding Party", "King of Boys", "Ayinla", "Jagun Jagun", "Swallow","The Bling Lagosians","The Black Book","Blood Sisters","The Set Up"]
for i in range(50):
    review = {
        "movie": random.choice(movies),
        "rating": random.randint(1,10),
        "text": f"Review {i} - {'great' if random.random()>0.5 else 'bad'}",
        "timestamp": time.time()
    }
    producer.send('movie-reviews', value=review)
    print(f"Sent: {review}")
    time.sleep(0.5)
    
producer.flush()