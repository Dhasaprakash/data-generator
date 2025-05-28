import yaml
from faker import Faker
import json
from typing import Dict, List, Any, Optional, Tuple
import os
import ast
from datetime import datetime
from dataclasses import dataclass
from collections import defaultdict
import argparse

@dataclass
class SchemaConfig:
    file_path: str
    parent_table: Optional[str] = None
    records_per_parent: int = 1
    is_root: bool = False

class SchemaHierarchy:
    def __init__(self):
        self.schemas: Dict[str, SchemaConfig] = {}
        self.children: Dict[str, List[str]] = defaultdict(list)
        self.parent_map: Dict[str, str] = {}
        
    def add_schema(self, table_name: str, config: SchemaConfig):
        self.schemas[table_name] = config
        if config.parent_table:
            self.children[config.parent_table].append(table_name)
            self.parent_map[table_name] = config.parent_table
    
    def get_root_schemas(self) -> List[str]:
        return [name for name, config in self.schemas.items() if config.is_root]
    
    def get_children(self, table_name: str) -> List[str]:
        return self.children[table_name]
    
    def get_parent(self, table_name: str) -> Optional[str]:
        return self.parent_map.get(table_name)
    
    def get_config(self, table_name: str) -> SchemaConfig:
        return self.schemas[table_name]

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class FakeDataGenerator:
    def __init__(self, record_counts: Optional[Dict[str, int]] = None):
        self.faker = Faker()
        self.generated_data = {}
        self.schema_hierarchy = SchemaHierarchy()
        self.record_counts = record_counts or {}

    def load_schema(self, schema_file: str) -> Dict[str, Any]:
        """Load and parse the YAML schema file."""
        if not os.path.exists(schema_file):
            raise FileNotFoundError(f"Schema file not found: {schema_file}")
        
        with open(schema_file, 'r') as f:
            return yaml.safe_load(f)

    def load_manifest_directory(self, manifest_dir: str = "manifest") -> None:
        """Load all schema files from the manifest directory and build the hierarchy."""
        if not os.path.exists(manifest_dir):
            raise FileNotFoundError(f"Manifest directory not found: {manifest_dir}")

        schema_files = [f for f in os.listdir(manifest_dir) if f.endswith('.yaml')]

        for schema_file in schema_files:
            schema = self.load_schema(os.path.join(manifest_dir, schema_file))
            table_name = schema['table_name']
            parent_table = None
            records_per_parent = schema.get('records_per_parent', 1)
            
            # Override records_per_parent if provided in command line
            if table_name in self.record_counts:
                records_per_parent = self.record_counts[table_name]
            
            # Look for references to find parent-child relationships
            for field in schema['fields']:
                if 'references' in field:
                    parent_table = field['references']['table']
                    break
            
            config = SchemaConfig(
                file_path=os.path.join(manifest_dir, schema_file),
                parent_table=parent_table,
                records_per_parent=records_per_parent,
                is_root=(parent_table is None)
            )
            
            self.schema_hierarchy.add_schema(table_name, config)

    def generate_field_value(self, field: Dict[str, Any], record: Dict[str, Any]) -> Any:
        """Generate a value for a field based on its schema definition."""
        if 'faker_method' in field:
            method_spec = field['faker_method']
            
            # Handle method specifications with arguments
            if ':' in method_spec:
                method_name, args = method_spec.split(':', 1)
                
                # Handle constant values
                if method_name == 'constant':
                    return args
                
                # Handle random_element with list argument
                if method_name == 'random_element':
                    try:
                        choices = ast.literal_eval(args)
                        return self.faker.random_element(elements=choices)
                    except:
                        raise ValueError(f"Invalid choices for random_element: {args}")
                
                # Handle format with dependencies
                if method_name == 'format':
                    try:
                        return args.format(**record)
                    except KeyError as e:
                        raise ValueError(f"Missing dependent field for format: {e}")
                
                # Handle conditional field generation
                if method_name == 'conditional':
                    try:
                        condition_field, value_map = args.split(':', 1)
                        value_map = ast.literal_eval(value_map)
                        condition_value = record[condition_field]
                        faker_method = value_map[condition_value]
                        return getattr(self.faker, faker_method)()
                    except (ValueError, KeyError) as e:
                        raise ValueError(f"Error in conditional field generation: {e}")
                
                faker_method = getattr(self.faker, method_name, None)
                if faker_method is None:
                    raise ValueError(f"Unsupported faker method: {method_name}")
                
                return faker_method(args)
            else:
                faker_method = getattr(self.faker, method_spec, None)
                if faker_method is None:
                    raise ValueError(f"Unsupported faker method: {method_spec}")
                if method_spec == 'date_time':
                    return faker_method().isoformat()
                return faker_method()
        elif field['type'] == 'uuid' and not 'faker_method' in field:
            return self.faker.uuid4()
        else:
            raise ValueError(f"Field {field['name']} missing faker_method and has no default generator")

    def sort_fields_by_dependencies(self, fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort fields so that dependencies are generated before dependent fields."""
        def get_dependencies(field):
            deps = set(field.get('depends_on', []))
            if field.get('faker_method', '').startswith('conditional:'):
                condition_field = field['faker_method'].split(':', 2)[1]
                deps.add(condition_field)
            return deps

        field_deps = [(field, get_dependencies(field)) for field in fields]
        sorted_fields = []
        seen = set()

        while field_deps:
            available = [(f, d) for f, d in field_deps if d.issubset(seen)]
            if not available:
                raise ValueError("Circular dependency detected in field definitions")
            
            field, deps = available[0]
            sorted_fields.append(field)
            seen.add(field['name'])
            field_deps.remove((field, deps))

        return sorted_fields

    def generate_fake_data(self, schema: Dict[str, Any], num_records: int = 1, parent_data: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Generate fake data based on the provided schema with support for referential contexts."""
        records = []
        table_name = schema['table_name']
        
        sorted_fields = self.sort_fields_by_dependencies(schema['fields'])
        
        for i in range(num_records):
            record = {}
            for field in sorted_fields:
                field_name = field['name']
                
                if 'references' in field:
                    ref_table = field['references']['table']
                    ref_field = field['references']['field']
                    
                    if parent_data and ref_table in self.generated_data:
                        parent_index = i % len(parent_data)
                        record[field_name] = parent_data[parent_index][ref_field]
                    else:
                        raise ValueError(f"Referenced table {ref_table} not found in generated data")
                else:
                    record[field_name] = self.generate_field_value(field, record)
            
            records.append(record)
        
        self.generated_data[table_name] = records
        return records

    def generate_hierarchical_data(self, root_records: int = 1) -> Dict[str, List[Dict[str, Any]]]:
        """Generate nested hierarchical data where child records are nested within parent records."""
        def generate_for_table(table_name: str, parent_record: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
            config = self.schema_hierarchy.get_config(table_name)
            schema = self.load_schema(config.file_path)
            
            # Determine number of records to generate
            num_records = root_records if config.is_root else config.records_per_parent
            
            records = []
            for i in range(num_records):
                record = {}
                sorted_fields = self.sort_fields_by_dependencies(schema['fields'])
                
                for field in sorted_fields:
                    field_name = field['name']
                    if 'references' in field and parent_record:
                        ref_table = field['references']['table']
                        ref_field = field['references']['field']
                        record[field_name] = parent_record[ref_field]
                    else:
                        record[field_name] = self.generate_field_value(field, record)
                
                # Generate child records and nest them within this record
                for child_table in self.schema_hierarchy.get_children(table_name):
                    child_records = generate_for_table(child_table, record)
                    # Use the child table name as the key for nested records
                    record[child_table] = child_records
                
                records.append(record)
            
            return records

        nested_data = {}
        for root_table in self.schema_hierarchy.get_root_schemas():
            nested_data[root_table] = generate_for_table(root_table)

        return nested_data

    def generate_and_save(self, output_file: str, root_records: int = 1, kafka_producer=None):
        """Generate hierarchical data and save to a JSON file, optionally publish to Kafka."""
        if not self.schema_hierarchy.schemas:
            self.load_manifest_directory()

        data = self.generate_hierarchical_data(root_records)
        
        # Save to file
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, cls=DateTimeEncoder)
        
        # If Kafka producer is provided, publish each profile
        if kafka_producer:
            for profile in data['customer_profile']:
                profile_id = profile['PROFILE_ID']
                # Build the complete profile aggregate
                profile_data = {
                    **profile,
                    'contacts': [
                        contact for contact in data.get('customer_contact', [])
                        if contact['PROFILE_ID'] == profile_id
                    ],
                    'addresses': []
                }

                # Add addresses with their exceptions
                addresses = [
                    addr for addr in data.get('customer_address', [])
                    if addr['PROFILE_ID'] == profile_id
                ]
                
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

                # Publish to Kafka
                kafka_producer.publish_profile(profile_data)
        
        print(f"\nGenerated data summary:")
        for table_name, records in data.items():
            config = self.schema_hierarchy.get_config(table_name)
            parent = self.schema_hierarchy.get_parent(table_name)
            if parent:
                print(f"  {table_name}: {len(records)} records ({config.records_per_parent} per {parent} record)")
            else:
                print(f"  {table_name}: {len(records)} records (root table)")

def parse_record_count(arg: str) -> Tuple[str, int]:
    try:
        table, count = arg.split(':')
        return table, int(count)
    except ValueError:
        raise argparse.ArgumentTypeError('Record count must be in format table_name:count')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate fake data based on schema definitions')
    parser.add_argument('--root-records', type=int, default=1,
                      help='Number of root records to generate')
    parser.add_argument('--output', type=str, default='generated_data.json',
                      help='Output JSON file path')
    parser.add_argument('--record-counts', type=parse_record_count, nargs='*',
                      help='Override records per parent (format: table_name:count)')
    parser.add_argument('--kafka-bootstrap-servers', type=str,
                      help='Kafka bootstrap servers (e.g., localhost:9092). If provided, will publish to Kafka')
    
    args = parser.parse_args()
    
    # Convert record counts to dictionary
    record_counts = dict(args.record_counts) if args.record_counts else {}
    
    # Initialize generator
    generator = FakeDataGenerator(record_counts)

    # Initialize Kafka producer if bootstrap servers are provided
    kafka_producer = None
    if args.kafka_bootstrap_servers:
        from customer_profile_producer import CustomerProfileProducer
        kafka_producer = CustomerProfileProducer(bootstrap_servers=args.kafka_bootstrap_servers)

    try:
        # Generate and optionally publish data
        generator.generate_and_save(args.output, args.root_records, kafka_producer)
    finally:
        if kafka_producer:
            kafka_producer.close() 