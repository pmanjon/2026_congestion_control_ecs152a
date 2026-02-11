import socket

command_win_size = 1
PACKET_SIZE = 1024
SEQ_ID_SIZE = 4 
port_num = 5001

#for evaluating performance set the initial window size = 1 packet and the initial slow start threshold to 64 packets

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket, \
     open('docker/file.mp3', 'rb') as mp3:

     address, _ = udp_socket.getsockname()
     udp_socket.connect((address, port_num))


     num = 0
     msg = num.to_bytes(length=SEQ_ID_SIZE, byteorder='big') + bytes('==FINACK==', 'utf-8')
     udp_socket.send(msg)