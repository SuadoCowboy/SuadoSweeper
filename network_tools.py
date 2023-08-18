import socket
import pickle

class BaseData:
	"""
	Base class for the datas that will be sent to a client/server
	"""
	def __init__(self, content: bytes):
		self.content = content
		self.write_mode = 'w'

class ImageData(BaseData):
	def __init__(self, content: bytes, type: str):
		super().__init__(content)
		
		self.type = type
		self.write_mode = 'wb'

def send_data(conn: socket.socket, data):
	data = pickle.dumps(data)

	conn.sendall(pickle.dumps(len(data)))
	conn.sendall(data)

def recv_packets(conn: socket.socket):
	data_size = conn.recv(128)
	if not data_size: raise socket.timeout('data size is empty')

	data_size = pickle.loads(data_size)
	
	data = bytes()

	while data_size > 0:
		packet = conn.recv(4096)
		if not packet: raise socket.timeout('server sent an empty packet')
		
		data += packet
		data_size -= 4096
	
	return data