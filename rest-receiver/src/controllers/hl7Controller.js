/**
 * HL7 Controller
 * 
 * This file contains the controller logic for processing HL7 messages.
 */
const path = require('path');
const fs = require('fs');
const moment = require('moment');
const hl7Parser = require('../utils/hl7Parser');

// In-memory store for messages (would use a database in production)
const messages = [];
let messageCounter = 0;

/**
 * Receive and process an HL7 message
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.receiveMessage = async (req, res) => {
  try {
    const { message, messageType, sendTime } = req.body;
    
    if (!message) {
      return res.status(400).json({ error: 'No message provided' });
    }
    
    // Decode base64 message
    let decodedMessage;
    try {
      decodedMessage = Buffer.from(message, 'base64').toString('utf-8');
    } catch (err) {
      return res.status(400).json({ error: 'Invalid message encoding' });
    }
    
    // Parse the HL7 message
    const parsedMessage = hl7Parser.parseHL7(decodedMessage);
    
    if (!parsedMessage) {
      return res.status(400).json({ error: 'Failed to parse HL7 message' });
    }
    
    // Store the message
    const receivedTime = moment().format();
    const messageId = ++messageCounter;
    
    const storedMessage = {
      id: messageId,
      messageType: parsedMessage.messageType || messageType || 'Unknown',
      messageControlId: parsedMessage.messageControlId || 'Unknown',
      sendTime: sendTime || receivedTime,
      receivedTime,
      message: decodedMessage,
      parsedMessage
    };
    
    messages.push(storedMessage);
    
    // Also save to a file for persistence
    const storageDir = path.join(__dirname, '../../storage');
    if (!fs.existsSync(storageDir)) {
      fs.mkdirSync(storageDir, { recursive: true });
    }
    
    // Save the raw message to a timestamped file
    const timestamp = moment().format('YYYYMMDD_HHmmss');
    const messageFilename = `${timestamp}_${messageId}_${storedMessage.messageType}.hl7`;
    fs.writeFileSync(path.join(storageDir, messageFilename), decodedMessage);
    
    // Log the message receipt
    console.log(`Received HL7 message type ${storedMessage.messageType} with control ID ${storedMessage.messageControlId}`);
    
    // Generate an acknowledgment
    const ackMessage = hl7Parser.generateAcknowledgment(parsedMessage);
    
    return res.status(200).json({
      message: 'Message received successfully',
      messageId,
      acknowledgment: ackMessage
    });
    
  } catch (err) {
    console.error('Error processing HL7 message:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
};

/**
 * Get all received messages
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.getMessages = (req, res) => {
  // Pagination
  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 10;
  const startIndex = (page - 1) * limit;
  const endIndex = page * limit;
  
  // Filter by message type if provided
  const messageType = req.query.type;
  
  let filteredMessages = messages;
  if (messageType) {
    filteredMessages = messages.filter(msg => msg.messageType.includes(messageType));
  }
  
  // Add pagination info
  const results = {
    totalCount: filteredMessages.length,
    totalPages: Math.ceil(filteredMessages.length / limit),
    currentPage: page
  };
  
  // Add next/prev page info if available
  if (endIndex < filteredMessages.length) {
    results.nextPage = page + 1;
  }
  
  if (startIndex > 0) {
    results.prevPage = page - 1;
  }
  
  // Get the paginated messages, excluding the full message content for brevity
  results.messages = filteredMessages.slice(startIndex, endIndex).map(msg => ({
    id: msg.id,
    messageType: msg.messageType,
    messageControlId: msg.messageControlId,
    sendTime: msg.sendTime,
    receivedTime: msg.receivedTime
  }));
  
  return res.status(200).json(results);
};

/**
 * Get a specific message by ID
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.getMessageById = (req, res) => {
  const messageId = parseInt(req.params.id);
  
  if (isNaN(messageId)) {
    return res.status(400).json({ error: 'Invalid message ID' });
  }
  
  const message = messages.find(msg => msg.id === messageId);
  
  if (!message) {
    return res.status(404).json({ error: 'Message not found' });
  }
  
  return res.status(200).json(message);
};

/**
 * Get counts of messages by message type
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.getMessageTypes = (req, res) => {
  const typeCounts = {};
  
  messages.forEach(msg => {
    const type = msg.messageType;
    typeCounts[type] = (typeCounts[type] || 0) + 1;
  });
  
  return res.status(200).json(typeCounts);
}; 