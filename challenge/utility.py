import socket

def get_free_port(START_PORT, END_PORT, HOST="localhost"):
    for port in range(START_PORT, END_PORT):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex((HOST, port))
            if result == 111:
                print(f"Port {port} is avilable")
                return port
    return None
