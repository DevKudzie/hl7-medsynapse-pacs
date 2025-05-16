"""
Templates for generating HL7 v2.3 messages according to Medsynapse PACS conformance statement.
"""

# ORM (Order Message) Template for Order Update - used for new orders, updates, cancellations
ORM_O01_TEMPLATE = """MSH|^~\\&|{sending_app}|{sending_facility}|{receiving_app}|{receiving_facility}|{datetime}||ORM^O01|{message_id}|P|2.3
PID|1||{patient_id}||{patient_name}||{dob}|{gender}||||||||||{admission_id}
PV1|1|{patient_class}||||||^{referring_physician}||||||||||||{patient_weight}
ORC|{order_control}|||||||||||^{requesting_physician}|||||^{institution_name}
OBR|1|{accession_number}||{sps_id}^{sps_description}|{priority}||||||||||{rp_description}|||{ss_name}|{rp_id}|{sps_location}|{ss_aetitle}|||{modality}|||||||{reason_for_study}|||{performing_physician}||{sps_start_datetime}
ZDS|{study_instance_uid}
"""

# ORU (Observation Result) Template for Report Update
ORU_R01_TEMPLATE = """MSH|^~\\&|{sending_app}|{sending_facility}|{receiving_app}|{receiving_facility}|{datetime}||ORU^R01|{message_id}|P|2.3|1|||||||
PID|1||{patient_id}||{patient_name}||{dob}|{gender}||||||||||{admission_id}||||||||||||
PV1|1|{patient_class}||||||^{referring_physician}||||||||||||{patient_weight}||||||||||||||||||||||||||||||||
ORC|{order_control}|||||||||||^{requesting_physician}|||||^{institution_name}|||||||
OBR|1|{accession_number}||{sps_id}^{sps_description}|{priority}||||||||||{rp_description}|||{ss_name}|{rp_id}|{sps_location}|{ss_aetitle}|||{modality}|||||||{reason_for_study}|||{performing_physician}||{sps_start_datetime}|||||||||
OBX||{report_format}|{study_id}^{study_description}||{report_text}||||||{report_status}|||{report_date}||{radiologist_id}^{radiologist_name}|
"""

# ADT (Patient Information Update) Message Template
ADT_A08_TEMPLATE = """MSH|^~\\&|{sending_app}|{sending_facility}|{receiving_app}|{receiving_facility}|{datetime}||ADT^A08|{message_id}|P|2.3
EVN|A08|{datetime}
PID|1||{patient_id}||{patient_name}|||{gender}||||||||||{admission_id}
"""

# ADT (Patient Merge) Message Template
ADT_A40_TEMPLATE = """MSH|^~\\&|{sending_app}|{sending_facility}|{receiving_app}|{receiving_facility}|{datetime}||ADT^A40|{message_id}|P|2.3
EVN|A40|{datetime}
PID|1||{patient_id_new}
MRG|{patient_id_old}
"""

# Acknowledgment Message Template
ACK_TEMPLATE = """MSH|^~\\&|{receiving_app}|{receiving_facility}|{sending_app}|{sending_facility}|{datetime}||ACK^{trigger_event}|{message_id}|P|2.3|1||||91|||
MSA|{ack_code}|{message_control_id}|{text_message}|||
"""

# Common field values for testing
SENDING_APPLICATIONS = [
    "HIS_APP", "RIS_SYS", "EMR_APP", "CLINIC_SYS", "LAB_SYS"
]

SENDING_FACILITIES = [
    "HIS_FACILITY", "RADIOLOGY_DEPT", "MAIN_HOSPITAL", "IMAGING_CENTER", "MEDICAL_CENTER"
]

RECEIVING_APPLICATIONS = [
    "PACS_APP", "BROKER_APP", "ARCHIVE_SYS", "WORKLIST_SYS", "VNA_SYS"
]

RECEIVING_FACILITIES = [
    "PACS_FACILITY", "IMAGING_ARCHIVE", "RADIOLOGY_PACS", "ENTERPRISE_ARCHIVE", "CLOUD_STORAGE"
]

PATIENT_CLASSES = [
    "I", "O", "E", "P", "R"  # Inpatient, Outpatient, Emergency, Preadmit, Recurring
]

ORDER_CONTROLS = [
    "NW", "CA", "CM", "XO"  # New Order, Cancel, Complete, Change Order
]

GENDER_CODES = [
    "M", "F", "O", "U"  # Male, Female, Other, Unknown
]

MODALITY_CODES = [
    "CR", "CT", "DX", "ES", "GM", "IO", "MG", "MR", "NM", "PX",
    "RF", "OT", "PT", "SC", "SM", "US", "XA", "XC", "ECG"
]

REPORT_FORMATS = [
    "TX", "RTF"  # Plain Text, Rich Text Format
]

REPORT_STATUSES = [
    "I", "R", "F", "P"  # STUDY COMPLETED, REPORT READ, REPORT FINAL, REPORT PRINT
]

PRIORITIES = [
    "ROUTINE", "STAT", "ASAP", "STANDBY"
]

ACK_CODES = [
    "AA", "AR", "AE"  # Application Accept, Application Reject, Application Error
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