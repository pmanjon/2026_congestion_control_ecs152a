# Quick explanation
# TCP reno, starts with a slow start, 
# figures out the threshold when packet is dropped
# then divides window size by 2
# makes the threshold == current window size
# starts additive increase from the reduced window size
# TCP reno can not track multiple transmission errors(partial ACKS)

import socket
from timeit import default_timer as timer
from sortedcontainers import SortedDict # just to keep track of not skipped over acknowledgements

def avgTime(someList):
    avgThing = 0.0 
    for time in someList:
        avgThing += time
    avgThing /= len(someList)
    return avgThing

def resendLast(lastACKED: int, cur_socket: socket.socket, dataLength : int):
     #send more messagess because we expect that the lost packet is recovered
     messages_left = min(MESSAGE_SIZE, dataLength - lastACKED)
     fast_message = last_ack.to_bytes(SEQ_ID_SIZE, byteorder='big', signed=True) + data[lastACKED: lastACKED + messages_left]
     cur_socket.sendto(fast_message, ("localhost", 5001))
     return True
PACKET_SIZE = 1024
SEQ_ID_SIZE = 4 
MESSAGE_SIZE = PACKET_SIZE - SEQ_ID_SIZE 
port_num = 5000

PacketDelays = SortedDict({0:[0,0]}) # seq_id : [start_timer, end_timer]
#for evaluating performance set the initial window size = 1 packet and the initial slow start threshold to 64 packets
startThroughput = 0.0
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket, \
     open('file.mp3', 'rb') as mp3:

     data = mp3.read()

     startThroughput = timer()
     udp_socket.bind(("localhost", port_num))
     udp_socket.settimeout(0.5) # timeout for half a sec 
     last_ack = 0 # last acknowledge
     seq_id = 0
     command_win_size = 1
     ssthreshold = 64
     fast_recover = False
     while seq_id < len(data):
          #print(len(data), seq_id, command_win_size, ssthreshold)
          # make messages
          messages = []
          for _ in range(command_win_size):
               messages_left = min(MESSAGE_SIZE, len(data) - seq_id)
               if(messages_left <= 0):
                    break
               messages.append(seq_id.to_bytes(SEQ_ID_SIZE, byteorder='big', signed=True) + data[seq_id: seq_id + messages_left])
               seq_id += messages_left
               PacketDelays[seq_id] = [0.0,0.0]

          # send messages
          for i in range(len(messages)):
               PacketDelays[int.from_bytes(messages[i][:SEQ_ID_SIZE],byteorder='big',signed=True)][0] = timer()
               udp_socket.sendto(messages[i], ("localhost", 5001))

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
                              resendLast(last_ack, udp_socket, len(data))
                         elif dup_ack_count > 3:
                              # fast recovery
                              command_win_size += 1
                              #send more messagess because we expect that the lost packet is recovered
                              messages_left = min(MESSAGE_SIZE, len(data) - seq_id)
                              if(messages_left <= 0): # no knew messages to send past message
                                   resendLast(last_ack, udp_socket, len(data))
                                   continue
                              fast_message = seq_id.to_bytes(SEQ_ID_SIZE, byteorder='big', signed=True) + data[seq_id: seq_id + messages_left]
                              PacketDelays[seq_id] = [timer(), 0.0]
                              udp_socket.sendto(fast_message, ("localhost", 5001))
                    else:
                         PacketDelays[cur_ack][1] = timer() # end time for packet
                         last_ack = cur_ack
                         dup_ack_count = 0
                         if fast_recover:
                              # command_win_size = ssthreshold
                              fast_recover = False

               except socket.timeout:
                    # if timeout do slow start 
                    ssthreshold = max(int(command_win_size // 2), 1) # must be at least 1
                    command_win_size = ssthreshold
                    break
                    # if time out must send last packet to ensure that there is 
                    resendLast(last_ack, udp_socket, len(data))
          # Either still in slow start or in additive increase 
          if command_win_size < ssthreshold:
               command_win_size = min(ssthreshold, (command_win_size * 2) )  
          else:
               command_win_size += 1 # arbitrary choice for now
          


     # final message 
     final_mess = (0).to_bytes(SEQ_ID_SIZE, byteorder='big',signed = True) + b"==FINACK=="
     PacketDelays[0] = [timer(), 0]
     udp_socket.sendto(final_mess, ("localhost", 5001))

     not_finished = True
     while (not_finished):
          try:
               head, _ = udp_socket.recvfrom(PACKET_SIZE)
               head = int.from_bytes(head[:SEQ_ID_SIZE],byteorder='big', signed=True)
               PacketDelays[0][1] = timer()
               not_finished = False
          except socket.timeout: # socket
               break
endThroughput = timer()

TruePacketDelays = []
prev = endThroughput
#counter = 0
for key, time in reversed(PacketDelays.items()):
     if time[1] == 0.0:
          TruePacketDelays.append(prev-time[0])
#         counter += 1
     else:
          prev = time[1]
          TruePacketDelays.append(time[1]-time[0])

#print(counter)
avgPacket = avgTime(TruePacketDelays)
throughput = endThroughput - startThroughput 
#print("Throughput", throughput)
#print("Packet Delays",avgPacket)
#print("Metric", (0.3 * throughput / 1000) + (0.7 * avgPacket))
print(f'{throughput:.7f}, {avgPacket:.7f}, {((0.3 * throughput / 1000) + (0.7 * avgPacket)):.7f}')