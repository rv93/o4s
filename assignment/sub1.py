from time import sleep
import time as time_
import zmq
import json 




def set_sub_connection():
    context_sub = zmq.Context()
    socket_sub = context_sub.socket(zmq.SUB)
    # We can connect to several endpoints if we desire, and receive from all.
    socket_sub.connect("tcp://127.0.0.1:5000")
    return socket_sub

def set_pub_connection():
	context_pub = zmq.Context()
	socket_pub = context_pub.socket(zmq.PUB)
	socket_pub.setsockopt(zmq.LINGER,0)
	socket_pub.connect("tcp://127.0.0.1:5001")
    # We must declare the socket as of type SUBSCRIBER, and pass a prefix filter.
    # Here, the filter is the empty string, wich means we receive all messages.
    # We may subscribe to several filters, thus receiving from all.
	socket_sub.setsockopt(zmq.SUBSCRIBE, '')
	return socket_pub

socket_sub=set_sub_connection()
socket_pub=set_pub_connection()

pos=None
x1,y1=None,None
while True:
	message = socket_sub.recv_pyobj()
	print "R1 ---- Received %s from Master" %(message)

	if message == "KILL":
		break
	
	if message == "END of Lap":
		print "R1 ---- End of Lap"
		socket_pub.close()
		sleep(1)
		socket_pub = set_pub_connection()
		pos=None
		continue

	if pos==None and message and message!="END of Lap":
		pos=message
		m1,c1=pos[0]
		m2,c2=pos[1]

		#point of intersection
		x1 = (c2 - c1)/(m1-m2)
		y1 = m1 * x1 + c1
		print "Point of intersection = %d,%d" %(x1,y1)

	elif pos:
		x1+=1
		y1=m1*x1+c1
		pos=[x1,y1]

#	print "pos = %d" %(pos)
	sleep(0.05)
#	socket_pub.send_pyobj([b'A',pos])
	socket_pub.send_multipart([b'R1',json.dumps({'x':x1, 'y':y1,'t':int(round(time_.time() * 1000))})])

	print "R1 ---- sent pos %s to M" %(pos)


