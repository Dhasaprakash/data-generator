import json
from kafka import KafkaProducer
from typing import Dict, Any

class CustomerProfileProducer:
    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
            key_serializer=str.encode
        )
        self.topic = 'customer-profiles'

    def publish_profile(self, profile_data: Dict[str, Any]) -> None:
        """
        Publish a single customer profile with its related data to Kafka.
        profile_data should contain the complete customer profile aggregate including
        contacts, addresses (with exceptions), and CDD data.
        """
        try:
            profile_id = profile_data.get('PROFILE_ID')
            if not profile_id:
                raise ValueError("Profile data must contain PROFILE_ID")

            future = self.producer.send(
                self.topic,
                key=profile_id,
                value=profile_data
            )
            # Wait for the message to be delivered
            record_metadata = future.get(timeout=10)
            print(f"Successfully published profile {profile_id} to topic {record_metadata.topic}")
        except Exception as e:
            print(f"Error publishing profile: {str(e)}")

    def close(self) -> None:
        self.producer.close() 