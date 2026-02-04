from timeit import default_timer as timer
PACKET_SIZE = 1024

Throughputs =       []
totalPacketDelays = [] # non-cummalitive 
Performances =      []

def avgTime(someList):
    avgThing = 0.0 
    for time in someList:
        avgThing += time
    avgThing /= len(someList)
    return avgThing

# Placeholder for sending individual packets
def sendPacket(x):
    return x

# PlaceHolder for sending the file
def sendFile(x):
    startPacket = timer()
    PacketDelays = []

    # replace this line with the actual send packet code
    sendPacket(x)
    
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
    sendFile(x)

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