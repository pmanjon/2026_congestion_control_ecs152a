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

    FILE = "docker/file.mp3"
    with open(FILE, "rb") as file:
        data = file.read()
    total_packets = int(len(data) / MESSAGE_SIZE)
    packets_left = total_packets


    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind(("localhost", 5000))
        udp_socket.settimeout(1)

        seq_id = 0

        # cur_acks = {}
        # cur_messages = []
        
        PacketDelays = {}
        window = set()
        while seq_id < len(data) or len(window) > 0:
            if (packets_left == 0): break
            if (len(window) != WINDOW_SIZE and seq_id < len(data)):
                cur_mes = seq_id.to_bytes(SEQ_ID_SIZE, byteorder='big', signed=True) + data[seq_id: seq_id + MESSAGE_SIZE]
                udp_socket.sendto(cur_mes, ("localhost", 5001))

                seq_id += MESSAGE_SIZE
                # print("seq_id:", seq_id)
                PacketDelays[seq_id] = timer()
                window.add(seq_id)

            else:
                try:
                    new_data, _ = udp_socket.recvfrom(PACKET_SIZE)
                    ackHead = int.from_bytes(new_data[:SEQ_ID_SIZE],byteorder='big', signed=True)
                    # cur_acks[ackHead] = True
                    if (ackHead in window):
                        PacketDelays[ackHead] = timer() - PacketDelays[ackHead]
                        window.remove(ackHead)
                        # print("removed", ackHead)
                        packets_left -= 1

                except socket.timeout:
                    for cur_id in window:
                        actual_id = cur_id - MESSAGE_SIZE
                        new_msg = actual_id.to_bytes(SEQ_ID_SIZE, byteorder='big', signed=True) + data[actual_id: actual_id + MESSAGE_SIZE]
                        udp_socket.sendto(new_msg, ("localhost", 5001))
                
        # final message 
        final_mess = (-1).to_bytes(SEQ_ID_SIZE, byteorder='big',signed = True) + b"==FINACK=="
        udp_socket.sendto(final_mess, ("localhost", 5001))
        endPacket = timer()

        not_finished = True
        while (not_finished):
            try:
                head, _ = udp_socket.recvfrom(PACKET_SIZE)
                head = int.from_bytes(head[:SEQ_ID_SIZE],byteorder='big', signed=True)
                PacketDelays[head] = timer() - endPacket
                not_finished = False
            except socket.timeout:
                udp_socket.sendto(final_mess, ("localhost", 5001))

    return PacketDelays

sendFile()
print("end")
# #sending the same file 10 times to get average
for x in range(0,10):
    startThroughput = timer()
    
    # replace with actual send file code
    pack_delays = sendFile()

    # keep this the same 
    endThroughput = timer()
    # Throughput = PACKET_SIZE / (endThroughput - startThroughput)
    Throughput = MESSAGE_SIZE / (endThroughput - startThroughput)
    Throughputs.append(Throughput)

    avgPacketdelay = sum(pack_delays.values()) / len(pack_delays)
    performance = .3*Throughput + (0.7/avgPacketdelay)
    Performances.append(performance)

    print("trial", x)
    print("Throughput:", Throughput)
    print("Avg packet delay:", avgPacketdelay)
    print("Performance:", performance)


# """
# Printing the averages of the metrics
# """
# avgThroughput = avgTime(Throughputs)
# avgPacketdelay = avgTime(PacketDelays)
# avgPerfomance = avgTime(Performances)

# print(f"{avgThroughput:.7f}, {avgPacketdelay:.7f}, {avgPerfomance:.7f}")