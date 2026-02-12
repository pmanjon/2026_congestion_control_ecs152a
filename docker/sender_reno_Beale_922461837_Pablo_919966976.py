# Quick explanation
# TCP reno, starts with a slow start, 
# figures out the threshold when packet is dropped
# then divides window size by 2
# makes the threshold == current window size
# starts additive increase from the reduced window size
# TCP reno can not track multiple transmission errors(partial ACKS)

import socket
from timeit import default_timer as timer
# measurements aren't done
Throughputs =       []
totalPacketDelays = [] 
Performances =      []

def avgTime(someList):
    avgThing = 0.0 
    for time in someList:
        avgThing += time
    avgThing /= len(someList)
    return avgThing


PACKET_SIZE = 1024
SEQ_ID_SIZE = 4 
MESSAGE_SIZE = PACKET_SIZE - SEQ_ID_SIZE 
port_num = 5001

#for evaluating performance set the initial window size = 1 packet and the initial slow start threshold to 64 packets
startThroughput = 0.0
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket, \
     open('file.mp3', 'rb') as mp3:

     data = mp3.read()

     startThroughput = timer()
     address, _ = udp_socket.getsockname()
     udp_socket.connect((address, port_num))
     udp_socket.settimeout(0.5) # timeout for half a sec 
     last_ack = 0 # last acknowledge
     seq_id = 0
     command_win_size = 1
     ssthreshold = 64
     fast_recover = False
     while seq_id < len(data):
          print(seq_id, command_win_size, ssthreshold)
          # make messages
          messages = []
          for _ in range(command_win_size):
               messages.append(seq_id.to_bytes(SEQ_ID_SIZE, byteorder='big', signed=True) + data[seq_id: seq_id + MESSAGE_SIZE])
               seq_id += MESSAGE_SIZE

          # send messages
          for i in range(command_win_size):
               udp_socket.send(messages[i])

          # recieve acknowledgements
          # the while condition is to take care of any outstanding packets.
          dup_ack_count = 0
          while last_ack < seq_id:
               try:
                    newdata, _ = udp_socket.recvfrom(PACKET_SIZE)
                    cur_ack = int.from_bytes(newdata[:SEQ_ID_SIZE], byteorder='big', signed=True)
                    # duplicate acks
                    if cur_ack == last_ack:
                         dup_ack_count += 1

                         # sends the dropped packet, only happens for the 3rd duplicate, other duplicate returns are ignored since it was transmitted 
                         if dup_ack_count == 3:
                              command_win_size = int(command_win_size + 3)
                              # in case that the last_ack is NOT in the current window
                              fast_message = last_ack.to_bytes(SEQ_ID_SIZE, byteorder='big', signed=True) + data[last_ack: last_ack + MESSAGE_SIZE]
                              udp_socket.send(fast_message)
                    elif cur_ack == last_ack and fast_recover:
                         # send a new message and see if the acknowledgement is actually new
                         command_win_size += 1
                         fast_message = seq_id.to_bytes(SEQ_ID_SIZE,byteorder='big', signed=True) + data[seq_id: seq_id + MESSAGE_SIZE]
                         seq_id += MESSAGE_SIZE
                    elif last_ack < cur_ack:
                         last_ack = max(cur_ack, last_ack)
                         dup_ack_count = 0
                         if fast_recover:
                              # command_win_size = ssthreshold
                              fast_recover = False
                    else:
                         last_ack = max(cur_ack, last_ack)
                         dup_ack_count = 0


               except socket.timeout:
                    # if timeout do slow start 
                    ssthreshold = max(int(command_win_size // 2), 1) # must be at least 1
                    command_win_size = ssthreshold
                    break # if no break, will be stuck in a stop and wait situation
          
          # Either still in slow start or in additive increase 
          if command_win_size < ssthreshold:
               command_win_size = min(ssthreshold, (command_win_size * 2) )  
          else:
               command_win_size += 1 # arbitrary choice for now



     num = 0
     msg = num.to_bytes(length=SEQ_ID_SIZE, byteorder='big') + bytes('==FINACK==', 'utf-8')
     udp_socket.send(msg)
endThroughput = timer()

print("Throughput", endThroughput-startThroughput)
print("Done")