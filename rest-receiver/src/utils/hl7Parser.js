/**
 * HL7 Parser Utility
 * 
 * This utility parses HL7 v2.3 messages and extracts relevant data.
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
    
    // Split message into segments
    const segments = message.split('\n');
    
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
            let middleName = '';
            
            if (patientName && patientName.includes('^')) {
              const nameParts = patientName.split('^');
              lastName = nameParts[0] || '';
              firstName = nameParts[1] || '';
              middleName = nameParts[2] || '';
            }
            
            // Add patient details to parsed message
            parsedMessage.patient = {
              id: patientId,
              name: {
                full: patientName,
                last: lastName,
                first: firstName,
                middle: middleName
              },
              gender: fields[8] || '',
              dob: fields[7] || '',
              address: fields[11] || ''
            };
          }
          break;
          
        case 'OBR':
          // Observation Request segment
          if (fields.length > 4) {
            parsedMessage.order = {
              id: fields[2] || '',
              fillerId: fields[3] || '',
              universalServiceId: fields[4] || ''
            };
          }
          break;
          
        case 'OBX':
          // Observation/Result segment
          if (fields.length > 5) {
            // Initialize the observation array if it doesn't exist
            if (!parsedMessage.observations) {
              parsedMessage.observations = [];
            }
            
            // Extract observation details
            const observation = {
              setId: fields[1] || '',
              valueType: fields[2] || '',
              observationId: fields[3] || '',
              value: fields[5] || '',
              units: fields[6] || '',
              referenceRange: fields[7] || '',
              abnormalFlags: fields[8] || ''
            };
            
            parsedMessage.observations.push(observation);
          }
          break;
          
        case 'PV1':
          // Patient Visit segment
          if (fields.length > 8) {
            parsedMessage.visit = {
              patientClass: fields[2] || '',
              location: fields[3] || '',
              attendingDoctor: fields[7] || '',
              visitNumber: fields[19] || ''
            };
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
 * Generate an acknowledgment (ACK) message for a received HL7 message
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
      messageControlId
    } = parsedMessage;
    
    // Generate current date/time in HL7 format
    const currentDateTime = moment().format('YYYYMMDDHHmmss');
    
    // Create the MSH segment (switching sender and receiver)
    const msh = `MSH|^~\\&|${receivingApplication}|${receivingFacility}|${sendingApplication}|${sendingFacility}|${currentDateTime}||ACK|ACK${messageControlId}|P|2.3`;
    
    // Create the MSA segment (Message Acknowledgment)
    // AA = Application Accept
    const msa = `MSA|AA|${messageControlId}|Message received and processed successfully`;
    
    // Return the complete ACK message
    return `${msh}\r${msa}`;
    
  } catch (err) {
    console.error('Error generating ACK message:', err);
    return '';
  }
}; 