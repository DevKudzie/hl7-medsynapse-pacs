#!/usr/bin/env python
"""
HL7 v2.3 Message Generator

This script generates sample HL7 v2.3 messages for testing and learning purposes.
"""
import os
import sys
import random
import argparse
from datetime import datetime, timedelta
import uuid
from faker import Faker
from sample_data.templates import (
    ADT_A01_TEMPLATE, ORU_R01_TEMPLATE, ORM_O01_TEMPLATE, ACK_TEMPLATE,
    SENDING_APPLICATIONS, SENDING_FACILITIES, RECEIVING_APPLICATIONS, RECEIVING_FACILITIES,
    PATIENT_CLASSES, LOCATIONS, GENDER_CODES, MARITAL_STATUS_CODES, ORDER_STATUSES,
    VALUE_TYPES, RESULT_STATUSES, ABNORMAL_FLAGS, ACK_CODES,
    UNIVERSAL_SERVICE_IDS, OBSERVATION_IDS
)

# Initialize faker for generating realistic fake data
fake = Faker()

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
    
    # Generate data in HL7 format
    patient_data = {
        'patient_id': str(random.randint(10000, 99999)),
        'patient_name': f"{last_name}^{first_name}^{fake.first_name()[0]}",
        'dob': fake.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y%m%d'),
        'gender': gender,
        'address': f"{fake.street_address()}^^{fake.city()}^{fake.state_abbr()}^{fake.zipcode()}",
        'phone': fake.phone_number().replace('-', ''),
        'marital_status': random.choice(MARITAL_STATUS_CODES),
        'mrn': f"MRN{random.randint(100000, 999999)}",
        'ssn': f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"
    }
    return patient_data

def generate_provider_data():
    """Generate random provider data"""
    provider_data = {
        'attending_id': f"{random.randint(10000, 99999)}",
        'attending_name': f"{fake.last_name()}^{fake.first_name()}^{fake.first_name()[0]}^{random.choice(['MD', 'DO', 'NP', 'PA'])}",
        'referring_id': f"{random.randint(10000, 99999)}",
        'referring_name': f"{fake.last_name()}^{fake.first_name()}^{fake.first_name()[0]}^{random.choice(['MD', 'DO', 'NP', 'PA'])}"
    }
    return provider_data

def generate_adt_message():
    """Generate an ADT (Admission, Discharge, Transfer) message"""
    # Common message data
    message_data = {
        'sending_app': random.choice(SENDING_APPLICATIONS),
        'sending_facility': random.choice(SENDING_FACILITIES),
        'receiving_app': random.choice(RECEIVING_APPLICATIONS),
        'receiving_facility': random.choice(RECEIVING_FACILITIES),
        'datetime': generate_datetime(),
        'message_id': f"MSG{uuid.uuid4().hex[:8].upper()}"
    }
    
    # Add patient data
    message_data.update(generate_patient_data())
    
    # Add provider data
    message_data.update(generate_provider_data())
    
    # Add visit data
    message_data.update({
        'patient_class': random.choice(PATIENT_CLASSES),
        'location': random.choice(LOCATIONS),
        'visit_number': f"VN{random.randint(100000, 999999)}",
        'admit_date': generate_datetime()
    })
    
    return ADT_A01_TEMPLATE.format(**message_data)

