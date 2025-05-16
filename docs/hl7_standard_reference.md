# HL7 v2.3 Standard Reference Guide

This document provides a comprehensive reference for understanding and working with HL7 v2.3 messages.

## HL7 Overview

HL7 (Health Level Seven) is a set of international standards for the exchange, integration, sharing, and retrieval of electronic health information. Version 2.3 is a widely implemented version of the HL7 messaging standard.

## Message Structure

HL7 v2.3 messages are structured as follows:

1. **Segments**: Basic building blocks of HL7 messages, separated by carriage returns (`\r`). Each segment starts with a three-letter code that identifies its type.
2. **Fields**: Components within segments, separated by the pipe (`|`) character.
3. **Components**: Subfields within fields, separated by the caret (`^`) character.
4. **Subcomponents**: Elements within components, separated by the ampersand (`&`) character.
5. **Repetitions**: Repeated fields, separated by the tilde (`~`) character.

### Delimiters

The standard delimiters used in HL7 v2.3 are:

| Delimiter | Character | Description |
|-----------|-----------|-------------|
| Field Separator | `\|` | Separates fields within a segment |
| Component Separator | `^` | Separates components within a field |
| Subcomponent Separator | `&` | Separates subcomponents within a component |
| Repetition Separator | `~` | Separates repeated fields |
| Escape Character | `\\` | Used to escape special characters |

These delimiters are defined in the MSH segment (MSH-1 and MSH-2).

## Common Segments

### MSH (Message Header)

This is the first segment in every HL7 message. It defines the message's source, purpose, destination, and syntax.

```
MSH|^~\&|SENDING_APP|SENDING_FACILITY|RECEIVING_APP|RECEIVING_FACILITY|20230915120000||ADT^A01|MSG00001|P|2.3
```

- MSH-1: Field Separator (`|`)
- MSH-2: Encoding Characters (`^~\&`)
- MSH-3: Sending Application
- MSH-4: Sending Facility
- MSH-5: Receiving Application
- MSH-6: Receiving Facility
- MSH-7: Date/Time of Message
- MSH-8: Security
- MSH-9: Message Type (Message Type^Trigger Event)
- MSH-10: Message Control ID
- MSH-11: Processing ID
- MSH-12: Version ID

### PID (Patient Identification)

Contains patient demographic information.

```
PID|1||12345^^^MRN||DOE^JOHN^Q||19800101|M|||123 MAIN ST^^ANYTOWN^NY^12345||555-123-4567|||S||MRN12345|123-45-6789
```

- PID-1: Set ID
- PID-2: Patient ID (External)
- PID-3: Patient ID (Internal)
- PID-4: Alternate Patient ID
- PID-5: Patient Name (Last^First^Middle)
- PID-6: Mother's Maiden Name
- PID-7: Date/Time of Birth
- PID-8: Sex
- PID-9: Patient Alias
- PID-10: Race
- PID-11: Patient Address
- PID-12: Country Code
- PID-13: Phone Number - Home
- PID-14: Phone Number - Business
- PID-15: Primary Language
- PID-16: Marital Status
- PID-17: Religion
- PID-18: Patient Account Number
- PID-19: SSN Number

### PV1 (Patient Visit)

Contains information about a patient's visit or encounter.

```
PV1|1|I|2WEST^2021^01||||12345^SMITH^JANE^M^MD|67890^JONES^BOB^W^MD|||||||||ADM12345|||||||||||||||||||||||||20230915120000
```

- PV1-1: Set ID
- PV1-2: Patient Class (I=Inpatient, O=Outpatient, E=Emergency, etc.)
- PV1-3: Assigned Patient Location
- PV1-4: Admission Type
- PV1-5: Preadmit Number
- PV1-6: Prior Patient Location
- PV1-7: Attending Doctor
- PV1-8: Referring Doctor
- PV1-9: Consulting Doctor
- PV1-10: Hospital Service
- PV1-11: Temporary Location
- PV1-12: Preadmit Test Indicator
- PV1-13: Re-admission Indicator
- PV1-14: Admit Source
- PV1-15: Ambulatory Status
- PV1-16: VIP Indicator
- PV1-17: Admitting Doctor
- PV1-18: Patient Type
- PV1-19: Visit Number

### ORC (Common Order)

Contains common order information for any order type.

```
ORC|NW|ORD123456|FIL987654|GRP567890|IP||||20230915120000|||12345^SMITH^JANE^M^MD
```

- ORC-1: Order Control (NW=New Order, CA=Cancel, etc.)
- ORC-2: Placer Order Number
- ORC-3: Filler Order Number
- ORC-4: Placer Group Number
- ORC-5: Order Status
- ORC-6: Response Flag
- ORC-7: Quantity/Timing
- ORC-8: Parent
- ORC-9: Date/Time of Transaction
- ORC-10: Entered By
- ORC-11: Verified By
- ORC-12: Ordering Provider

### OBR (Observation Request)

Contains information about a specific order.

```
OBR|1|ORD123456|FIL987654|CBC^Complete Blood Count^LN|||20230915120000|20230915120000||||||20230915120000|BLOOD||12345^SMITH^JANE^M^MD||||||F|||||||
```

