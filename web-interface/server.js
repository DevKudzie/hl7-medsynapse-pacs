const express = require('express');
const axios = require('axios');
const path = require('path');
const fs = require('fs');
const morgan = require('morgan');
const cors = require('cors');
const { spawn } = require('child_process');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(morgan('dev'));
app.use(express.static(path.join(__dirname, 'public')));

// Determine appropriate HL7 API endpoint - in Docker, localhost refers to the container itself
const isDocker = fs.existsSync('/.dockerenv') || fs.existsSync('/app/venv');
const HL7_API_ENDPOINT = process.env.HL7_API_ENDPOINT || 
                        (isDocker ? 'http://localhost:3000/api/hl7' : 'http://localhost:3000/api/hl7');

console.log(`Using HL7 API endpoint: ${HL7_API_ENDPOINT}`);

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// API route to handle HL7 message generation
app.post('/api/generate', (req, res) => {
  const { count, type } = req.body;
  const outputFile = path.join(__dirname, '..', 'hl7-sender', 'generated_messages.txt');
  
  // Get Python executable path (use virtual env in Docker, regular python otherwise)
  const pythonPath = fs.existsSync('/app/venv/bin/python') 
    ? '/app/venv/bin/python'
    : 'python3';
  
  // Spawn python process to generate messages
  const pythonProcess = spawn(pythonPath, [
    path.join(__dirname, '..', 'hl7-sender', 'generate_hl7.py'),
    '--count', count || '5',
    '--type', type || 'ALL',
    '--output', outputFile
  ]);
  
  let output = '';
  let errorOutput = '';
  
  pythonProcess.stdout.on('data', (data) => {
    output += data.toString();
  });
  
  pythonProcess.stderr.on('data', (data) => {
    errorOutput += data.toString();
  });
  
  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      return res.status(500).json({ error: errorOutput || 'Error generating HL7 messages' });
    }
    
    // Read the generated file
    fs.readFile(outputFile, 'utf8', (err, data) => {
      if (err) {
        return res.status(500).json({ error: 'Error reading generated HL7 messages' });
      }
      
      // Split into individual messages
      const messages = data.split('\n\n').filter(msg => msg.trim());
      
      res.json({
        success: true,
        message: `Generated ${messages.length} HL7 messages`,
        messageCount: messages.length,
        messages: messages
      });
    });
  });
});

// API route to send a message to the HL7 API
app.post('/api/send', async (req, res) => {
  const { message } = req.body;
  
  if (!message) {
    return res.status(400).json({ error: 'No message provided' });
  }
  
  try {
    // Encode message to base64
    const encodedMessage = Buffer.from(message).toString('base64');
    
    // Extract message type for logging
    const messageLines = message.split('\n');
    let messageType = 'Unknown';
    
    if (messageLines && messageLines[0].startsWith('MSH|')) {
      const mshFields = messageLines[0].split('|');
      if (mshFields.length > 9) {
        messageType = mshFields[8];
      }
    }
    
    // Prepare request payload
    const payload = {
      message: encodedMessage,
      messageType: messageType,
      sendTime: new Date().toISOString()
    };
    
    // Send to HL7 API
    const response = await axios.post(HL7_API_ENDPOINT, payload, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    res.json({
      success: true,
      response: response.data
    });
    
  } catch (error) {
    console.error('Error sending HL7 message:', error);
    res.status(500).json({
      error: 'Error sending HL7 message',
      details: error.response ? error.response.data : error.message
    });
  }
});

// API route to get received messages
app.get('/api/messages', async (req, res) => {
  try {
    const response = await axios.get(`${HL7_API_ENDPOINT}/messages`);
    res.json(response.data);
  } catch (error) {
    console.error('Error fetching messages:', error);
    res.status(500).json({
      error: 'Error fetching messages',
      details: error.response ? error.response.data : error.message
    });
  }
});

// API route to get message by ID
app.get('/api/messages/:id', async (req, res) => {
  try {
    const messageId = req.params.id;
    const response = await axios.get(`${HL7_API_ENDPOINT}/messages/${messageId}`);
    res.json(response.data);
  } catch (error) {
    console.error(`Error fetching message with ID ${req.params.id}:`, error);
    res.status(500).json({
      error: `Error fetching message with ID ${req.params.id}`,
      details: error.response ? error.response.data : error.message
    });
  }
});

// API route to get message types
app.get('/api/messages/types', async (req, res) => {
  try {
    const response = await axios.get(`${HL7_API_ENDPOINT}/types`);
    res.json(response.data);
  } catch (error) {
    console.error('Error fetching message types:', error);
    res.status(500).json({
      error: 'Error fetching message types',
      details: error.response ? error.response.data : error.message
    });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`HL7 Web Interface running on port ${PORT}`);
}); 