# Key Generator Microservice

A microservice that generates random keys for one-time pad encryption. This service receives file names via ZeroMQ, generates appropriate-length random keys using ASCII printable characters (32-126), and saves them to files.

## Installation Requirements

1. Python 3.7 or higher
2. PyZMQ library

Install the required dependencies:
```bash
pip install pyzmq
```

### Step-by-Step Installation

1. First, check your Python version:
```bash
python --version
```

2. (Optional but recommended) Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install the required package:
```bash
pip install -r requirements.txt
```

If you encounter permission errors:
```bash
sudo pip install pyzmq
```

### Verify Installation
```python
# Run Python and try:
import zmq
print(zmq.pyzmq_version())
```

## Setup Instructions

1. Clone this repository or download the source files
2. Ensure all files are in your working directory
3. Start the key generator service:
```bash
python key_generator_service.py
```

## Communication Contract

### How to Request Data

The microservice accepts requests via ZeroMQ on port 5555. Send a string containing the input filename for which you need a key generated.

Example request code:
```python
import zmq

# Setup ZeroMQ context and socket
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

# Send the filename
input_filename = "message.txt"
socket.send_string(input_filename)
```

### How to Receive Data

The service responds with two parts:
1. Status: "success" or "error"
2. Response: Either the key filename or error message

Example receiving code:
```python
# Receive the response
status, response = socket.recv_multipart()
status = status.decode('utf-8')
response = response.decode('utf-8')

if status == "success":
    key_filename = response
    print(f"Key saved to: {key_filename}")
else:
    error_message = response
    print(f"Error: {error_message}")
```

### UML Sequence Diagram

```mermaid
sequenceDiagram
    participant C as Client Program
    participant K as Key Generator Service
    participant FS as File System
    
    C->>+K: Send filename (ZMQ REQ)
    K->>+FS: Check if file exists
    FS-->>-K: File status
    
    alt File exists
        K->>+FS: Read file length
        FS-->>-K: File length
        K->>K: Generate random key
        K->>+FS: Save key to file
        FS-->>-K: Save confirmation
        K-->>-C: Send success + key filename
    else File not found
        K-->>C: Send error + error message
    end
```

## Error Handling

The service handles several types of errors:
1. File not found
2. Permission errors when reading/writing files
3. Invalid file formats
4. Network communication errors

Error responses will include descriptive messages to help diagnose issues.

## Key Generation Details

- Keys are generated using Python's random.randint()
- Characters are in the ASCII printable range (32-126)
- Key length matches input file length exactly
- Keys are saved in the same directory as the program
- Key filenames are generated as: "key_[original_filename].txt"

## File Management

- All generated key files are stored in the same directory as the program
- Files are automatically named based on the input filename
- Existing files with the same name will be overwritten
- UTF-8 encoding is used for all file operations

## Usage Example

1. Start the service:
```bash
python key_generator_service.py
```

2. In your client code:
```python
import zmq

def request_key(filename):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    
    socket.send_string(filename)
    status, response = socket.recv_multipart()
    
    status = status.decode('utf-8')
    response = response.decode('utf-8')
    
    return status, response

# Example usage
status, response = request_key("message.txt")
if status == "success":
    print(f"Key generated and saved to: {response}")
else:
    print(f"Error: {response}")
```

## Troubleshooting

Common issues and solutions:

1. "Address already in use" error:
   - Another instance of the service is running
   - Wait a few seconds and try again, or use a different port

2. "Connection refused" error:
   - Service is not running
   - Check if service is started on the correct port

3. "File not found" error:
   - Verify the input file exists
   - Check file path is correct
   - Ensure proper file permissions

## Testing

Run the included test program to verify the service is working:
```bash
python test_key_generator.py
```

The test program will:
1. Create a test input file
2. Request a key
3. Display the results