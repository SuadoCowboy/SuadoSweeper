import socket
import pickle
from network_tools import *
import os

HOST, PORT = socket.gethostbyname(socket.gethostname()), 5555

username = input('Username: ')

# IPV4 & TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
	conn.connect((HOST, PORT))

	# first thing the client should send is his username.
	send_data(conn, username)

	username = recv_data(conn)
	if not username:
		print('Server stopped?')
		quit()
	
	username = pickle.loads(username)
	
	print('Commands:\n/file <path>')
	while True:
		try:
			message = input(f'{username}: ')
		except KeyboardInterrupt:
			break
		
		if message.startswith('/'):
			if len(message) == 1:
				continue
			
			message = message.split(' ', 1)
			if len(message) == 1:
				# commands that does not require arguments goes here
				command = message
			
			else: # commands that require arguments goes here
			
				command, arguments = message
				command = command[1:]
				
				if command == 'file':
					if not os.path.exists(arguments):
						print('Path does not exists')
						continue

					file_extension = os.path.splitext(arguments)[-1][1:]
					if not file_extension:
						print('Missing file extension')
						continue

					with open(arguments, 'rb') as fb:
						send_data(conn, FileData(fb.read(), file_extension, 'wb', 'rb'))

		else:
			data = MessageData(message, 'server')
			send_data(conn, data)

			result = recv_data(conn)

			if check(result, ClientNotFoundError):
				print(f'{data.receiver} not found')

		try:
			received = recv_data(conn)
		except TimeoutError:
			print('Server stopped')
			quit()
		
		received = pickle.loads(received)
		if not received:
			print('Oops! Something went wrong...')