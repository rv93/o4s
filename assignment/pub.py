from time import sleep
import time
import zmq
import random
import math
from datetime import datetime 
import json 


def set_pub_connection():
	context_pub = zmq.Context()
	socket_pub = context_pub.socket(zmq.PUB)
	socket_pub.bind('tcp://127.0.0.1:5000')
	return socket_pub

def set_sub_connection():
	context_sub = zmq.Context()
	socket_sub = context_sub.socket(zmq.SUB)
	socket_sub.setsockopt(zmq.LINGER,0)
	socket_sub.bind('tcp://127.0.0.1:5001')

	socket_sub.setsockopt(zmq.SUBSCRIBE,"R1")
	socket_sub.setsockopt(zmq.SUBSCRIBE,"R2")
	return socket_sub


class Lap:
	def	__init__(self, lap_number):
		self.lap_number=lap_number
		self.start_time=datetime.now().time()
		self.end_time=None
		self.total_latency=[]
		self.average_latency=[]
		self.loops=0

	def end_lap(self):
		self.end_time=datetime.now().time()

	def averageLatency(self):
		self.average_latency = [str(float(l)/self.loops) for l in self.total_latency]
		return self.average_latency
		
	def timeToCompletion(self):
		diff=datetime.combine(datetime.today(), self.end_time) - datetime.combine(datetime.today(), self.start_time)
		self.time_to_completion=diff.total_seconds()
		return self.time_to_completion

	def __str__(self):
		#[LapNumber, LapStart, LapEnd, TimeToCompletion, AverageLatencyR1(optional), AverageLatencyR2(optional)]
		return "%d, %s, %s, %s s, %s" %(self.lap_number, self.start_time, self.end_time, self.timeToCompletion(), ", ".join(self.averageLatency())) 

	__repr__ = __str__



def calculate_distance(a,b):
	"""
	a and b are two list objects representing two points. We could also have used namedTuple here
	eg. 
		a = [x1,y1]
		b = [x2,y2]
	"""
	return math.sqrt( (a[0]-b[0])**2 + (a[1]-b[1])**2)


socket_pub=set_pub_connection()
socket_sub=set_sub_connection()

new_lap=True
filters = ['R1', 'R2']
laps = []
lap_count = 0 
loops=0
total_latency=[]

while True:
	if new_lap:
		
		lap_count+=1
		loops=0
		if lap_count==11:
			socket_pub.send_pyobj("KILL")
			break
	
		print "Master :: Beginning new Lap"
		print "Master :: Sending Initial data from Master "
		
		sleep(1)
		
#		m1 = random.randint(100,200)
#		c1 = random.randint(1,200)
#		m2 = random.randint(1,m1-1)
#		c2 = random.randint(c1+1,300)
#
		m1 = random.randint(5,7)
		c1 = random.randint(10,15)
		m2 = random.randint(3,m1-1)
		c2 = random.randint(c1+1,18)

		data=[(m1,c1),(m2,c2)]

		lap = Lap(lap_count)

		laps.append(lap)

		print "Master :: Sending %s to R1 and R2" %(data)

		d = {'R1':{}, 'R2':{}}
		d['R1']['exp_t']=int(round(time.time() * 1000))+50  # Setting expected time 
		d['R2']['exp_t']=int(round(time.time() * 1000))+50

		new_lap=False


	loops+=1  
	socket_pub.send_pyobj(data)
	data=None
	[filter, msg]  = socket_sub.recv_multipart()

	if msg:
		json_msg=json.loads(msg)
		d[filter]['pos']=[json_msg['x'], json_msg['y']]
		d[filter]['total_latency']=d[filter].setdefault('total_latency',0) + json_msg['t'] - d[filter]['exp_t']
		print "Master :: Received %s : %s" %(filter, json_msg)
#		print "Current Latency = %d" %(json_msg['t'] - d[filter]['exp_t'])
#		print "Latency for %s = %d" %(filter, d[filter]['total_latency'])

		d[filter]['exp_t']=int(round(time.time() * 1000))+50  # Setting expected time 

	if 'pos' in d['R1'] and 'pos' in d['R2'] and calculate_distance(d['R1']['pos'],d['R2']['pos']) > 10:
		socket_pub.send_pyobj("END of Lap")

		#Setting total latency
		#This will be used later to find average_latency
		for filter in filters:
			lap.total_latency.append(d[filter]['total_latency'])

		lap.loops=loops if loops<=1 else loops/2
		lap.end_lap()

		print "Master :: Finishing Lap %d" %(lap.lap_number)
		print lap
		print "\n\n"

		socket_sub.close()
		sleep(1)
		socket_sub=set_sub_connection()
		new_lap = True



print "\n\nMaster :: END OF All Laps\n\n"

laps.sort(key=lambda l: l.time_to_completion)

#Printing final result of all laps
for lap in laps:
	print lap
