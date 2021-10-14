import socket

print('Getting an available port')
_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
_socket.bind(('localhost', 0))
_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
available_port: int = _socket.getsockname()[1]
_socket.close()
