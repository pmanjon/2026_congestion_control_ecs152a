import socket

#this is hardcoded in right now but it needs to abide be the training profile
PACKET_SIZE = 1024
SEQ_ID_SIZE = 4 #we can make sequence ids between 0-15
# src_add = "127.0.0.2"
port_num = 5001

def getSeqID(sequence):
    output, power = 0, 2^SEQ_ID_SIZE

    for char in sequence:
        #char is either '0' or '1'
        output += int(char) * power
        power/= 2

    return output

def send_file(src_socket: socket.socket, data):
    sequence_id = 0
    binary_string = format(sequence_id, 'b')
    print(sequence_id)
    print(binary_string)

    address, port = src_socket.getsockname()

    remaining = len(data) #how many bytes there are left
    # index where we start reading within data to make a packet
    bookmark = 0

    # how far we normally read to make a packet
    # divide PACKET_SIZE by 8 because we are reading bytes
    reading_length = int(PACKET_SIZE/8) - SEQ_ID_SIZE

    while remaining > 0: 
        # print(remaining)
        # length of packet we are sending
        length = min(remaining, reading_length)

        #packet = sequence number concatenated with data
        packet = sequence_id.to_bytes() + data[bookmark: bookmark + length] 
        
        src_socket.send(packet)

        acknowledged = False
        while not(acknowledged):
            msg = src_socket.recvfrom(length)
            if (getSeqID(msg) == sequence_id): acknowledged = True
            #print(acknowledged)

        remaining -= length
        bookmark += length
        sequence_id = sequence_id + 1 if sequence_id != 2^SEQ_ID_SIZE - 1 else 0
    #remaining should now be 0 
    return

#create a udp socket
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket, open('docker/file.mp3', 'rb') as mp3:
    address, port = udp_socket.getsockname()
    print(address)
    print(port)

    udp_socket.connect((address, port_num))
    # udp_socket.settimeout(1)
    # udp_socket.listen(1) #only listening to one receiver

    #data will be the data read out of the file
    data = mp3.read() #made of bytes
    print(type(data))

    send_file(udp_socket, data)



print("end")

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