import socketserver
from socket import gethostbyname, gethostname
from network_tools import send_data, recv_packets
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

class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            data = recv_packets(self.request)
        except TimeoutError:
            print(f'{self.client_address} disconnected.')
            return
        try:
            data = pickle.loads(data)

            print('received:', type(data), 'from:', self.client_address)
            
            filename = f'output.{data.type}'
            i = 0
            while os.path.exists(filename):
                i += 1
                filename = f'output({i}).{data.type}'
            
            print('creating file:', filename)
            
            with open(filename, data.write_mode) as f:
                f.write(data.content)

            print('file created.')
        except Exception as e:
            print(e)
            send_data(self.request, False)
            return
        
        send_data(self.request, True)

with socketserver.TCPServer(ADDR, TCPHandler) as server:
    print('Started server')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

print('Finished program')