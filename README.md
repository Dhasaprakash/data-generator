# Customer Profile Data Pipeline

This project consists of two main components:
1. A Spring Boot application that consumes customer profile data from Kafka and persists it in PostgreSQL
2. A Python utility for generating test data and interacting with the system

## Prerequisites

- Docker and Docker Compose
- Java 17 or higher
- Maven 3.9 or higher
- Python 3.8 or higher
- pip (Python package installer)

## Technology Stack

- Spring Boot
- Apache Kafka
- PostgreSQL
- Docker
- JPA/Hibernate
- Python 3.8+

## Project Structure

```
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/
│   │   │       └── example/
│   │   │           ├── model/
│   │   │           │   ├── CustomerProfile.java
│   │   │           │   ├── CustomerAddress.java
│   │   │           │   ├── CustomerContact.java
│   │   │           │   ├── CustomerDueDiligence.java
│   │   │           │   └── CustomerAddressException.java
│   │   │           ├── service/
│   │   │           │   └── CustomerProfileConsumer.java
│   │   │           └── CustomerProfileApplication.java
│   │   └── resources/
│   │       └── application.properties
├── python/
│   ├── requirements.txt
│   ├── data_generator.py
│   └── kafka_utils.py
├── docker-compose.yml
├── Dockerfile
└── pom.xml
```

## Setup and Running

### Spring Boot Application

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. Build the application:
   ```bash
   ./mvnw clean package -DskipTests
   ```

3. Start the services using Docker Compose:
   ```bash
   docker compose up -d
   ```

This will start:
- Zookeeper (port 2181)
- Kafka (port 9092)
- PostgreSQL (port 5432)
- Spring Boot application (port 8080)

### Python Setup

1. Create and activate a virtual environment:

   ```bash
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r python/requirements.txt
   ```

3. Run the data generator:
   ```bash
   # Generate and send test data
   python python/data_generator.py --count 10

   # Generate data with specific profile types
   python python/data_generator.py --count 5 --profile-type INDIVIDUAL

   # Save generated data to file
   python python/data_generator.py --count 3 --output data.json

   # Send existing JSON file to Kafka
   python python/kafka_utils.py --file data.json
   ```

### Python Script Options

#### data_generator.py
```bash
Options:
  --count INTEGER          Number of profiles to generate [default: 1]
  --profile-type TEXT      Profile type (INDIVIDUAL/CORPORATE) [default: INDIVIDUAL]
  --output TEXT           Output file path [optional]
  --send-to-kafka BOOLEAN Send to Kafka directly [default: True]
  --help                  Show this message and exit.
```

#### kafka_utils.py
```bash
Options:
  --file TEXT            JSON file containing profiles to send [required]
  --topic TEXT           Kafka topic name [default: customer-profiles]
  --bootstrap-servers TEXT Kafka bootstrap servers [default: localhost:9092]
  --help                 Show this message and exit.
```

## Testing the Application

1. Create a test message (example provided in `test-message.json`):
```json
{
  "profileId": "PROF001",
  "tenantId": "TENANT001",
  "profileType": "I",
  "profileStatus": "ACTIVE",
  "firstName": "John",
  "lastName": "Doe",
  ...
}
```

2. Send a message to Kafka:
```bash
docker compose exec kafka kafka-console-producer --broker-list localhost:9092 --topic customer-profiles < test-message.json
```

3. Monitor the application logs:
```bash
docker compose logs -f app
```

## Configuration

### Kafka Configuration
- Bootstrap Servers: kafka:9092
- Consumer Group: customer-profile-group
- Topic: customer-profiles

### PostgreSQL Configuration
- Host: postgres
- Port: 5432
- Database: customerdb
- Username: postgres
- Password: postgres

## Data Model

### CustomerProfile
- Basic customer information (ID, name, status)
- One-to-many relationships with:
  - Addresses
  - Contacts
  - Due Diligence records

### CustomerAddress
- Address details
- One-to-many relationship with address exceptions

### CustomerContact
- Contact information (phone, email, etc.)
- Contact preferences and status

### CustomerDueDiligence
- KYC information
- Risk assessment
- Income and occupation details

## Debugging Commands

### Docker Container Management
```bash
# Stop all containers and remove volumes
docker compose down -v

# Restart all services
docker compose down && docker compose up -d

# Check container status
docker compose ps

# View logs of specific service
docker compose logs kafka    # Kafka logs
docker compose logs postgres # PostgreSQL logs
docker compose logs app      # Application logs

# Follow logs in real-time
docker compose logs -f app
```

### Kafka Commands
```bash
# List Kafka topics
docker compose exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Create Kafka topic
docker compose exec kafka kafka-topics --create --topic customer-profiles --partitions 1 --replication-factor 1 --bootstrap-server localhost:9092

# Describe Kafka topic
docker compose exec kafka kafka-topics --describe --topic customer-profiles --bootstrap-server localhost:9092

# Consume messages from topic
docker compose exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic customer-profiles --from-beginning

# Produce test message to topic
docker compose exec kafka kafka-console-producer --broker-list localhost:9092 --topic customer-profiles < test-message.json

# Check if topic exists
docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --topic customer-profiles --describe 2>/dev/null || echo "Topic does not exist"

# Alternative way to check topic existence
docker compose exec kafka kafka-topics --list --bootstrap-server localhost:9092 | grep -w "customer-profiles"

# Get detailed topic information
docker compose exec kafka kafka-topics --describe --bootstrap-server localhost:9092 --topic customer-profiles

# Check topic partition count and replication
docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --describe --topic customer-profiles | grep "PartitionCount"

# List all topics and their details
docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --describe --list

# Create topic if it doesn't exist
docker compose exec kafka kafka-topics --create --if-not-exists --topic customer-profiles --partitions 1 --replication-factor 1 --bootstrap-server localhost:9092

# Check topic configuration
docker compose exec kafka kafka-configs --bootstrap-server localhost:9092 --entity-type topics --entity-name customer-profiles --describe

# Check topic lag
docker compose exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group customer-profile-group | grep customer-profiles

# List active consumers for the topic
docker compose exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group customer-profile-group

# Test topic by producing and consuming a message
echo "test message" | docker compose exec -T kafka kafka-console-producer --broker-list localhost:9092 --topic customer-profiles
docker compose exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic customer-profiles --from-beginning --max-messages 1
```

