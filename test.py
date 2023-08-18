import socket
import sys
import pickle
from network_tools import send_data, recv_packets, ImageData

HOST, PORT = socket.gethostbyname(socket.gethostname()), 5555

filepath = ' '.join(sys.argv[1:])

with open(filepath, 'rb') as fb:
    data = ImageData(fb.read(), filepath.split('.')[-1])

# IPV4 & TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
    conn.connect((HOST, PORT))
    
    send_data(conn, data)
    
    try:
        received = recv_packets(conn)
    except TimeoutError:
        print('Server stopped.')
        quit()
    
    received = pickle.loads(received)
    if received:
        print('The file was moved successfully')
    else:
        print('Something went wrong')