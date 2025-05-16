/**
 * MLLP Server Implementation
 * 
 * This module implements the Minimal Lower Layer Protocol (MLLP) for HL7 message exchange
 * as specified in the Medsynapse PACS conformance statement.
 */
const net = require('net');
const hl7Parser = require('./hl7Parser');
const winston = require('winston');
const path = require('path');
const fs = require('fs');

// MLLP control characters
const VT = 0x0b;  // <VT> Start of block
const FS = 0x1c;  // <FS> End of block
const CR = 0x0d;  // <CR> End of block

// Create a logger specific for MLLP server
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  defaultMeta: { service: 'mllp-server' },
  transports: [
    new winston.transports.File({ 
      filename: path.join(__dirname, '../../../logs/mllp-error.log'), 
      level: 'error' 
    }),
    new winston.transports.File({ 
      filename: path.join(__dirname, '../../../logs/mllp-combined.log') 
    }),
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    })
  ],
});

/**
 * Process an incoming HL7 message and generate an acknowledgment
 * @param {Buffer} message - The received HL7 message as a buffer
 * @returns {Object} An object containing the parsed message and the ACK message
 */
function processHL7Message(message) {
  try {
    // Convert buffer to string
    const messageStr = message.toString('utf8');
    
    // Parse the HL7 message
    const parsedMessage = hl7Parser.parseHL7(messageStr);
    
    if (!parsedMessage) {
      logger.error('Failed to parse HL7 message');
      return {
        success: false,
        errorText: 'Failed to parse HL7 message'
      };
    }
    
    // Save the received message to storage
    const storageDir = path.join(__dirname, '../../../storage');
    if (!fs.existsSync(storageDir)) {
      fs.mkdirSync(storageDir, { recursive: true });
    }
    
    // Create a filename based on message type and timestamp
    const timestamp = new Date().toISOString().replace(/[-:]/g, '').replace('T', '_').split('.')[0];
    let messageType = parsedMessage.messageType || 'UNKNOWN';
    if (parsedMessage.triggerEvent) {
      messageType += `_${parsedMessage.triggerEvent}`;
    }
    
    const filename = `${timestamp}_${messageType}.hl7`;
    fs.writeFileSync(path.join(storageDir, filename), messageStr);
    
    // Generate the acknowledgment
    const ackMessage = hl7Parser.generateAcknowledgment(parsedMessage);
    
    // Log success
    logger.info(`Processed ${messageType} message successfully`);
    
    return {
      success: true,
      parsedMessage,
      acknowledgment: ackMessage
    };
  } catch (err) {
    logger.error(`Error processing HL7 message: ${err.message}`);
    return {
      success: false,
      errorText: err.message
    };
  }
}

/**
 * Start the MLLP server
 * @param {number} port - The port to listen on
 * @param {function} callback - Callback function when server is started
 * @returns {net.Server} The server instance
 */
function startMLLPServer(port, callback) {
  // Create TCP server
  const server = net.createServer((socket) => {
    logger.info(`New client connected: ${socket.remoteAddress}:${socket.remotePort}`);
    
    let messageBuffer = Buffer.alloc(0);
    let messageStarted = false;
    
    // Handle data from client
    socket.on('data', (data) => {
      logger.debug(`Received data from ${socket.remoteAddress}:${socket.remotePort}`);
      
      for (let i = 0; i < data.length; i++) {
        const byte = data[i];
        
        // Check for start of message (VT)
        if (byte === VT && !messageStarted) {
          messageStarted = true;
          messageBuffer = Buffer.alloc(0); // Reset buffer
          continue;
        }
        
        // Check for end of message (FS CR)
        if (byte === FS && messageStarted && i + 1 < data.length && data[i + 1] === CR) {
          // Process complete message
          const result = processHL7Message(messageBuffer);
          
          if (result.success) {
            // Send ACK message
            const ackBuffer = Buffer.concat([
              Buffer.from([VT]),
              Buffer.from(result.acknowledgment),
              Buffer.from([FS, CR])
            ]);
            socket.write(ackBuffer);
            logger.info('Sent acknowledgment message');
          } else {
            // Send NAK message
            const nakMessage = `MSH|^~\\&|PACS_APP|PACS_FACILITY|${result.parsedMessage?.sendingApplication || 'UNKNOWN'}|${result.parsedMessage?.sendingFacility || 'UNKNOWN'}|${new Date().toISOString().replace(/[-:T]/g, '')}||ACK|NAK${Date.now()}|P|2.3\rMSA|AE|${result.parsedMessage?.messageControlId || 'UNKNOWN'}|${result.errorText}`;
            const nakBuffer = Buffer.concat([
              Buffer.from([VT]),
              Buffer.from(nakMessage),
              Buffer.from([FS, CR])
            ]);
            socket.write(nakBuffer);
            logger.warn(`Sent negative acknowledgment: ${result.errorText}`);
          }
          
          // Reset message state
          messageStarted = false;
          i++; // Skip CR
          continue;
        }
        
        // Append to message if collecting
        if (messageStarted) {
          messageBuffer = Buffer.concat([messageBuffer, Buffer.from([byte])]);
        }
      }
    });
    
    // Handle client disconnect
    socket.on('end', () => {
      logger.info(`Client disconnected: ${socket.remoteAddress}:${socket.remotePort}`);
    });
    
    // Handle errors
    socket.on('error', (err) => {
      logger.error(`Socket error: ${err.message}`);
    });
  });
  
  // Start server
  server.listen(port, () => {
    logger.info(`MLLP server listening on port ${port}`);
    if (callback) callback();
  });
  
  // Handle server errors
  server.on('error', (err) => {
    logger.error(`Server error: ${err.message}`);
    if (err.code === 'EADDRINUSE') {
      logger.error(`Port ${port} is already in use`);
    }
  });
  
  return server;
}

module.exports = {
  startMLLPServer
}; 