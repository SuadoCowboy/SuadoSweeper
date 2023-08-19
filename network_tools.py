import socket
import pickle

PACKET_BUFSIZE = 4096
DATA_SIZE_BUFSIZE = 128
OK_BUFSIZE = 4

class BaseData:
	"""
	Base class for the datas that will be sent to a client/server
	"""
	def __init__(self, content):
		self.content = content

class MessageData(BaseData):
	def __init__(self, content: str, receiver: str=None):
		super().__init__(content)

		"""
		if receiver is None it sends to everyone
		if receiver is server it sends to the server only
		"""

		self.receiver = receiver
		self.sender = ''

class FileData(BaseData):
	def __init__(self, content: bytes, type: str, write_mode: str='w', read_mode: str='r'):
		super().__init__(content)
		
		self.type = type
		self.write_mode = write_mode
		self.read_mode = read_mode

class ClientNotFoundError(BaseException):
	def __init__(self, client: str='Client', *args: object) -> None:
		if not args:
			args = [f'{client} does not exists in clients list.']
		super().__init__(*args)

def send_data(conn: socket.socket, data):
	data = pickle.dumps(data)

	data_size = len(data)

	conn.sendall(pickle.dumps(data_size))
	
	if check(conn.recv(OK_BUFSIZE), True):
		conn.sendall(data)

def recv_data(conn: socket.socket):
	data_size = conn.recv(DATA_SIZE_BUFSIZE)
	if not data_size: raise socket.timeout('data size is empty')

	conn.sendall(pickle.dumps(True))

	data_size = pickle.loads(data_size)
	
	data = bytes()
	while data_size > 0:
		packet = conn.recv(PACKET_BUFSIZE)
		if not packet: raise socket.timeout('received an empty packet')
		
		data += packet
		data_size -= PACKET_BUFSIZE
	
	return data

def check(data, to_check):
	"""
	<data> must be a data that came from the connection,
	if <data> is not empty and is equals <to_check>, it returns True
	"""
	return True if data and pickle.loads(data) == to_check else False

def find_sublist_by_variable(iterable: list | tuple | dict, variable):
	for item in iterable:
		if variable in item:
			return item