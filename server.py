import socketserver
from socket import gethostbyname, gethostname
from network_tools import *
from configparser import ConfigParser
import pickle
import os

config = ConfigParser()

'''def convert_to_bool(value: str):
	if value == '0' or value.lower() == 'false' or not bool(value):
		return False
	
	if value == '1' or value.lower() == 'true':
		return True
	
	return None'''

CONFIG_PATH = 'server.ini'
if os.path.exists(CONFIG_PATH):
	config.read(CONFIG_PATH)
else:

	config['SERVER'] = {'port':'5555'}

	with open(CONFIG_PATH, 'w') as configfile:
		config.write(configfile)

HOST = gethostbyname(gethostname())
PORT = int(config['SERVER']['port'])
ADDR = (HOST, PORT)

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
	def handle(self):
		print(self.client_address, 'connected')

		try:
			self.client_username = recv_data(self.request)
		except TimeoutError:
			print(f'{self.client_address} disconnected.')
		
		username = self.client_username = pickle.loads(self.client_username)
		
		i = 1
		while find_sublist_by_variable(self.server.clients, username):
			username = f'{self.client_username}({i})'
			i += 1
		
		if username != self.client_username:
			print(f'{self.client_username} is already taken, new username:', username)
			self.client_username = username
		
		send_data(self.request, self.client_username)
		
		find_sublist_by_variable(self.server.clients, self.client_address).append(self.client_username)

		while True:
			went_wrong = False
			
			# receive data
			try:
				data = recv_data(self.request)
			except (TimeoutError, ConnectionResetError):
				print(f'{self.client_username} disconnected.')
				return
			
			# handle data
			try:
				data = pickle.loads(data)
				
				if type(data) == MessageData:
					data.sender = self.client_username
					
					if data.receiver in ('server', None):
						print(f'{data.sender}: {data.content}')
						send_data(self.request, True)

						if not data.receiver: # TODO: make it work(clients only sends and doesn't receive)
							for client in self.server.clients:
								send_data(client[0], data)
					
					elif data.receiver: # FUTURE TODO: test this part of code(send message to a specific person)
						receiver = find_sublist_by_variable(self.server.clients, data.receiver)[0]
						
						if not receiver:
							send_data(self.request, ClientNotFoundError)
						
						else:
							send_data(receiver, data)

				elif type(data) == FileData:
					filename = f'output.{data.type}'
					
					i = 0
					while os.path.exists(filename):
						i += 1
						filename = f'output({i}).{data.type}'
					
					with open(filename, data.write_mode) as f:
						f.write(data.content)

			except Exception as e:
				print(type(e), e)
				went_wrong = True
			
			send_data(self.request, not went_wrong) # sends "ok" or "not ok" to client

class ThreadedTCPServer(socketserver.ThreadingTCPServer):
	def __init__(self, server_address, RequestHandlerClass, bind_and_activate: bool=True):
		super().__init__(server_address, RequestHandlerClass, bind_and_activate)
		self.clients = []

	def get_request(self):
		request, address = super().get_request()
		self.clients.append([request, address])
		return request, address

with ThreadedTCPServer(ADDR, ThreadedTCPRequestHandler) as server:
	print('Started server')
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		pass

print('Finished program')