#!/usr/bin/env python
"""
HL7 v2.3 Message Generator for Medsynapse PACS

This script generates sample HL7 v2.3 messages following the Medsynapse PACS conformance statement.
"""
import os
import sys
import random
import argparse
from datetime import datetime, timedelta
import uuid
import re
from faker import Faker
from sample_data.templates import (
    ORM_O01_TEMPLATE, ORU_R01_TEMPLATE, ADT_A08_TEMPLATE, ADT_A40_TEMPLATE, ACK_TEMPLATE,
    SENDING_APPLICATIONS, SENDING_FACILITIES, RECEIVING_APPLICATIONS, RECEIVING_FACILITIES,
    PATIENT_CLASSES, GENDER_CODES, ORDER_CONTROLS, MODALITY_CODES, 
    REPORT_FORMATS, REPORT_STATUSES, PRIORITIES, ACK_CODES
)

# Initialize faker for generating realistic fake data
fake = Faker()

def escape_hl7_chars(text):
    """Escape special HL7 characters in text data"""
    if not text:
        return text
    
    # Replace special HL7 characters with escape sequences
    # Field separator | -> \F\
    # Component separator ^ -> \S\
    # Subcomponent separator & -> \T\
    # Repetition separator ~ -> \R\
    # Escape character \ -> \E\
    # New line -> \X0D\\X0A\
    
    text = text.replace('\\', '\\E\\')
    text = text.replace('|', '\\F\\')
    text = text.replace('^', '\\S\\')
    text = text.replace('&', '\\T\\')
    text = text.replace('~', '\\R\\')
    text = text.replace('\r\n', '\\X0D\\\\X0A\\')
    text = text.replace('\n', '\\X0D\\\\X0A\\')
    
    return text

def generate_datetime(past_days=30):
    """Generate a random datetime within the past number of days"""
    random_date = datetime.now() - timedelta(days=random.randint(0, past_days))
    return random_date.strftime('%Y%m%d%H%M%S')

def generate_patient_data():
    """Generate random patient demographic data"""
    gender = random.choice(GENDER_CODES)
    if gender == 'M':
        first_name = fake.first_name_male()
    elif gender == 'F':
        first_name = fake.first_name_female()
    else:
        first_name = fake.first_name()
    
    last_name = fake.last_name()
    
    # Generate data in HL7 format (Note: Limited fields as per Medsynapse spec)
    patient_data = {
        'patient_id': str(random.randint(100000, 999999)),
        'patient_name': f"{last_name}^{first_name}",
        'dob': fake.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y%m%d'),
        'gender': gender,
        'admission_id': f"ADM{random.randint(100000, 999999)}"
    }
    return patient_data

def generate_physician_data():
    """Generate random physician data"""
    physician_data = {
        'referring_physician': fake.last_name(),
        'requesting_physician': fake.last_name(),
        'performing_physician': fake.last_name(),
        'radiologist_id': f"RAD{random.randint(1000, 9999)}",
        'radiologist_name': fake.last_name()
    }
    return physician_data

def generate_study_data():
    """Generate random study/order data"""
    accession_number = f"ACC.{random.randint(100000, 999999)}"
    modality = random.choice(MODALITY_CODES)
    
    # Create study descriptions based on modality
    if modality == "CT":
        sps_description = random.choice(["CT HEAD", "CT CHEST", "CT ABDOMEN", "CT SPINE"])
        rp_description = f"{sps_description} W/WO CONTRAST"
    elif modality == "MR":
        sps_description = random.choice(["MR BRAIN", "MR KNEE", "MR SHOULDER", "MR SPINE"])
        rp_description = f"{sps_description} W/WO CONTRAST"
    elif modality == "US":
        sps_description = random.choice(["US ABDOMEN", "US PELVIS", "US THYROID", "US BREAST"])
        rp_description = sps_description
    elif modality == "CR" or modality == "DX":
        sps_description = random.choice(["XR CHEST", "XR HAND", "XR FOOT", "XR KNEE"])
        rp_description = sps_description
    else:
        sps_description = f"{modality} PROCEDURE"
        rp_description = sps_description
    
    study_data = {
        'accession_number': accession_number,
        'sps_id': f"SPS{random.randint(10000, 99999)}",
        'sps_description': sps_description,
        'rp_id': f"RP{random.randint(10000, 99999)}",
        'rp_description': rp_description,
        'ss_name': f"SS{random.randint(100, 999)}",
        'ss_aetitle': f"AETITLE{random.randint(1, 9)}",
        'sps_location': f"ROOM{random.randint(1, 20)}",
        'modality': modality,
        'priority': random.choice(PRIORITIES),
        'reason_for_study': fake.sentence(nb_words=6),
        'sps_start_datetime': generate_datetime(past_days=7),
        'institution_name': random.choice(["MAIN HOSPITAL", "IMAGING CENTER", "CLINIC"]),
        'study_instance_uid': f"1.2.826.0.1.3680043.{random.randint(1000000, 9999999)}",
        'patient_weight': str(random.randint(50, 120)),
        'study_id': f"STD{random.randint(10000, 99999)}",
        'study_description': sps_description
    }
    return study_data

def generate_report_data():
    """Generate random report data"""
    report_data = {
        'report_format': random.choice(REPORT_FORMATS),
        'report_status': random.choice(REPORT_STATUSES),
        'report_date': generate_datetime(past_days=5),
        'report_text': escape_hl7_chars(fake.paragraph(nb_sentences=3))
    }
    return report_data

