import socket
from datetime import datetime

def start_server(host='0.0.0.0', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Listening on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'received_image_{timestamp}.jpg'

        with open(filename, 'wb') as file:
            print(f"Receiving data for {filename}...")
            data = client_socket.recv(4096)
            while data:
                file.write(data)
                data = client_socket.recv(4096)

        print(f"Received and saved {filename}")
        client_socket.close()

start_server()
