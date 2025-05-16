"""
Templates for generating HL7 v2.3 messages with dummy data.
"""

# ADT (Admission, Discharge, Transfer) Message Template
ADT_A01_TEMPLATE = """MSH|^~\\&|{sending_app}|{sending_facility}|{receiving_app}|{receiving_facility}|{datetime}||ADT^A01|{message_id}|P|2.3
EVN|A01|{datetime}
PID|1||{patient_id}^^^MRN||{patient_name}||{dob}|{gender}|||{address}||{phone}|||{marital_status}||{mrn}|{ssn}
PV1|1|{patient_class}|{location}||||{attending_id}^{attending_name}|{referring_id}^{referring_name}|||||||||{visit_number}|||||||||||||||||||||||||{admit_date}
"""

# ORU (Observation Result) Message Template
ORU_R01_TEMPLATE = """MSH|^~\\&|{sending_app}|{sending_facility}|{receiving_app}|{receiving_facility}|{datetime}||ORU^R01|{message_id}|P|2.3
PID|1||{patient_id}^^^MRN||{patient_name}||{dob}|{gender}|||{address}||{phone}|||{marital_status}||{mrn}|{ssn}
PV1|1|{patient_class}|{location}||||{attending_id}^{attending_name}|{referring_id}^{referring_name}|||||||||{visit_number}
ORC|RE|{order_id}|{filler_id}|{group_id}|{order_status}||||{order_date}
OBR|1|{order_id}|{filler_id}|{universal_service_id}|||{observation_date}|{specimen_collection_date}||||||{specimen_received_date}|{specimen_source}||{ordering_provider}||||||{result_status}|||{reason}|
OBX|1|{value_type}|{observation_id}^{observation_text}|{sub_id}|{observation_value}|{units}|{reference_range}|{abnormal_flags}|{probability}|{nature_of_abnormality}|{result_status}|{date_last_normal}|{user_defined}|{observation_date}
"""

# ORM (Order Message) Template
ORM_O01_TEMPLATE = """MSH|^~\\&|{sending_app}|{sending_facility}|{receiving_app}|{receiving_facility}|{datetime}||ORM^O01|{message_id}|P|2.3
PID|1||{patient_id}^^^MRN||{patient_name}||{dob}|{gender}|||{address}||{phone}|||{marital_status}||{mrn}|{ssn}
PV1|1|{patient_class}|{location}||||{attending_id}^{attending_name}|{referring_id}^{referring_name}|||||||||{visit_number}
ORC|NW|{order_id}|{filler_id}|{group_id}|{order_status}||||{order_date}|||{ordering_provider}
OBR|1|{order_id}|{filler_id}|{universal_service_id}|||{order_date}|||||{clinical_info}|||{ordering_provider}|||||||||||{observation_date}|||{reason}|
"""

# Acknowledgment Message Template
ACK_TEMPLATE = """MSH|^~\\&|{sending_app}|{sending_facility}|{receiving_app}|{receiving_facility}|{datetime}||ACK|{message_id}|P|2.3
MSA|{ack_code}|{message_control_id}|{text_message}
"""

# Common field values for testing
SENDING_APPLICATIONS = [
    "EPIC", "CERNER", "MEDITECH", "ALLSCRIPTS", "NEXTGEN"
]

SENDING_FACILITIES = [
    "GENERAL HOSPITAL", "MEDICAL CENTER", "COMMUNITY CLINIC", "PRIMARY CARE", "SPECIALTY CENTER"
]

RECEIVING_APPLICATIONS = [
    "LAB_SYS", "RADIOLOGY_SYS", "PHARMACY_SYS", "BILLING_SYS", "EMR_SYS"
]

RECEIVING_FACILITIES = [
    "LAB CORP", "RADIOLOGY CENTER", "CENTRAL PHARMACY", "BILLING DEPT", "RECORDS DEPT"
]

PATIENT_CLASSES = [
    "I", "O", "E", "P", "R"  # Inpatient, Outpatient, Emergency, Preadmit, Recurring
]

LOCATIONS = [
    "WEST^2021^01", "EAST^3011^02", "ICU^1001^01", "ER^1500^01", "OR^2500^02"
]

GENDER_CODES = [
    "M", "F", "O", "U", "A"  # Male, Female, Other, Unknown, Ambiguous
]

MARITAL_STATUS_CODES = [
    "S", "M", "D", "W", "A", "U"  # Single, Married, Divorced, Widowed, Annulled, Unknown
]

ORDER_STATUSES = [
    "IP", "CM", "CA", "DC", "RP"  # In Process, Completed, Cancelled, Discontinued, Replaced
]

VALUE_TYPES = [
    "NM", "ST", "TX", "FT", "CE"  # Numeric, String, Text, Formatted Text, Coded Entry
]

RESULT_STATUSES = [
    "F", "P", "C", "X", "I"  # Final, Preliminary, Correction, Cancelled, Pending
]

ABNORMAL_FLAGS = [
    "L", "H", "LL", "HH", "N", "<", ">"  # Low, High, Critical Low, Critical High, Normal, Below, Above
]

ACK_CODES = [
    "AA", "AE", "AR", "CR", "CE"  # Application Accept, Application Error, Application Reject, Commit Reject, Commit Error
]

# Sample Universal Service IDs (Test Codes)
UNIVERSAL_SERVICE_IDS = [
    "CBC^Complete Blood Count^LN",
    "CHEM7^Basic Metabolic Panel^LN",
    "LIPID^Lipid Panel^LN",
    "CXR^Chest X-Ray^LN",
    "URIN^Urinalysis^LN"
]

# Sample Observation IDs
OBSERVATION_IDS = [
    "WBC^White Blood Cell Count^LN",
    "RBC^Red Blood Cell Count^LN",
    "HGB^Hemoglobin^LN",
    "GLU^Glucose^LN",
    "K^Potassium^LN",
    "NA^Sodium^LN",
    "CHOL^Cholesterol^LN"
] 