def generate_orm_message():
    """Generate an ORM^O01 (Order Message) following Medsynapse format"""
    # Common message data
    message_data = {
        'sending_app': random.choice(SENDING_APPLICATIONS),
        'sending_facility': random.choice(SENDING_FACILITIES),
        'receiving_app': random.choice(RECEIVING_APPLICATIONS),
        'receiving_facility': random.choice(RECEIVING_FACILITIES),
        'datetime': generate_datetime(past_days=1),
        'message_id': f"MSG{uuid.uuid4().hex[:8].upper()}",
        'order_control': random.choice(ORDER_CONTROLS),
        'patient_class': random.choice(PATIENT_CLASSES)
    }
    
    # Add patient data
    message_data.update(generate_patient_data())
    
    # Add physician data
    message_data.update(generate_physician_data())
    
    # Add study data
    message_data.update(generate_study_data())
    
    return ORM_O01_TEMPLATE.format(**message_data)

def generate_oru_message():
    """Generate an ORU^R01 (Observation Result) following Medsynapse format"""
    # Common message data
    message_data = {
        'sending_app': random.choice(SENDING_APPLICATIONS),
        'sending_facility': random.choice(SENDING_FACILITIES),
        'receiving_app': random.choice(RECEIVING_APPLICATIONS),
        'receiving_facility': random.choice(RECEIVING_FACILITIES),
        'datetime': generate_datetime(past_days=1),
        'message_id': f"MSG{uuid.uuid4().hex[:8].upper()}",
        'order_control': "RE",  # Results
        'patient_class': random.choice(PATIENT_CLASSES)
    }
    
    # Add patient data
    message_data.update(generate_patient_data())
    
    # Add physician data
    message_data.update(generate_physician_data())
    
    # Add study data
    message_data.update(generate_study_data())
    
    # Add report data
    message_data.update(generate_report_data())
    
    return ORU_R01_TEMPLATE.format(**message_data)

def generate_adt_a08_message():
    """Generate an ADT^A08 (Patient Information Update) following Medsynapse format"""
    # Common message data
    message_data = {
        'sending_app': random.choice(SENDING_APPLICATIONS),
        'sending_facility': random.choice(SENDING_FACILITIES),
        'receiving_app': random.choice(RECEIVING_APPLICATIONS),
        'receiving_facility': random.choice(RECEIVING_FACILITIES),
        'datetime': generate_datetime(past_days=1),
        'message_id': f"MSG{uuid.uuid4().hex[:8].upper()}"
    }
    
    # Add patient data
    message_data.update(generate_patient_data())
    
    return ADT_A08_TEMPLATE.format(**message_data)

def generate_adt_a40_message():
    """Generate an ADT^A40 (Patient Merge) following Medsynapse format"""
    # Common message data
    message_data = {
        'sending_app': random.choice(SENDING_APPLICATIONS),
        'sending_facility': random.choice(SENDING_FACILITIES),
        'receiving_app': random.choice(RECEIVING_APPLICATIONS),
        'receiving_facility': random.choice(RECEIVING_FACILITIES),
        'datetime': generate_datetime(past_days=1),
        'message_id': f"MSG{uuid.uuid4().hex[:8].upper()}",
        'patient_id_new': str(random.randint(100000, 999999)),
        'patient_id_old': str(random.randint(100000, 999999))
    }
    
    return ADT_A40_TEMPLATE.format(**message_data)

def generate_ack_message(message_id, trigger_event="O01"):
    """Generate an acknowledgment (ACK) message"""
    ack_data = {
        'receiving_app': random.choice(RECEIVING_APPLICATIONS),
        'receiving_facility': random.choice(RECEIVING_FACILITIES),
        'sending_app': random.choice(SENDING_APPLICATIONS),
        'sending_facility': random.choice(SENDING_FACILITIES),
        'datetime': datetime.now().strftime('%Y%m%d%H%M%S'),
        'message_id': f"ACK{uuid.uuid4().hex[:8].upper()}",
        'ack_code': random.choice(ACK_CODES),
        'message_control_id': message_id,
        'text_message': "Message processed successfully" if random.random() > 0.2 else "Processing error",
        'trigger_event': trigger_event
    }
    
    return ACK_TEMPLATE.format(**ack_data)

def main():
    parser = argparse.ArgumentParser(description='Generate sample HL7 v2.3 messages for Medsynapse PACS')
    parser.add_argument('--count', type=int, default=5, help='Number of messages to generate')
    parser.add_argument('--output', type=str, default='sample_messages.txt', help='Output file')
    parser.add_argument('--types', type=str, default='all', help='Comma-separated list of message types to generate (orm, oru, adt_a08, adt_a40, all)')
    
    args = parser.parse_args()
    
    # Determine which message types to generate
    message_types = []
    if args.types.lower() == 'all':
        message_types = ['orm', 'oru', 'adt_a08', 'adt_a40']
    else:
        message_types = [t.strip().lower() for t in args.types.split(',')]
    
    messages = []
    
    # Generate the specified number of each message type
    for _ in range(args.count):
        for msg_type in message_types:
            if msg_type == 'orm':
                messages.append(generate_orm_message())
            elif msg_type == 'oru':
                messages.append(generate_oru_message())
            elif msg_type == 'adt_a08':
                messages.append(generate_adt_a08_message())
            elif msg_type == 'adt_a40':
                messages.append(generate_adt_a40_message())
    
    # Write messages to output file
    with open(args.output, 'w') as f:
        for i, message in enumerate(messages):
            f.write(message)
            if i < len(messages) - 1:
                f.write('\n\n')
    
    print(f"Generated {len(messages)} HL7 messages and saved to {args.output}")

if __name__ == "__main__":
    main() 