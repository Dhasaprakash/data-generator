import json
from kafka import KafkaProducer
from fake_data_generator import FakeDataGenerator
import argparse

class KafkaProfilePublisher:
    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
            key_serializer=str.encode
        )
        self.topic = 'customer-profiles'

    def transform_data(self, data: dict) -> dict:
        """Transform the generated data to match our Kafka message structure"""
        result = {}
        for table_name, records in data.items():
            if table_name == 'customer_profile':
                # Process each customer profile
                for profile in records:
                    profile_id = profile['PROFILE_ID']
                    # Find related records for this profile
                    profile_data = {
                        **profile,
                        'contacts': [
                            contact for contact in data.get('customer_contact', [])
                            if contact['PROFILE_ID'] == profile_id
                        ],
                        'addresses': []
                    }

                    # Find addresses and their exceptions
                    addresses = [
                        addr for addr in data.get('customer_address', [])
                        if addr['PROFILE_ID'] == profile_id
                    ]

                    # Add exceptions to each address
                    for addr in addresses:
                        addr_exceptions = [
                            exc for exc in data.get('customer_address_exception', [])
                            if exc['PROFILE_ID'] == profile_id and exc['ADDRESS_TYPE'] == addr['ADDRESS_TYPE']
                        ]
                        addr['exceptions'] = addr_exceptions
                        profile_data['addresses'].append(addr)

                    # Add CDD data
                    cdd_data = next(
                        (cdd for cdd in data.get('customer_cdd', [])
                         if cdd['PROFILE_ID'] == profile_id),
                        None
                    )
                    if cdd_data:
                        profile_data['dueDiligence'] = cdd_data

                    result[profile_id] = profile_data

        return result

    def publish_profiles(self, data: dict) -> None:
        """Publish the transformed profile data to Kafka"""
        transformed_data = self.transform_data(data)
        
        for profile_id, profile in transformed_data.items():
            try:
                future = self.producer.send(
                    self.topic,
                    key=profile_id,
                    value=profile
                )
                # Wait for the message to be delivered
                record_metadata = future.get(timeout=10)
                print(f"Successfully published profile {profile_id} to topic {record_metadata.topic}")
            except Exception as e:
                print(f"Error publishing profile {profile_id}: {str(e)}")

    def close(self) -> None:
        self.producer.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate and publish customer profile events to Kafka')
    parser.add_argument('--bootstrap-servers', default='localhost:9092', help='Kafka bootstrap servers')
    parser.add_argument('--manifest-dir', default='manifest', help='Directory containing schema files')
    parser.add_argument('--root-records', type=int, default=10, help='Number of root records to generate')
    args = parser.parse_args()

    # Generate fake data using existing generator
    generator = FakeDataGenerator()
    generator.load_manifest_directory(args.manifest_dir)
    data = generator.generate_hierarchical_data(args.root_records)

    # Publish to Kafka
    publisher = KafkaProfilePublisher(bootstrap_servers=args.bootstrap_servers)
    try:
        publisher.publish_profiles(data)
    finally:
        publisher.close() 