### PostgreSQL Commands
```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U postgres -d customerdb

# Useful PostgreSQL queries
\dt                                           # List tables
\d customer_profile                           # Describe table
SELECT * FROM customer_profile;               # View all profiles
SELECT * FROM customer_address;               # View all addresses
SELECT * FROM customer_contact;               # View all contacts
SELECT * FROM customer_due_diligence;         # View all due diligence records
SELECT * FROM customer_address_exception;      # View all address exceptions
```

### Application Debugging
```bash
# View application startup
docker compose logs app | grep "Started CustomerProfileApplication"

# Check Kafka consumer group
docker compose exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group customer-profile-group

# Monitor consumer lag
docker compose exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group customer-profile-group | grep customer-profiles
```

### Network and Port Debugging
```bash
# Check if ports are in use
lsof -i :9092    # Check Kafka port
lsof -i :5432    # Check PostgreSQL port
lsof -i :2181    # Check Zookeeper port
lsof -i :8080    # Check Spring Boot application port

# Test port connectivity using netcat
nc -zv localhost 9092    # Test Kafka connectivity
nc -zv localhost 5432    # Test PostgreSQL connectivity
nc -zv localhost 2181    # Test Zookeeper connectivity
nc -zv localhost 8080    # Test Spring Boot app connectivity

# List all listening ports
netstat -tulpn | grep LISTEN    # Linux
lsof -nP -iTCP -sTCP:LISTEN    # macOS

# Check Docker network
docker network ls                                    # List networks
docker network inspect fake-data-generator_default   # Inspect network details
docker compose ps --format json                      # View container ports in JSON format

# Get container IP addresses
docker inspect -f '{{.Name}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker compose ps -q)

# Test inter-container connectivity
docker compose exec kafka ping postgres -c 2         # Test Kafka to PostgreSQL
docker compose exec app ping kafka -c 2             # Test App to Kafka
docker compose exec app ping postgres -c 2          # Test App to PostgreSQL
```

### Process Management
```bash
# Check Java processes
jps -l                          # List Java processes
ps aux | grep java             # List Java processes (alternative)

# Check process listening on ports
sudo lsof -PiTCP -sTCP:LISTEN  # All TCP listeners
sudo ss -tulpn                 # Alternative for Linux

# Memory usage
docker stats                    # Container resource usage
ps aux | grep java            # Java process memory usage
```

### System Resource Monitoring
```bash
# Container resource usage
docker stats $(docker compose ps -q)

# Disk space
df -h                          # Check disk space
docker system df               # Check Docker disk usage

# Memory
free -h                        # Check system memory
vmstat 1                       # Virtual memory statistics
```

### Log Analysis
```bash
# Search for errors in logs
docker compose logs | grep -i error
docker compose logs | grep -i exception
docker compose logs app | grep -i "failed to"

# Follow specific error types
docker compose logs -f app | grep -i "kafka"
docker compose logs -f app | grep -i "postgres"
docker compose logs -f app | grep -i "connection"

# Save logs to file for analysis
docker compose logs > application_logs.txt
docker compose logs app > spring_app_logs.txt
```

### Database Connection Testing
```bash
# Test PostgreSQL connection from host
psql -h localhost -p 5432 -U postgres -d customerdb -c "\l"

# Test from within container
docker compose exec postgres psql -U postgres -d customerdb -c "\l"

# Check PostgreSQL logs for connection issues
docker compose logs postgres | grep -i "connection"
docker compose logs postgres | grep -i "auth"
```

### Kafka Connection Testing
```bash
# Test Kafka broker connectivity
docker compose exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092

# List consumer groups and their status
docker compose exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --list
docker compose exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --describe --all-groups

# Check topic configuration
docker compose exec kafka kafka-configs --bootstrap-server localhost:9092 --entity-type topics --entity-name customer-profiles --describe

# Test producer connectivity
echo "test" | docker compose exec -T kafka kafka-console-producer --broker-list localhost:9092 --topic customer-profiles
```

## Stopping the Application

To stop all services:
```bash
docker compose down
```

To stop and remove all data (including volumes):
```bash
docker compose down -v
```

## Troubleshooting

1. If Kafka is not accessible:
   - Check if Kafka container is running: `docker compose ps`
   - Verify Kafka logs: `docker compose logs kafka`
   - Ensure topic exists: `docker compose exec kafka kafka-topics --list --bootstrap-server localhost:9092`

2. If PostgreSQL connection fails:
   - Check if PostgreSQL container is running: `docker compose ps`
   - Verify PostgreSQL logs: `docker compose logs postgres`
   - Test database connection: `docker compose exec postgres psql -U postgres -d customerdb -c "\l"`

3. If the application fails to start:
   - Check application logs: `docker compose logs app`
   - Verify all required environment variables are set in docker-compose.yml
   - Check for Java exceptions: `docker compose logs app | grep "Exception"` 