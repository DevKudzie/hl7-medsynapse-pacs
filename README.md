# HL7 v2.3 Integration Project

This project demonstrates how to work with HL7 v2.3 messages and transmit them from a local network to a REST API endpoint on the internet.

## Project Overview

This project includes:

1. **HL7 Generator** - Creates simulated HL7 v2.3 messages with dummy patient data
2. **HL7 Sender** - Transmits HL7 messages from a local network to the internet
3. **REST Receiver** - A REST API that receives and processes HL7 messages
4. **Web Interface** - A simple web UI for testing the integration
5. **Documentation** - Complete guide on HL7 v2.3 standard and implementation

## HL7 v2.3 Standard Overview

HL7 (Health Level Seven) v2.3 is a messaging standard for exchanging clinical and administrative data between healthcare systems. Key points:

- **Message Structure**: Messages consist of segments (like PID, MSH) separated by carriage returns
- **Segment Structure**: Each segment contains fields separated by the pipe (|) character
- **Field Structure**: Fields can contain components separated by carets (^)
- **Common Segments**:
  - MSH: Message Header - Contains metadata about the message
  - PID: Patient Identification - Contains patient demographic information
  - PV1: Patient Visit - Contains visit/encounter information
  - OBR: Observation Request - Contains information about orders
  - OBX: Observation Result - Contains results of observations/tests

## Quick Start with Docker

The easiest way to run this project is using Docker:

```
docker-compose up --build
```

This will start:
- HL7 REST receiver service on port 3000
- Web interface on port 5000

You can access the web interface at http://localhost:5000

## Manual Setup

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/hl7-integration-project.git
   cd hl7-integration-project
   ```

2. Set up the HL7 Generator and Sender:
   ```
   cd hl7-sender
   pip install -r requirements.txt
   cp env.example .env
   ```

3. Set up the REST Receiver:
   ```
   cd ../rest-receiver
   npm install
   cp env.example .env
   ```

4. Set up the Web Interface:
   ```
   cd ../web-interface
   npm install
   ```

## Usage

### Running All Services

To run all services at once (for Windows PowerShell):

```
Start-Process -NoNewWindow npm -ArgumentList "start", "--prefix", ".\rest-receiver"
Start-Process -NoNewWindow npm -ArgumentList "start", "--prefix", ".\web-interface"
```

For Linux/Mac:
```
npm start --prefix ./rest-receiver & npm start --prefix ./web-interface
```

### Generating HL7 Messages

To generate sample HL7 v2.3 messages:

```
cd hl7-sender
python generate_hl7.py --count 10 --output sample_messages.txt
```

### Sending HL7 Messages

To send HL7 messages to the REST API:

```
cd hl7-sender
python send_hl7.py --input sample_messages.txt --endpoint http://localhost:3000/api/hl7
```

### Using the Web Interface

The web interface allows you to:
1. Generate sample HL7 messages
2. Send messages to the REST API
3. View received messages and their details

Access the web interface at: http://localhost:5000

## Security Considerations

When transmitting healthcare data from a local network to the internet:

1. **Encryption**: Always use TLS/SSL (HTTPS) for data in transit
2. **Authentication**: Implement token-based authentication for API access
3. **Data Sanitization**: Remove any PHI/PII for testing and learning purposes
4. **Network Security**: Consider VPN or secure tunnel for production environments

## Project Structure

```
hl7-integration-project/
├── README.md
├── Dockerfile
├── docker-compose.yml
├── start.sh
├── hl7-sender/
│   ├── requirements.txt
│   ├── generate_hl7.py
│   ├── send_hl7.py
│   └── sample_data/
│       └── templates.py
├── rest-receiver/
│   ├── package.json
│   ├── server.js
│   └── src/
│       ├── routes/
│       │   └── hl7Routes.js
│       ├── controllers/
│       │   └── hl7Controller.js
│       └── utils/
│           └── hl7Parser.js
├── web-interface/
│   ├── package.json
│   ├── server.js
│   └── public/
│       └── index.html
└── docs/
    └── hl7_standard_reference.md
```

## Resources

- [HL7 v2.3 Standard Documentation](https://www.hl7.org/implement/standards/product_brief.cfm?product_id=140)
- [RESTful API Best Practices](https://restfulapi.net/)
- [Node.js Documentation](https://nodejs.org/en/docs/)
- [Python HL7 Library Documentation](https://python-hl7.readthedocs.io/) 