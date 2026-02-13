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
        # print(sequence_id)
        # print(remaining)
        # length of packet we are sending
        length = min(remaining, reading_length)
        head = sequence_id.to_bytes(length=SEQ_ID_SIZE, byteorder='big')

        #packet = sequence number concatenated with data
        packet = head + data[bookmark: bookmark + length] 
        
        del_start = timer() #note the time we sent the packet to calculate packet delay
        src_socket.sendto(packet, ("localhost", port_num))

        expectedAckHead = sequence_id + length
        acknowledged = False
        while not(acknowledged):
            try:
                msg, _ = src_socket.recvfrom(length)
                ackHead =  int.from_bytes(msg[:SEQ_ID_SIZE], byteorder='big')
                acknowledged = ackHead == expectedAckHead
            except socket.timeout:
                src_socket.sendto(packet,("localhost", port_num))

        cum_delay += timer() - del_start #calculate the packet delay and it to the cumulative delay
        # print(cum_delay)

        sequence_id += length
        remaining -= length
        bookmark += length

    # remaining should now be 0 
    # print("cum_delay:", cum_delay)

    #tell receiver we are done sending
    last_msg = sequence_id.to_bytes(length=SEQ_ID_SIZE, byteorder='big') \
             + bytes('==FINACK==', 'utf-8')
    udp_socket.sendto(last_msg, ("localhost", port_num))

    return cum_delay

#create a udp socket
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket, \
     open('file.mp3', 'rb') as mp3:
    
    udp_socket.bind(("localhost", 5000))
    udp_socket.settimeout(.5)

    #data will be the data read out of the file
    data = mp3.read() #made of bytes

    total_sent = len(data)
    num_of_packets = int(total_sent/DATA_SIZE)

    through_start = timer()
    total_delay = send_file(udp_socket, data)
    through_end = timer()
    throughput = total_sent / (through_end - through_start)
    avg_delay = total_delay/num_of_packets

    print(f'{throughput:.7f}, {avg_delay:.7f}, {((0.3 * throughput / 1000) + (0.7 * avg_delay)):.7f}')

