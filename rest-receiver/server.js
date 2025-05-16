/**
 * HL7 REST API and MLLP Receiver
 * 
 * This is the main server file that starts both the REST API and MLLP server for receiving HL7 v2.3 messages.
 * It simulates the Medsynapse PACS Broker according to its conformance statement.
 */
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const winston = require('winston');
const path = require('path');
const fs = require('fs');

// Import routes and MLLP server
const hl7Routes = require('./src/routes/hl7Routes');
const mllpServer = require('./src/utils/mllpServer');

// Create Express app
const app = express();

// Set up logging
const logDir = path.join(__dirname, 'logs');
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir);
}

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  defaultMeta: { service: 'hl7-rest-receiver' },
  transports: [
    new winston.transports.File({ filename: path.join(logDir, 'error.log'), level: 'error' }),
    new winston.transports.File({ filename: path.join(logDir, 'combined.log') }),
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    })
  ],
});

// Middleware
app.use(helmet()); // Security headers
app.use(cors()); // Enable CORS
app.use(express.json({ limit: '10mb' })); // Parse JSON request bodies with a larger limit
app.use(express.urlencoded({ extended: true, limit: '10mb' })); // Parse URL-encoded request bodies
app.use(morgan('combined', { stream: { write: message => logger.info(message.trim()) } })); // HTTP request logging

// API key verification middleware
const verifyApiKey = (req, res, next) => {
  const apiKey = req.headers['x-api-key'];
  const expectedApiKey = process.env.API_KEY;
  
  // If no API key is set in the .env file, skip verification
  if (!expectedApiKey) {
    return next();
  }
  
  if (!apiKey || apiKey !== expectedApiKey) {
    logger.warn(`Unauthorized API request from ${req.ip}`);
    return res.status(401).json({ error: 'Unauthorized: Invalid API key' });
  }
  
  next();
};

// Routes
app.use('/api/hl7', verifyApiKey, hl7Routes);

// Home route
app.get('/', (req, res) => {
  res.json({
    message: 'HL7 REST Receiver API and MLLP Server',
    endpoints: {
      restApi: '/api/hl7',
      mllpServer: `${process.env.MLLP_HOST || 'localhost'}:${process.env.MLLP_PORT || 2575}`
    },
    version: '1.0.0',
    conformance: 'Medsynapse PACS v3.0.0.6'
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  logger.error(`${err.status || 500} - ${err.message} - ${req.originalUrl} - ${req.method} - ${req.ip}`);
  
  res.status(err.status || 500);
  res.json({
    error: {
      message: err.message,
      status: err.status || 500
    }
  });
});

// 404 handler
app.use((req, res) => {
  logger.warn(`404 - ${req.originalUrl} - ${req.method} - ${req.ip}`);
  res.status(404).json({
    error: {
      message: 'Resource not found',
      status: 404
    }
  });
});

// Start REST API server
const REST_PORT = process.env.PORT || 3000;
app.listen(REST_PORT, () => {
  logger.info(`REST API server running on port ${REST_PORT}`);
  console.log(`HL7 REST Receiver API listening on port ${REST_PORT}`);
  
  // After REST API is running, start MLLP server
  const MLLP_PORT = process.env.MLLP_PORT || 2575;
  mllpServer.startMLLPServer(MLLP_PORT, () => {
    logger.info(`MLLP server running on port ${MLLP_PORT}`);
    console.log(`HL7 MLLP server listening on port ${MLLP_PORT}`);
  });
}); 