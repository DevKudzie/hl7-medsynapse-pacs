/**
 * HL7 Routes
 * 
 * This file defines the API routes for receiving HL7 messages.
 */
const express = require('express');
const router = express.Router();
const hl7Controller = require('../controllers/hl7Controller');

/**
 * @route POST /api/hl7
 * @desc Receive an HL7 message
 * @access Private
 */
router.post('/', hl7Controller.receiveMessage);

/**
 * @route GET /api/hl7/messages
 * @desc Get all received messages
 * @access Private
 */
router.get('/messages', hl7Controller.getMessages);

/**
 * @route GET /api/hl7/messages/:id
 * @desc Get a specific message by ID
 * @access Private
 */
router.get('/messages/:id', hl7Controller.getMessageById);

/**
 * @route GET /api/hl7/types
 * @desc Get counts of messages by message type
 * @access Private
 */
router.get('/types', hl7Controller.getMessageTypes);

module.exports = router; 