def generate_oru_message():
    """Generate an ORU (Observation Result) message"""
    # Common message data
    message_data = {
        'sending_app': random.choice(SENDING_APPLICATIONS),
        'sending_facility': random.choice(SENDING_FACILITIES),
        'receiving_app': random.choice(RECEIVING_APPLICATIONS),
        'receiving_facility': random.choice(RECEIVING_FACILITIES),
        'datetime': generate_datetime(),
        'message_id': f"MSG{uuid.uuid4().hex[:8].upper()}"
    }
    
    # Add patient data
    message_data.update(generate_patient_data())
    
    # Add provider data
    message_data.update(generate_provider_data())
    
    # Add visit data
    message_data.update({
        'patient_class': random.choice(PATIENT_CLASSES),
        'location': random.choice(LOCATIONS),
        'visit_number': f"VN{random.randint(100000, 999999)}"
    })
    
    # Add order data
    order_id = f"ORD{random.randint(100000, 999999)}"
    filler_id = f"FIL{random.randint(100000, 999999)}"
    
    message_data.update({
        'order_id': order_id,
        'filler_id': filler_id,
        'group_id': f"GRP{random.randint(10000, 99999)}",
        'order_status': random.choice(ORDER_STATUSES),
        'order_date': generate_datetime(past_days=60),
        'observation_date': generate_datetime(past_days=30),
        'specimen_collection_date': generate_datetime(past_days=45),
        'specimen_received_date': generate_datetime(past_days=40),
        'specimen_source': random.choice(['Blood', 'Urine', 'CSF', 'Tissue', 'Swab']),
        'ordering_provider': f"{random.randint(10000, 99999)}^{fake.last_name()}^{fake.first_name()}",
        'result_status': random.choice(RESULT_STATUSES),
        'reason': fake.sentence(nb_words=6)
    })
    
    # Add observation data
    observation = random.choice(OBSERVATION_IDS).split('^')
    observation_id = observation[0]
    observation_text = observation[1]
    
    # Generate a test result based on the observation type
    if observation_id in ['WBC', 'RBC', 'HGB', 'GLU', 'K', 'NA', 'CHOL']:
        # Generate numeric values
        if observation_id == 'WBC':
            value = round(random.uniform(3.5, 11.0), 1)
            units = 'K/uL'
            ref_range = '4.5-11.0'
        elif observation_id == 'RBC':
            value = round(random.uniform(3.8, 6.0), 2)
            units = 'M/uL'
            ref_range = '4.2-5.8'
        elif observation_id == 'HGB':
            value = round(random.uniform(11.0, 17.0), 1)
            units = 'g/dL'
            ref_range = '12.0-16.0'
        elif observation_id == 'GLU':
            value = round(random.uniform(70, 180), 0)
            units = 'mg/dL'
            ref_range = '70-110'
        elif observation_id == 'K':
            value = round(random.uniform(3.2, 5.5), 1)
            units = 'mmol/L'
            ref_range = '3.5-5.0'
        elif observation_id == 'NA':
            value = round(random.uniform(130, 148), 0)
            units = 'mmol/L'
            ref_range = '135-145'
        elif observation_id == 'CHOL':
            value = round(random.uniform(130, 280), 0)
            units = 'mg/dL'
            ref_range = '< 200'
        
        # Determine if abnormal
        min_val, max_val = ref_range.replace('<', '').replace('>', '').split('-') if '-' in ref_range else (0, ref_range.strip('< '))
        
        if float(value) < float(min_val):
            abnormal_flag = 'L'
        elif float(value) > float(max_val):
            abnormal_flag = 'H'
        else:
            abnormal_flag = 'N'
            
        observation_value = str(value)
        value_type = 'NM'
    else:
        # Generate text results
        observation_value = fake.sentence(nb_words=5)
        abnormal_flag = random.choice(['N', 'A'])
        units = ''
        ref_range = 'NEGATIVE'
        value_type = 'TX'
    
    message_data.update({
        'universal_service_id': random.choice(UNIVERSAL_SERVICE_IDS),
        'value_type': value_type,
        'observation_id': observation_id,
        'observation_text': observation_text,
        'sub_id': '1',
        'observation_value': observation_value,
        'units': units,
        'reference_range': ref_range,
        'abnormal_flags': abnormal_flag,
        'probability': '1.0',
        'nature_of_abnormality': '',
        'date_last_normal': generate_datetime(past_days=90),
        'user_defined': ''
    })
    
    return ORU_R01_TEMPLATE.format(**message_data)

