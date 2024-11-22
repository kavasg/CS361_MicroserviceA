import zmq
import time

def test_key_generator():
    """Test program to demonstrate key generator service usage"""
    # Setup ZeroMQ context and socket
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    
    # Create a test file
    test_filename = "test_input.txt"
    with open(test_filename, 'w', encoding='utf-8') as f:
        f.write("This is a test message that needs encryption.")
    
    # Send request to key generator service
    print(f"Requesting key generation for file: {test_filename}")
    socket.send_string(test_filename)
    
    # Get response
    status, key_filename = socket.recv_multipart()
    status = status.decode('utf-8')
    key_filename = key_filename.decode('utf-8')
    
    if status == "success":
        print(f"Key generated successfully!")
        print(f"Key saved to: {key_filename}")
        
        # Display the generated key
        with open(key_filename, 'r', encoding='utf-8') as f:
            key = f.read()
            print(f"Generated key (first 50 chars): {key[:50]}...")
    else:
        print(f"Error: {key_filename}")

if __name__ == "__main__":
    test_key_generator()