import socket

SEQ_LENGTH = 4
PACKET_SIZE = 1024
def send_file(src_socket: socket.socket, dest_socket: socket.socket, data):
    sequence_id = 0
    binary_string = format(sequence_id, 'b')
    print(sequence_id)
    print(binary_string)
    src_socket.connect(dest_socket)
    
    remaining = len(data) #how many bytes there are left
    # index where we start reading within data to make a packet
    bookmark = 0

    # how far we normally read to make a packet
    # divide PACKET_SIZE by 8 because we are reading bytes
    reading_length = int(PACKET_SIZE/8)

    while remaining > 0: 
        # print(remaining)

        # length of packet we are sending
        # divide PACKET_SIZE by 8 because we are reading bytes
        length = min(remaining, reading_length)

        packet = data[bookmark: bookmark + length] 
        src_socket.send(packet)

        acknowledged = False
        while not(acknowledged):
            acknowledged = src_socket.recv(length)

        remaining -= reading_length
        bookmark += reading_length
    
    #remaining should now be 0 or negative      


#create a udp socket
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket, open('docker/file.mp3', 'rb') as mp3:
    udp_socket.bind(("0.0.0.0", 5000))
    udp_socket.settimeout(1)
    udp_socket.listen(1) #only listening to one receiver

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