- OBR-1: Set ID
- OBR-2: Placer Order Number
- OBR-3: Filler Order Number
- OBR-4: Universal Service Identifier
- OBR-5: Priority
- OBR-6: Requested Date/Time
- OBR-7: Observation Date/Time
- OBR-8: Observation End Date/Time
- OBR-9: Collection Volume
- OBR-10: Collector Identifier
- OBR-11: Specimen Action Code
- OBR-12: Danger Code
- OBR-13: Relevant Clinical Information
- OBR-14: Specimen Received Date/Time
- OBR-15: Specimen Source
- OBR-16: Ordering Provider
- OBR-17: Order Callback Phone Number
- OBR-18: Placer Field 1
- OBR-19: Placer Field 2
- OBR-20: Filler Field 1
- OBR-21: Filler Field 2
- OBR-22: Results Report/Status Change Date/Time
- OBR-23: Charge to Practice
- OBR-24: Diagnostic Service Section ID
- OBR-25: Result Status

### OBX (Observation/Result)

Contains clinical observations and results.

```
OBX|1|NM|WBC^White Blood Cell Count^LN|1|8.5|K/uL|4.5-11.0|N|||F|||20230915120000
```

- OBX-1: Set ID
- OBX-2: Value Type (NM=Numeric, ST=String, TX=Text, etc.)
- OBX-3: Observation Identifier
- OBX-4: Observation Sub-ID
- OBX-5: Observation Value
- OBX-6: Units
- OBX-7: References Range
- OBX-8: Abnormal Flags (H=High, L=Low, N=Normal, etc.)
- OBX-9: Probability
- OBX-10: Nature of Abnormal Test
- OBX-11: Observation Result Status (F=Final, P=Preliminary, etc.)
- OBX-12: Effective Date of Reference Range
- OBX-13: User Defined Access Checks
- OBX-14: Date/Time of the Observation

### EVN (Event Type)

Captures information about the event that triggered the message.

```
EVN|A01|20230915120000
```

- EVN-1: Event Type Code
- EVN-2: Recorded Date/Time
- EVN-3: Date/Time Planned Event
- EVN-4: Event Reason Code
- EVN-5: Operator ID
- EVN-6: Event Occurred

## Common Message Types

HL7 v2.3 supports various message types. The most common ones include:

### ADT Messages (Admission, Discharge, Transfer)

ADT messages communicate patient demographic and visit information.

Common ADT trigger events:
- A01: Admit/Visit Notification
- A02: Transfer a Patient
- A03: Discharge/End Visit
- A04: Register a Patient
- A05: Pre-admit a Patient
- A08: Update Patient Information
- A11: Cancel Admit
- A13: Cancel Discharge

### ORM Messages (Order Message)

ORM messages transmit information about an order (e.g., laboratory tests, medications, etc.).

### ORU Messages (Observation Result)

ORU messages transmit observations and results, such as laboratory results, radiology reports, etc.

### ACK Messages (General Acknowledgment)

ACK messages confirm receipt of a message from a sending system.

```
MSH|^~\&|RECEIVING_APP|RECEIVING_FACILITY|SENDING_APP|SENDING_FACILITY|20230915120000||ACK|ACK00001|P|2.3
MSA|AA|MSG00001|Message Received and Processed Successfully
```

- MSA-1: Acknowledgment Code
  - AA: Application Accept
  - AE: Application Error
  - AR: Application Reject
- MSA-2: Message Control ID (from original message)
- MSA-3: Text Message

## Processing Rules

### Required vs. Optional Fields

HL7 v2.3 defines fields as:
- **Required (R)**: Must be present in the message
- **Optional (O)**: May be omitted
- **Conditional (C)**: Required under certain conditions

### Null Values

In HL7, a null value is represented by two consecutive delimiters with nothing between them. For example, `PID|1||12345` indicates that PID-2 is null.

### Repeating Fields

Some fields can repeat, separated by the repetition separator (`~`).

Example: `OBX|1|CE|ALLERGEN||POLLEN~DUST~MOLD`

## Message Validation

For a message to be valid in HL7 v2.3:

1. It must start with an MSH segment
2. Required segments must be present
3. Required fields within segments must be present
4. Segments must appear in the correct order
5. Data types must be valid for each field

## Security Considerations

When transmitting HL7 messages:

1. **Encryption**: Use TLS/SSL for data in transit
2. **Authentication**: Implement strong authentication mechanisms
3. **Authorization**: Control access to HL7 interfaces
4. **Audit Logging**: Track message access and modifications
5. **Data Sanitization**: Remove PHI/PII for testing and development

## Common Challenges

Working with HL7 v2.3 can present several challenges:

1. **Variations in Implementation**: Different systems may implement the standard differently
2. **Character Encoding**: Ensure consistent encoding (typically ASCII or UTF-8)
3. **Segment Order**: Some systems are sensitive to segment order
4. **Version Compatibility**: Differences between HL7 versions
5. **Message Size**: Large messages can cause processing issues

## Resources

- [HL7 International](https://www.hl7.org/)
- [HL7 v2.3 Documentation](https://www.hl7.org/implement/standards/product_brief.cfm?product_id=140)
- [HL7 Conformance Tool](https://www.hl7.org/documentcenter/public/tools/v2tools.html) 