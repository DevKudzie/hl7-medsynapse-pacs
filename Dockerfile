FROM node:18-alpine

# Install Python and pip
RUN apk add --no-cache python3 py3-pip

# Set working directory
WORKDIR /app

# Copy package.json and install Node.js dependencies
COPY rest-receiver/package.json /app/rest-receiver/
RUN cd /app/rest-receiver && npm install

# Copy Python requirements and install dependencies
COPY hl7-sender/requirements.txt /app/hl7-sender/
RUN cd /app/hl7-sender && pip3 install -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Create .env files from examples
RUN cd /app/hl7-sender && cp env.example .env
RUN cd /app/rest-receiver && cp env.example .env

# Expose ports
EXPOSE 3000 5000

# Add entrypoint script
COPY start.sh /app/
RUN chmod +x /app/start.sh

# Set entrypoint
ENTRYPOINT ["/app/start.sh"] 