/**
 * HL7 REST API Receiver
 * 
 * This is the main server file for the REST API that receives HL7 v2.3 messages.
 */
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const winston = require('winston');
const path = require('path');
const fs = require('fs');

// Import routes
const hl7Routes = require('./src/routes/hl7Routes');

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
    message: 'HL7 REST Receiver API',
    endpoints: {
      hl7: '/api/hl7'
    },
    version: '1.0.0'
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

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  logger.info(`Server running on port ${PORT}`);
  console.log(`HL7 REST Receiver API listening on port ${PORT}`);
}); 