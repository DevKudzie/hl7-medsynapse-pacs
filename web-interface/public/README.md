# HL7 v2.3 Integration Project (Medsynapse PACS Simulation)

This project demonstrates how to work with HL7 v2.3 messages by simulating the Medsynapse PACS Broker as defined in its conformance statement.

## Purpose

This project serves multiple purposes:

1. **Education and Training**: Provides a realistic environment for developers and healthcare IT professionals to learn HL7 v2.3 messaging without needing access to actual healthcare systems.

2. **Integration Testing**: Offers a simulated PACS environment for testing healthcare applications that need to communicate with imaging systems, without risking patient data or production systems.

3. **Bridge Legacy and Modern**: Demonstrates practical approaches for connecting modern web applications to legacy healthcare systems that use HL7 v2.x standards.

4. **Security Implementation**: Shows how to implement proper security controls when integrating cloud applications with on-premise healthcare systems.

5. **Proof of Concept**: Enables rapid prototyping of healthcare integration solutions before implementing in production environments.

The target audience includes healthcare IT professionals, software developers working on medical applications, system integrators, and students learning about healthcare interoperability standards.

## Project Overview

This project includes:

1. **HL7 Generator** - Creates simulated HL7 v2.3 messages following Medsynapse PACS specifications
2. **HL7 Sender** - Transmits HL7 messages using MLLP (Minimal Lower Layer Protocol) over TCP/IP
3. **MLLP Server** - A TCP socket server that receives and processes HL7 messages according to Medsynapse standards
4. **REST API** - An HTTP API that provides access to received messages and system status
5. **Web Interface** - A simple web UI for testing the integration
6. **Documentation** - Complete guide on HL7 v2.3 standard and implementation

## How Medsynapse PACS Works in Healthcare

Medsynapse PACS (Picture Archiving and Communication System) is a critical healthcare IT system that handles medical imaging data. Understanding its place in the clinical workflow helps explain its integration challenges:

### Typical Clinical Workflow

1. **Order Creation**: A physician orders an imaging study in the RIS (Radiology Information System) or EMR/EHR (Electronic Medical/Health Record)
   - The RIS sends an `ORM^O01` (Order) message to the Medsynapse PACS Broker
   - The order contains patient demographics, study details, and scheduling information

2. **Modality Worklist**: An imaging device (CT scanner, MRI, etc.) queries the PACS Broker for scheduled procedures
   - This happens using DICOM protocol (not HL7)
   - The PACS Broker has converted the HL7 order data into DICOM format

3. **Image Acquisition**: The technologist performs the imaging procedure
   - Patient information is pulled from the worklist (no manual entry needed)
   - Images are generated and sent to the PACS storage system

4. **Reading & Reporting**: A radiologist reads the study and creates a report
   - The report is stored in the PACS or RIS
   - The PACS sends an `ORU^R01` (Results) message to the RIS, or
   - The RIS sends an `ORU^R01` message to the PACS (depending on where reporting happens)

5. **Patient Updates**: When patient demographics change in the RIS
   - `ADT^A08` (Patient Information Update) messages are sent to keep systems synchronized
   - `ADT^A40` (Patient Merge) messages handle duplicate patient records

### Medsynapse PACS Architecture

The Medsynapse PACS Broker serves as a communication gateway between different healthcare systems:

```
                  HL7 via MLLP                      DICOM
┌──────────┐                    ┌───────────────┐             ┌─────────────┐
│   RIS    │◄──── ORU ─────────┤               │             │  Imaging    │
│   or     │                    │  Medsynapse   │◄──Query────┤  Modality   │
│   EHR    │───── ORM/ADT ─────►│  PACS Broker  │───Results──►│  (CT/MRI)   │
└──────────┘     over TCP/IP    └───────────────┘  over TCP/IP└─────────────┘
                                      │   ▲
                                      │   │
                                      ▼   │
                                ┌─────────────────┐
                                │     PACS        │
                                │   Storage and   │
                                │   Workstations  │
                                └─────────────────┘
```

The Broker's primary roles are:
- Protocol translation between HL7 and DICOM
- Data mapping between different field formats
- Maintaining a database of orders, patients, and studies
- Providing worklists to modalities
- Sending status updates and results between systems

## Integrating Modern RESTful Applications with Medsynapse PACS

### The Integration Challenge

Modern applications typically use JSON over HTTP (RESTful APIs), but healthcare systems like Medsynapse PACS use HL7 over MLLP (TCP/IP sockets). This creates several challenges:

1. **Protocol Mismatch**: REST uses HTTP, while HL7 uses TCP sockets with MLLP framing
2. **Data Format**: JSON vs. pipe-delimited text with specific segment structure
3. **Connection Management**: REST is stateless, while MLLP connections persist
4. **Character Encoding**: JSON handles Unicode easily, while HL7 requires special character escaping
5. **Event Model**: REST is request/response, while HL7 can be event-driven

