/**
 * HL7 Parser Utility for Medsynapse PACS
 * 
 * This utility parses HL7 v2.3 messages according to the Medsynapse PACS conformance statement.
 */
const moment = require('moment');

/**
 * Parse an HL7 message and extract key information
 * @param {string} message - Raw HL7 message
 * @returns {Object} Parsed message data
 */
exports.parseHL7 = (message) => {
  try {
    if (!message || typeof message !== 'string') {
      console.error('Invalid message format');
      return null;
    }
    
    // Split message into segments by carriage return
    let segments = message.split('\r');
    if (segments.length === 1) {
      // Try splitting by newline if carriage return didn't work
      segments = message.split('\n');
    }
    
    // Check if we have an MSH segment
    if (!segments[0] || !segments[0].startsWith('MSH|')) {
      console.error('No MSH segment found');
      return null;
    }
    
    // Extract fields from MSH segment
    const mshFields = segments[0].split('|');
    
    if (mshFields.length < 10) {
      console.error('MSH segment has insufficient fields');
      return null;
    }
    
    // Extract message type and trigger event from MSH-9
    let messageType = 'Unknown';
    let triggerEvent = '';
    
    if (mshFields[8] && mshFields[8].includes('^')) {
      const msgTypeParts = mshFields[8].split('^');
      messageType = msgTypeParts[0] || 'Unknown';
      triggerEvent = msgTypeParts[1] || '';
    } else if (mshFields[8]) {
      messageType = mshFields[8];
    }
    
    // Extract other key fields
    const sendingApp = mshFields[2] || '';
    const sendingFacility = mshFields[3] || '';
    const receivingApp = mshFields[4] || '';
    const receivingFacility = mshFields[5] || '';
    const messageDateTime = mshFields[6] || '';
    const messageControlId = mshFields[9] || '';
    
    // Initialize the parsed message object
    const parsedMessage = {
      messageType,
      triggerEvent,
      messageControlId,
      sendingApplication: sendingApp,
      sendingFacility,
      receivingApplication: receivingApp,
      receivingFacility,
      messageDateTime,
      segments: {}
    };
    
    // Process all segments
    for (const segment of segments) {
      if (!segment || segment.trim() === '') continue;
      
      const segmentId = segment.substring(0, 3);
      const fields = segment.split('|');
      
      // Store the segment data
      parsedMessage.segments[segmentId] = fields;
      
      // Process specific segments based on message type
      switch (segmentId) {
        case 'PID':
          // Patient Identification segment
          if (fields.length > 5) {
            // Extract patient ID and name
            const patientId = fields[3] || '';
            const patientName = fields[5] || '';
            
            // Parse patient name components if available
            let lastName = '';
            let firstName = '';
            
            if (patientName && patientName.includes('^')) {
              const nameParts = patientName.split('^');
              lastName = nameParts[0] || '';
              firstName = nameParts[1] || '';
            }
            
            // Add patient details to parsed message
            parsedMessage.patient = {
              id: patientId,
              name: {
                full: patientName,
                last: lastName,
                first: firstName
              },
              gender: fields[8] || '',
              dob: fields[7] || '',
              admissionId: fields[18] || ''
            };
          }
          break;
          
        case 'OBR':
          // Observation Request segment - follows Medsynapse field mapping
          if (fields.length > 4) {
            parsedMessage.order = {
              accessionNumber: fields[2] || '',
              spsId: fields[4]?.split('^')?.[0] || '',
              spsDescription: fields[4]?.split('^')?.[1] || '',
              priority: fields[5] || '',
              rpDescription: fields[15] || '',
              ssName: fields[18] || '',
              rpId: fields[19] || '',
              spsLocation: fields[20] || '',
              ssAeTitle: fields[21] || '',
              modality: fields[24] || '',
              reasonForStudy: fields[31] || '',
              performingPhysician: fields[34] || '',
              spsStartDateTime: fields[36] || ''
            };
          }
          break;
          
        case 'OBX':
          // Observation/Result segment - modified for Medsynapse report format
          if (fields.length > 5) {
            const reportFormat = fields[2] || '';
            const studyId = fields[3]?.split('^')?.[0] || '';
            const studyDescription = fields[3]?.split('^')?.[1] || '';
            
            // Unescape the report text
            let reportText = fields[5] || '';
            reportText = reportText.replace(/\\X0D\\\\X0A\\/g, '\n');
            reportText = reportText.replace(/\\F\\/g, '|');
            reportText = reportText.replace(/\\S\\/g, '^');
            reportText = reportText.replace(/\\T\\/g, '&');
            reportText = reportText.replace(/\\R\\/g, '~');
            reportText = reportText.replace(/\\E\\/g, '\\');
            
            parsedMessage.report = {
              studyId,
              studyDescription,
              format: reportFormat,
              text: reportText,
              status: fields[11] || '',
              date: fields[14] || '',
              radiologistId: fields[16]?.split('^')?.[0] || '',
              radiologistName: fields[16]?.split('^')?.[1] || ''
            };
          }
          break;
          
        case 'ORC':
          // Order Control segment
          if (fields.length > 1) {
            parsedMessage.orderControl = fields[1] || '';
            
            // Add institution and requesting physician
            if (fields.length > 12) {
              parsedMessage.requestingPhysician = fields[12]?.split('^')?.[1] || '';
            }
            
            if (fields.length > 17) {
              parsedMessage.institutionName = fields[17]?.split('^')?.[1] || '';
            }
          }
          break;
          
        case 'MRG':
          // Merge segment for patient merges (ADT^A40)
          if (fields.length > 1) {
            parsedMessage.mergeInfo = {
              oldPatientId: fields[1] || ''
            };
          }
          break;
          
        case 'PV1':
          // Patient Visit segment - extract only what Medsynapse uses
          if (fields.length > 8) {
            parsedMessage.visit = {
              patientClass: fields[2] || '',
              referringPhysician: fields[8]?.split('^')?.[1] || '',
              patientWeight: fields[20] || ''
            };
          }
          break;
          
        case 'ZDS':
          // Custom ZDS segment for Study Instance UID
          if (fields.length > 1) {
            parsedMessage.studyInstanceUid = fields[1] || '';
          }
          break;
      }
    }
    
    return parsedMessage;
    
  } catch (err) {
    console.error('Error parsing HL7 message:', err);
    return null;
  }
};

