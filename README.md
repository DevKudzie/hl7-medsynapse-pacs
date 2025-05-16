# HL7 v2.3 Integration Project

This project demonstrates how to work with HL7 v2.3 messages and transmit them from a local network to a REST API endpoint on the internet.

## Project Overview

This project includes:

1. **HL7 Generator** - Creates simulated HL7 v2.3 messages with dummy patient data
2. **HL7 Sender** - Transmits HL7 messages from a local network to the internet
3. **REST Receiver** - A REST API that receives and processes HL7 messages
4. **Documentation** - Complete guide on HL7 v2.3 standard and implementation

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

## Project Setup

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
   ```

3. Set up the REST Receiver:
   ```
   cd ../rest-receiver
   npm install
   ```

## Usage

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

### Running the REST Receiver

To start the REST API receiver:

```
cd rest-receiver
npm start
```

The API will be available at `http://localhost:3000/api/hl7`

## Security Considerations

When transmitting healthcare data from a local network to the internet:

1. **Encryption**: Always use TLS/SSL (HTTPS) for data in transit
2. **Authentication**: Implement token-based authentication for API access
3. **Data Sanitization**: Remove any PHI/PII for testing and learning purposes
4. **Network Security**: Consider VPN or secure tunnel for production environments

## HL7 Message Examples

### Sample HL7 v2.3 ADT (Admission, Discharge, Transfer) Message

```
MSH|^~\&|SENDING_APP|SENDING_FACILITY|RECEIVING_APP|RECEIVING_FACILITY|20230915120000||ADT^A01|MSG00001|P|2.3
EVN|A01|20230915120000
PID|1||12345^^^MRN||DOE^JOHN^Q||19800101|M|||123 MAIN ST^^ANYTOWN^NY^12345||555-123-4567|||S||MRN12345|123-45-6789
PV1|1|I|2WEST^2021^01||||12345^SMITH^JANE^M^MD|67890^JONES^BOB^W^MD|||||||||ADM12345|||||||||||||||||||||||||20230915120000
```

## Project Structure

```
hl7-integration-project/
├── README.md
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
└── docs/
    └── hl7_standard_reference.md
```

## Resources

- [HL7 v2.3 Standard Documentation](https://www.hl7.org/implement/standards/product_brief.cfm?product_id=140)
- [RESTful API Best Practices](https://restfulapi.net/)
- [Node.js Documentation](https://nodejs.org/en/docs/)
- [Python HL7 Library Documentation](https://python-hl7.readthedocs.io/) 