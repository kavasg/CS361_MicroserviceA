import zmq
import random
import os
from typing import Tuple

class KeyGeneratorService:
    """
    A microservice that generates random keys for one-time pad encryption.
    Communicates with the main program using ZeroMQ.
    """
    def __init__(self, port: int = 5555):
        """Initialize ZeroMQ context and socket"""
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{port}")
        
    def generate_key(self, length: int) -> str:
        """
        Generate a random key of specified length using ASCII printable characters (32-126)
        
        Args:
            length: The required length of the key
            
        Returns:
            A string of random printable ASCII characters
        """
        return ''.join(chr(random.randint(32, 126)) for _ in range(length))
    
    def save_key(self, key: str, filename: str) -> None:
        """
        Save the generated key to a file
        
        Args:
            key: The generated key string
            filename: Name of the file to save the key to
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(key)
            
    def get_file_length(self, filename: str) -> int:
        """
        Get the length of the input file
        
        Args:
            filename: Name of the file to measure
            
        Returns:
            Length of the file in characters
        """
        with open(filename, 'r', encoding='utf-8') as f:
            return len(f.read())
            
    def process_request(self, request: str) -> Tuple[str, str]:
        """
        Process an incoming file request and generate appropriate key
        
        Args:
            request: The filename to generate a key for
            
        Returns:
            Tuple of (status message, key filename)
        """
        try:
            # Get length of input file
            file_length = self.get_file_length(request)
            
            # Generate key filename
            key_filename = f"key_{os.path.splitext(os.path.basename(request))[0]}.txt"
            
            # Generate and save key
            key = self.generate_key(file_length)
            self.save_key(key, key_filename)
            
            return "success", key_filename
            
        except FileNotFoundError:
            return "error", "Input file not found"
        except Exception as e:
            return "error", f"Error generating key: {str(e)}"
    
    def run(self):
        """
        Main service loop - continuously listen for requests and process them
        """
        print("Key Generator Service is running...")
        while True:
            try:
                # Wait for next request from client
                filename = self.socket.recv_string()
                print(f"Received request for file: {filename}")
                
                # Process the request
                status, response = self.process_request(filename)
                
                # Send response back to client
                self.socket.send_multipart([
                    status.encode('utf-8'),
                    response.encode('utf-8')
                ])
                
            except Exception as e:
                print(f"Error processing request: {str(e)}")
                self.socket.send_multipart([
                    b"error",
                    str(e).encode('utf-8')
                ])

if __name__ == "__main__":
    service = KeyGeneratorService()
    service.run()