/**
 * Generate an acknowledgment (ACK) message for a received HL7 message according to Medsynapse specs
 * @param {Object} parsedMessage - Parsed HL7 message
 * @returns {string} ACK message
 */
exports.generateAcknowledgment = (parsedMessage) => {
  try {
    if (!parsedMessage) {
      return '';
    }
    
    // Extract required fields from the parsed message
    const {
      sendingApplication,
      sendingFacility,
      receivingApplication,
      receivingFacility,
      messageControlId,
      triggerEvent
    } = parsedMessage;
    
    // Generate current date/time in HL7 format
    const currentDateTime = moment().format('YYYYMMDDHHmmss');
    
    // Determine the trigger event (from the original message type)
    const ackTriggerEvent = triggerEvent || 'O01'; // Default to O01 if none provided
    
    // Create the MSH segment (switching sender and receiver) according to Medsynapse format
    const msh = `MSH|^~\\&|${receivingApplication}|${receivingFacility}|${sendingApplication}|${sendingFacility}|${currentDateTime}||ACK^${ackTriggerEvent}|ACK${Date.now()}|P|2.3|1||||91|||`;
    
    // Create the MSA segment (Message Acknowledgment)
    // AA = Application Accept
    const msa = `MSA|AA|${messageControlId}|Message received and processed successfully|||`;
    
    // Return the complete ACK message with carriage returns
    return `${msh}\r${msa}`;
    
  } catch (err) {
    console.error('Error generating ACK message:', err);
    return '';
  }
}; 