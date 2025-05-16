FROM node:18-alpine

# Install Python and pip
RUN apk add --no-cache python3 py3-pip

# Set working directory
WORKDIR /app

# Copy package.json files for both Node.js apps
COPY rest-receiver/package.json /app/rest-receiver/
COPY web-interface/package.json /app/web-interface/

# Install Node.js dependencies for both apps
RUN cd /app/rest-receiver && npm install
RUN cd /app/web-interface && npm install

# Copy Python requirements and install dependencies in a virtual environment
COPY hl7-sender/requirements.txt /app/hl7-sender/
RUN cd /app/hl7-sender && \
    python3 -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip && \
    /app/venv/bin/pip install -r requirements.txt

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