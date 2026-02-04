import socket

PACKET_SIZE = 1024

#sequence id size is 4
#bits 0 to 15 are source port, 16 to 30 are distination port, 31 to 47 is checksum, 48 to 64 is length
#bits 65 to 1023 are data

#there will be 1024-32 = 992 bits of actual data = 124 Bytes
# localhost = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# source = 0b0000000000000000
source = "0000000000000000"
#5001 in binary is 0001001110001001
# dest = 0b0001001110001001
dest = "0001001110001001"
# length = 0b0000010000000000
length = "0000010000000000"


# socket.bind(("localhost", "0.0.0.0"))
def send(source, dest, packet):
    pass


#create a udp socket
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket, open('docker/file.mp3', 'rb') as mp3:
    udp_socket.bind(("0.0.0.0", 5001))

    #data will be the data read out of the file
    data = mp3.read() #
    checksum = hash(data) #this gives different results when hash is used in a different executable
    checksum = str(checksum)[:16]
    packet_header = source + dest + checksum + length
    

    remaining = len(data)

    while remaining > PACKET_SIZE:
        print(remaining)
        packet = packet_header + data[]
        send("localhost", 5001, packet)
        remaining -= PACKET_SIZE


    # print(data[0])
    # print(data[1])
    # print(data[2:10])
    # print (data)
    print(checksum)
         
print("end")