### Integration Approaches

This project demonstrates three main approaches to integrate with Medsynapse PACS:

#### 1. Direct MLLP Integration (Traditional)

Your modern application connects directly to the MLLP socket and speaks native HL7:

```
┌──────────────┐    HL7 over MLLP    ┌─────────────┐
│ Your Modern  │───────────────────►│ Medsynapse  │
│ Application  │◄───────────────────│ PACS Broker │
└──────────────┘    TCP/IP socket    └─────────────┘
```

**Implementation:**
```python
# This is what the send_hl7.py script does
socket = create_socket(host, port)
socket.write(mllp_start + hl7_message + mllp_end)
ack = socket.read()  # Wait for acknowledgment
socket.close()
```

#### 2. API Gateway Approach (Recommended)

Create a translation layer between your modern app and the legacy system:

```
┌──────────────┐    JSON over HTTP    ┌──────────────┐    HL7 over MLLP    ┌─────────────┐
│ Your Modern  │──────────────────►│   This       │◄──────────────────│ Medsynapse  │
│ Application  │◄──────────────────│   Project    │                     │ PACS Broker │
└──────────────┘    REST API         └──────────────┘    TCP/IP socket    └─────────────┘
```

**Implementation:**
```javascript
// Your modern app
fetch('/api/orders', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    patientId: '12345',
    study: 'CT CHEST',
    priority: 'ROUTINE'
  })
});

// API Gateway (this project)
// 1. Receives REST request
// 2. Converts JSON to HL7
// 3. Sends HL7 via MLLP socket
// 4. Waits for ACK
// 5. Returns REST response
```

#### 3. Hybrid Streaming Approach

For real-time applications requiring event streams:

```
┌──────────────┐    WebSocket     ┌──────────────┐    HL7 over MLLP    ┌─────────────┐
│ Your Modern  │◄───────────────►│   This       │◄───────────────────►│ Medsynapse  │
│ Application  │    (events)      │   Project    │                     │ PACS Broker │
└──────────────┘                  └──────────────┘                     └─────────────┘
      │                                  ▲
      │                                  │
      └─────────────── REST ────────────┘
                     (commands)
```

### Cloud to On-Premise Integration

Connecting a cloud-based application (e.g., mydoctorapp.com) to an on-premise Medsynapse PACS requires special consideration for network security. Here's a recommended approach:

```
┌────────────────┐                   ┌─────────────────┐                  ┌──────────────┐
│                │    HTTPS/TLS      │  API Gateway    │    HL7/MLLP      │ Medsynapse   │
│ mydoctorapp.com│ ----------------> │  (On-Premise)   │ ---------------> │ PACS Broker  │
│                │    (REST/JSON)    │                 │    (TCP/IP)      │              │
└────────────────┘                   └─────────────────┘                  └──────────────┘
         ^                                   |
         |                                   |
         └───────────────────────────────────┘
                     Secure Connection
                (VPN, Reverse Proxy, etc.)
```

#### Implementation Steps:

1. **Deploy API Gateway On-Premise**: Install the rest-receiver component on a server within the healthcare network
2. **Establish Secure Connectivity**: Choose one of these approaches:
   - **VPN Solution**: Create a secure tunnel between cloud and healthcare network
   - **Reverse Proxy with TLS**: Use NGINX or similar with strong TLS encryption
   - **Site-to-Site Connection**: Leverage services like Azure ExpressRoute or AWS Direct Connect
3. **Implement Network Security Controls**:
   - Firewall rules allowing only specific traffic
   - Network segmentation to isolate healthcare systems
   - Intrusion detection/prevention systems

#### Security Best Practices:

- **Never expose MLLP ports (2575) directly to the internet**
- **Use TLS 1.2+ for all external connections**
- **Implement strong authentication (API keys, OAuth, etc.)**
- **Limit API gateway access to specific IP ranges**
- **Encrypt all PHI/PII in transit and at rest**
- **Maintain audit logs of all access attempts**
- **Keep all components updated with security patches**

#### Example Client Implementation:

```javascript
// Modern web app code to fetch PACS data securely
async function fetchPatientStudies(patientId) {
  const response = await fetch('https://gateway.healthcare.org/api/hl7/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': process.env.SECURE_API_KEY
    },
    body: JSON.stringify({
      queryType: 'patient_studies',
      patientId: patientId
    })
  });
  
  return await response.json();
}
```

### Data Translation Examples

#### From JSON to HL7

**REST API Request (JSON):**
```json
{
  "order": {
    "accessionNumber": "ACC123456",
    "patient": {
      "id": "PAT789",
      "name": "SMITH, JOHN",
      "gender": "M",
      "dateOfBirth": "19800101"
    },
    "study": {
      "modality": "CT",
      "description": "CT CHEST",
      "priority": "ROUTINE"
    },
    "scheduling": {
      "aeTitle": "CT1",
      "scheduledDateTime": "20230614132030"
    }
  }
}
```

