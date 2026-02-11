import socket
from timeit import default_timer as timer

PACKET_SIZE = 1024
SEQ_ID_SIZE = 4
DATA_SIZE = PACKET_SIZE - SEQ_ID_SIZE
port_num = 5001
# cum_delay = 0 #cumulative packet delays


def send_file(src_socket: socket.socket, data):
    sequence_id = 0
    remaining = len(data) #how many bytes there are left
    # index where we start reading within data to make a packet
    bookmark = 0

    # how far we normally read to make a packet
    reading_length = DATA_SIZE
    cum_delay = 0 #cumulative packet delays


    while remaining > 0: 
        # print(remaining)
        # length of packet we are sending
        length = min(remaining, reading_length)
        head = sequence_id.to_bytes(length=SEQ_ID_SIZE, byteorder='big')

        #packet = sequence number concatenated with data
        packet = head + data[bookmark: bookmark + length] 
        
        del_start = timer() #note the time we sent the packet to calculate packet delay
        src_socket.send(packet)

        expectedAckHead = sequence_id + length
        acknowledged = False
        while not(acknowledged):
            msg, _ = src_socket.recvfrom(length)
            ackHead =  int.from_bytes(msg[:SEQ_ID_SIZE], byteorder='big')
            acknowledged = ackHead == expectedAckHead

            if(not(acknowledged)): src_socket.send(packet)

        cum_delay += timer() - del_start #calculate the packet delay and it to the cumulative delay
        # print(cum_delay)

        sequence_id += length
        remaining -= length
        bookmark += length

    #remaining should now be 0 
    print("cum_delay:", cum_delay)

    #tell receiver we are done sending
    last_msg = sequence_id.to_bytes(length=SEQ_ID_SIZE, byteorder='big') \
             + bytes('==FINACK==', 'utf-8')
    udp_socket.send(last_msg)

    return cum_delay

#create a udp socket
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket, \
     open('docker/file.mp3', 'rb') as mp3:
    
    address, _ = udp_socket.getsockname()
    udp_socket.connect((address, port_num))
    # udp_socket.settimeout(1)

    #data will be the data read out of the file
    data = mp3.read() #made of bytes
    # print(type(data))

    total_sent = len(data)
    num_of_packets = int(total_sent/DATA_SIZE)

    through_start = timer()
    total_delay = send_file(udp_socket, data)
    through_end = timer()
    throughput = total_sent / (through_end - through_start)
    avg_delay = total_delay/num_of_packets

    print("throughput is ", throughput)
    print("average delay of packets:", avg_delay)
    print("performance:", (0.3 * throughput / 1000) + (0.7 * avg_delay))
    # print("num of packets:", num_of_packets)


# print("end")

# from timeit import default_timer as timer
# PACKET_SIZE = 1024

# Throughputs =       []
# totalPacketDelays = [] # non-cummalitive 
# Performances =      []

# def avgTime(someList):
#     avgThing = 0.0 
#     for time in someList:
#         avgThing += time
#     avgThing /= len(someList)
#     return avgThing

# # Placeholder for sending individual packets
# def sendPacket(x):
#     return x

# # PlaceHolder for sending the file
# def sendFile(x):
#     startPacket = timer()
#     PacketDelays = []

#     # replace this line with the actual send packet code
#     sendPacket(x)
    
#     # Keep the same
#     endPacket = timer()
#     PacketDelays.append(endPacket-startPacket)
#     totalPacketDelays.append(endPacket-startPacket)
#     return 0

# #sending the same file 10 times to get average
# for x in range(0,10):
#     startThroughput = timer()
#     PacketDelays = [] # erase me -- temp var
#     # replace with actual send file code
#     sendFile(x)

#     # keep this the same 
#     endThroughput = timer()
#     Throughput = PACKET_SIZE / (endThroughput - startThroughput)
#     avgPacketdelay = avgTime(PacketDelays)
#     Throughputs.append(Throughput)
#     performance = .3*Throughput + (0.7/avgPacketdelay)
#     Performances.append(performance)



# """
# Printing the averages of the metrics
# """
# avgThroughput = avgTime(Throughputs)
# avgPacketdelay = avgTime(PacketDelays)
# avgPerfomance = avgTime(Performances)

# print(f"{avgThroughput:.7f}, {avgPacketdelay:.7f}, {avgPerfomance:.7f}")