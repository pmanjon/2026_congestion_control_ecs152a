# Uses selective repetition 
from timeit import default_timer as timer
import socket

PACKET_SIZE = 1024  # size in bytes of packet
WINDOW_SIZE = 100   # packets per window
SEQ_ID_SIZE = 4     # int for the sequence number
MESSAGE_SIZE = PACKET_SIZE - SEQ_ID_SIZE # 
port_num = 5001


def avgTime(someList):
    avgThing = 0.0 
    for time in someList:
        avgThing += time
    avgThing /= len(someList)
    return avgThing

# PlaceHolder for sending the file
def sendFile():

    FILE = "file.mp3"
    with open(FILE, "rb") as file:
        data = file.read()
    data_length = len(data)
    total_packets = int(data_length / MESSAGE_SIZE)
    packets_left = total_packets

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        address, _ = udp_socket.getsockname()
        udp_socket.connect((address, port_num))
        udp_socket.settimeout(0.5)

        seq_id = 0
        # print("length:", data_length)
        # cur_acks = {}
        # cur_messages = []
        packetDelays = {}
        window = set()
        # We subtract MESSAGE_SIZE to stop the loop just before we send the last packet
        # this is so we can empty the window first and then send the last packet
        while seq_id < data_length - MESSAGE_SIZE:
            print(seq_id)
            if (packets_left == 0): break

            if (len(window) != WINDOW_SIZE and seq_id + MESSAGE_SIZE < data_length):
                cur_mes = seq_id.to_bytes(SEQ_ID_SIZE, byteorder='big', signed=True) + data[seq_id: seq_id + MESSAGE_SIZE]
                udp_socket.send(cur_mes)

                seq_id += MESSAGE_SIZE
                # print("seq_id:", seq_id)
                packetDelays[seq_id] = timer()
                window.add(seq_id)

            else:
                try:
                    new_data, _ = udp_socket.recvfrom(PACKET_SIZE)
                    # print("in try")
                    ackHead = int.from_bytes(new_data[:SEQ_ID_SIZE],byteorder='big', signed=True)
                    # print(window)
                    print("len", len(window))
                    print(ackHead)
                    print(ackHead in window)
                    # cur_acks[ackHead] = True
                    if (ackHead in window):
                        packetDelays[ackHead] = timer() - packetDelays[ackHead]
                        window.remove(ackHead)
                        # print("removed", ackHead)
                        packets_left -= 1
                    elif (ackHead >= data_length):
                        break

                except socket.timeout:
                    if (seq_id >= data_length):
                        break
                    # print("in except")
                    for cur_id in window:
                        actual_id = cur_id - MESSAGE_SIZE
                        new_msg = actual_id.to_bytes(SEQ_ID_SIZE, byteorder='big', signed=True) + data[actual_id: actual_id + MESSAGE_SIZE]
                        udp_socket.send(new_msg)
                        packetDelays[cur_id] = timer()
        
        cleanseWindow(data, udp_socket, window, packetDelays)

        length = min(data_length - seq_id, MESSAGE_SIZE)
        last_packet = seq_id.to_bytes(SEQ_ID_SIZE, byteorder='big', signed=True) + data[seq_id: seq_id + length]

        udp_socket.send(last_packet)
        packetDelays[seq_id] = timer()
        while(True):
            try:
                new_data, _ = udp_socket.recvfrom(PACKET_SIZE)
                ackHead = int.from_bytes(new_data[:SEQ_ID_SIZE],byteorder='big', signed=True)
                if (ackHead == seq_id + MESSAGE_SIZE): 
                    packetDelays[seq_id] = timer() - packetDelays[ackHead]
                    break
            except socket.timeout:
                udp_socket.send(last_packet)
                packetDelays[seq_id] = timer()

        # final message 
        final_mess = (-1).to_bytes(SEQ_ID_SIZE, byteorder='big',signed = True) + b"==FINACK=="
        udp_socket.send(final_mess)

    return packetDelays

def cleanseWindow(data, socket: socket.socket, window: set, pack_delays: dict):
    while (len(window) > 0):
        cur_id = window.pop()
        cur_packet = cur_id.to_bytes(SEQ_ID_SIZE, byteorder='big', signed=True) + data[cur_id: cur_id + MESSAGE_SIZE]

        socket.send(cur_packet)
        pack_delays[cur_id + MESSAGE_SIZE] = timer()

        while(True):
            try:
                new_data, _ = socket.recvfrom(PACKET_SIZE)
                ackHead = int.from_bytes(new_data[:SEQ_ID_SIZE],byteorder='big', signed=True)
                if (ackHead == cur_id + MESSAGE_SIZE): 
                    pack_delays[cur_id + MESSAGE_SIZE] = timer() - pack_delays[ackHead]
                    window.remove(ackHead)
                    break
                elif (ackHead in window):
                    pack_delays[ackHead] = timer() - pack_delays[ackHead]
                    window.remove(ackHead)
            except socket.timeout:
                socket.send(cur_packet)
                pack_delays[cur_id + MESSAGE_SIZE] = timer()

startThroughput = timer()

# replace with actual send file code
pack_delays = sendFile()

# keep this the same 
endThroughput = timer()
# Throughput = PACKET_SIZE / (endThroughput - startThroughput)
Throughput = MESSAGE_SIZE / (endThroughput - startThroughput)

avgPacketdelay = sum(pack_delays.values()) / len(pack_delays)
performance = (0.3 / 1000 * Throughput) + (0.7/avgPacketdelay)

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