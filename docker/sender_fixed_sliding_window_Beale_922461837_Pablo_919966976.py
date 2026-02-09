# Uses selective repetition 
from timeit import default_timer as timer
import socket

PACKET_SIZE = 1024  # size in bytes of packet
WINDOW_SIZE = 100   # packets per window
SEQ_ID_SIZE = 4     # int for the sequence number
MESSAGE_SIZE = PACKET_SIZE - SEQ_ID_SIZE # 

Throughputs =       []
totalPacketDelays = [] 
Performances =      []

def avgTime(someList):
    avgThing = 0.0 
    for time in someList:
        avgThing += time
    avgThing /= len(someList)
    return avgThing

# PlaceHolder for sending the file
def sendFile():
    PacketDelays = {}

    FILE = "file.mp3"
    with open(FILE, "rb") as file:
        data = file.read()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind(("localhost", 5000))
        udp_socket.settimeout(1)

        seq_id = 0
        while seq_id < len(data):
            
            cur_acks = {}
            cur_messages = []
            cur_seq_id = seq_id
            # make the current messages to send
            for idx in range(WINDOW_SIZE):
                cur_mes = idx.to_bytes(SEQ_ID_SIZE, byteorder='big', signed='True') + data[cur_seq_id: cur_seq_id + MESSAGE_SIZE]
                cur_messages.append((cur_seq_id, cur_mes))
                cur_acks[cur_seq_id] = False
                cur_seq_id += MESSAGE_SIZE

            # send messages
            for cur_id, message in cur_messages:
                startPacket = timer()
                udp_socket.sendto(message,("localhost", 5001))
                PacketDelays[cur_id] = (startPacket, startPacket)

            # wait for acknowledgements
            while True:
                try:
                    data, address = udp_socket.recvfrom(PACKET_SIZE)
                    data = int.from_bytes(data[:SEQ_ID_SIZE],byteorder='big', signed=True)
                    cur_acks[data] = True # first bytes is the sequence number
                    PacketDelays[data].second = timer()

                    if all(cur_acks):
                        break
                except socket.timeout:
                    # Selective repetition sends only packets that were dropped
                    for cur_id, cur_mess in cur_messages:
                        if not cur_acks[cur_id]:
                            udp_socket.sendto(message, ("localhost", 5001))
        # final message 
        final_mess = (-1).to_bytes(SEQ_ID_SIZE, byteorder='big',signed='TRUE') + "==FINACK"
        udp_socket.sendto(final_mess, ("localhost", 5001))

    # Keep the same
    endPacket = timer()
    PacketDelays.append(endPacket-startPacket)
    totalPacketDelays.append(endPacket-startPacket)
    return 0



#sending the same file 10 times to get average
for x in range(0,10):
    startThroughput = timer()
    PacketDelays = [] # erase me -- temp var
    
    # replace with actual send file code
    sendFile()

    # keep this the same 
    endThroughput = timer()
    Throughput = PACKET_SIZE / (endThroughput - startThroughput)
    avgPacketdelay = avgTime(PacketDelays)
    Throughputs.append(Throughput)
    performance = .3*Throughput + (0.7/avgPacketdelay)
    Performances.append(performance)



"""
Printing the averages of the metrics
"""
avgThroughput = avgTime(Throughputs)
avgPacketdelay = avgTime(PacketDelays)
avgPerfomance = avgTime(Performances)

print(f"{avgThroughput:.7f}, {avgPacketdelay:.7f}, {avgPerfomance:.7f}")