**Translated to HL7 ORM^O01:**
```
MSH|^~\&|API_GATEWAY|FACILITY|PACS_APP|PACS_FACILITY|20230614131415||ORM^O01|MSG123|P|2.3
PID|1||PAT789||SMITH^JOHN||19800101|M
PV1|1|O
ORC|NW
OBR|1|ACC123456||CT123^CT CHEST|ROUTINE||||||||||CT CHEST|||CT1||||CT|||||||||||20230614132030
```

#### From HL7 to JSON

**HL7 ORU^R01 Message:**
```
MSH|^~\&|PACS_APP|PACS_FACILITY|API_GATEWAY|FACILITY|20230614151617||ORU^R01|ACK123|P|2.3
PID|1||PAT789||SMITH^JOHN||19800101|M
OBR|1|ACC123456||CT123^CT CHEST
OBX||TX|CT123^CT CHEST||Normal study with no significant findings.\X0D\\X0A\Lungs are clear.||||||F
```

**Translated to JSON:**
```json
{
  "report": {
    "accessionNumber": "ACC123456",
    "patient": {
      "id": "PAT789",
      "name": {
        "family": "SMITH",
        "given": "JOHN"
      }
    },
    "study": {
      "id": "CT123",
      "description": "CT CHEST"
    },
    "result": {
      "status": "FINAL",
      "content": "Normal study with no significant findings.\nLungs are clear."
    }
  }
}
```

## Field Mapping Guide

When integrating with Medsynapse PACS, you must map your application fields to specific HL7 segments and positions. Here's a practical guide for the most common data elements:

### Patient Demographics
| Your App Field    | HL7 Location      | Example Value    |
|-------------------|-------------------|------------------|
| Patient ID        | PID-3-1           | 12345            |
| Last Name         | PID-5-1           | SMITH            |
| First Name        | PID-5-2           | JOHN             |
| Date of Birth     | PID-7             | 19800101         |
| Gender            | PID-8             | M                |
| Admission ID      | PID-18            | ADM98765         |

### Order Information
| Your App Field    | HL7 Location      | Example Value    |
|-------------------|-------------------|------------------|
| Accession Number  | OBR-2-1           | ACC.12345        |
| Procedure ID      | OBR-4-1           | CT1234           |
| Procedure Name    | OBR-4-2           | CT CHEST         |
| Priority          | OBR-5-1           | ROUTINE          |
| Modality          | OBR-24-1          | CT               |
| Order Status      | ORC-1             | NW (new)         |

### Scheduling Information 
| Your App Field    | HL7 Location      | Example Value    |
|-------------------|-------------------|------------------|
| AE Title          | OBR-21-1          | CTSCANNER        |
| Station Name      | OBR-18-1          | CT_ROOM1         |
| Start DateTime    | OBR-36-1          | 20230614132030   |
| Location          | OBR-20-1          | RADIOLOGY        |

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

To generate sample HL7 v2.3 messages following Medsynapse format:

```
cd hl7-sender
python generate_hl7.py --count 5 --output sample_messages.txt --types all
```

Available message types: `orm`, `oru`, `adt_a08`, `adt_a40`, `all`

### Sending HL7 Messages via MLLP

To send HL7 messages to the MLLP server:

```
cd hl7-sender
python send_hl7.py --input sample_messages.txt --host localhost --port 2575
```

### Sending HL7 Messages via REST API

The REST API can also receive HL7 messages (for backward compatibility):

```
cd hl7-sender
python send_hl7.py --input sample_messages.txt --http --endpoint http://localhost:3000/api/hl7
```

### Using the Web Interface

The web interface allows you to:
1. Generate sample HL7 messages
2. Send messages to the MLLP server or REST API
3. View received messages and their details

Access the web interface at: http://localhost:5000

## Troubleshooting

### MLLP Connection Issues

If you're having trouble connecting to the MLLP server:

1. Ensure port 2575 is not already in use
2. Check firewall settings for TCP socket connections
3. Verify message format includes proper MLLP framing (VT at start, FS+CR at end)

### Authentication Issues

If you encounter "Unauthorized: Invalid API key" errors:

1. Verify that both services are using the same API key
2. Check that the web interface is including the `x-api-key` header in requests
3. Make sure environment variables are correctly loaded

### Docker Issues

If running into issues with Docker:

1. Make sure Docker and Docker Compose are properly installed
2. Check that no services are already running on ports 3000, 5000, and 2575
3. Review Docker logs for specific error messages

## Resources

- [HL7 v2.3 Standard Documentation](https://www.hl7.org/implement/standards/product_brief.cfm?product_id=140)
- [MLLP Specification](https://www.hl7.org/documentcenter/public/wg/inm/mllp_transport_specification.PDF)
- [Medsynapse HL7 Conformance Statement](docs/Medsynapse%20HL7%20Conformance%20Statement.txt) 