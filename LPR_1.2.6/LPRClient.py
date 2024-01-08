#-*- coding:utf-8 -*-
import socket
import GlobalCounters
HOST = "210.119.32.94"
PORT = 4000

def connectServer():
    GlobalCounters.mysocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
 
def sendMessage(msg):
        packet = msg
        GlobalCounters.mysocket.sendto(packet,(GlobalCounters.HOST,GlobalCounters.PORT))
 
        packet, address = GlobalCounters.mysocket.recvfrom(1024)
 
        print "Packet recevied!"
        print "From : %s, Port : %s"%(address[0],address[1])
        print "Length : ",len(packet)
        print "Packet : ",packet       
        print "\n"
 
def closeServer():
   GlobalCounters.mysocket.close()