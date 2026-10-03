import socket
import sys
import time

# --- CONFIGURATION ---
# Replace with your ESP32-S3's actual Wi-Fi IP address
ip = "10.0.0.151"  # Example IP address
port = 3333         # Must match dest_addr_ip4->sin_port in ESP-IDF
TIMEOUT_SEC = 5           # Seconds before giving up on a response
# ---------------------

def connect_to_esp32(message_to_send: str, ip, port):
    """
    Connects to the ESP32-S3 TCP server, sends a message, 
    and prints the echoed response.
    """
    l = len(message_to_send)
    tmp = b"CMD:" + l.to_bytes(2, byteorder='big') + message_to_send.encode('utf-8')
    print(tmp)

    print(f"Connecting to ESP32-S3 at {ip}:{port}...")
    
    # Create a standard TCP/IP socket
    # AF_INET = IPv4, SOCK_STREAM = TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        # Set a timeout so the script doesn't freeze if the ESP32 is offline
        client_socket.settimeout(TIMEOUT_SEC)
        
        try:
            # Establish connection
            client_socket.connect((ip, port))
            print("Connected successfully!")
            
            # Send data (strings must be encoded to bytes over network sockets)
            print(f"Sending: '{message_to_send}'")
            client_socket.sendall(tmp)
            
            # Receive data back from the echo server
            # 1024 bytes is standard; matches or exceeds the ESP32 rx_buffer size
            response_bytes = client_socket.recv(1024)
            
            if not response_bytes:
                print("Server closed the connection without data.")
                return

            response_str = response_bytes.decode('utf-8')
            print(f"Received from ESP32: '{response_str}'")
            
        except socket.timeout:
            print(f"Error: Connection timed out after {TIMEOUT_SEC} seconds.")
        except ConnectionRefusedError:
            print("Error: Connection refused. Is the server running on the ESP32?")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            print("Socket closed.\n")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("USAGE: {} <ip> <port> <MSG>".format(sys.argv[0]))
    else:
        connect_to_esp32(sys.argv[3],sys.argv[1], int(sys.argv[2]))