def generate_orm_message():
    """Generate an ORM (Order Message) message"""
    # Common message data
    message_data = {
        'sending_app': random.choice(SENDING_APPLICATIONS),
        'sending_facility': random.choice(SENDING_FACILITIES),
        'receiving_app': random.choice(RECEIVING_APPLICATIONS),
        'receiving_facility': random.choice(RECEIVING_FACILITIES),
        'datetime': generate_datetime(),
        'message_id': f"MSG{uuid.uuid4().hex[:8].upper()}"
    }
    
    # Add patient data
    message_data.update(generate_patient_data())
    
    # Add provider data
    message_data.update(generate_provider_data())
    
    # Add visit data
    message_data.update({
        'patient_class': random.choice(PATIENT_CLASSES),
        'location': random.choice(LOCATIONS),
        'visit_number': f"VN{random.randint(100000, 999999)}"
    })
    
    # Add order data
    message_data.update({
        'order_id': f"ORD{random.randint(100000, 999999)}",
        'filler_id': f"FIL{random.randint(100000, 999999)}",
        'group_id': f"GRP{random.randint(10000, 99999)}",
        'order_status': random.choice(ORDER_STATUSES),
        'order_date': generate_datetime(past_days=30),
        'observation_date': generate_datetime(past_days=15),
        'universal_service_id': random.choice(UNIVERSAL_SERVICE_IDS),
        'ordering_provider': f"{random.randint(10000, 99999)}^{fake.last_name()}^{fake.first_name()}",
        'clinical_info': fake.sentence(nb_words=10),
        'reason': fake.sentence(nb_words=6)
    })
    
    return ORM_O01_TEMPLATE.format(**message_data)

def generate_ack_message(message_id):
    """Generate an ACK (Acknowledgment) message"""
    # Common message data
    message_data = {
        'sending_app': random.choice(RECEIVING_APPLICATIONS),  # Reverse sender/receiver
        'sending_facility': random.choice(RECEIVING_FACILITIES),
        'receiving_app': random.choice(SENDING_APPLICATIONS),
        'receiving_facility': random.choice(SENDING_FACILITIES),
        'datetime': generate_datetime(),
        'message_id': f"MSG{uuid.uuid4().hex[:8].upper()}",
        'ack_code': random.choice(ACK_CODES),
        'message_control_id': message_id,
        'text_message': random.choice(['Message Received', 'Message Processed', 'Error Processing Message', 'Invalid Message Format', ''])
    }
    
    return ACK_TEMPLATE.format(**message_data)

def main():
    parser = argparse.ArgumentParser(description='Generate HL7 v2.3 messages')
    parser.add_argument('--count', type=int, default=5, help='Number of messages to generate')
    parser.add_argument('--type', type=str, choices=['ADT', 'ORU', 'ORM', 'ACK', 'ALL'], default='ALL', 
                        help='Type of HL7 message to generate')
    parser.add_argument('--output', type=str, default='hl7_messages.txt', help='Output file name')
    
    args = parser.parse_args()
    
    print(f"Generating {args.count} HL7 messages of type {args.type}...")
    
    messages = []
    message_types = ['ADT', 'ORU', 'ORM']
    
    for i in range(args.count):
        if args.type == 'ALL':
            msg_type = random.choice(message_types)
        else:
            msg_type = args.type
        
        if msg_type == 'ADT':
            messages.append(generate_adt_message())
        elif msg_type == 'ORU':
            messages.append(generate_oru_message())
        elif msg_type == 'ORM':
            messages.append(generate_orm_message())
        elif msg_type == 'ACK':
            # For ACK we need a message ID to acknowledge
            messages.append(generate_ack_message(f"MSG{uuid.uuid4().hex[:8].upper()}"))
    
    # Write messages to file
    with open(args.output, 'w') as f:
        for msg in messages:
            f.write(msg)
            f.write('\n\n')
    
    print(f"Generated {args.count} HL7 messages and saved to {args.output}")

if __name__ == "__main__":
    main() 