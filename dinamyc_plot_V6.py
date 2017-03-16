import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import Tkinter as tk
import matplotlib.pyplot as plt
from numpy import arange, pi, random, linspace
import logging
import numpy as np
import time 
import boto3
import datetime
import threading
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

#Possibly this rendering backend is broken currently
#from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas

useWebsocket = True
host = "a1235sx9xlme6.iot.us-west-2.amazonaws.com"
cognitoIdentityPoolID = "us-west-2:ec4501fb-2115-4d27-bcdf-f0e85d46da84"
rootCAPath = "root-CA.crt"
certificatePath = "Raspberry.cert.pem"
privateKeyPath = "Raspberry.private.key"
Arduino_number = 1
PATH = "arduino/"+str(Arduino_number)
PUB = PATH+"/analog/#"
print PUB


def customCallback(client, userdata, message):
	print("MESSAGES: "+message.topic+" "+str(message.payload))
	msg_list = message.topic.split("/")
	analog_number = int(msg_list[3])
	print analog_number
	c = int(float(message.payload))
	print c
	mc.add_point(None,c,analog_number)


class MainClass():
	def __init__(self,myAWSIoTMQTTClient):
		print myAWSIoTMQTTClient				
		self.y = np.zeros([1,6])
		self.x = []		
		self.x.append(datetime.datetime.now())		
		self.builder = Gtk.Builder()
		self.builder.add_objects_from_file('client.glade', ('window1', '') )
	
		self.window = self.builder.get_object('window1')

		self.sw = []
		self.fig =[]
		self.ax =[]
		self.canvas = []
		self.sw=[]
		for i in range(1,7):
			print i
			c = i - 1
			self.obj = 'scrolledwindow' + str(i)
			self.sw.append(self.builder.get_object(self.obj))			
			self.fig.append(plt.Figure(figsize=(5,5), dpi=80))
			self.ax.append(self.fig[i-1].add_subplot(1,1,1))
			self.fig[i-1].autofmt_xdate()	
			self.canvas.append(FigureCanvas(self.fig[i-1]))
			self.sw[i-1].add_with_viewport(self.canvas[i-1])

			x_labels = [self.x[i].time().strftime("%H:%M:%S") for i in range(len(self.x))]
			self.ax[c].cla()
			self.ax[c].set_xticklabels(x_labels,rotation='vertical')
			self.ax[c].plot(self.x,self.y[:,c])		
			self.fig[c].canvas.draw_idle()	

		print self.sw

		self.handlers = {
		    "on_window1_destroy": Gtk.main_quit,
		    "LigarPressed": self.ligar,
		    "DesligarPressed": self.desligar
		}
		self.builder.connect_signals(self.handlers)

		
	def add_point(self,widget,y_point,number):	
		y_temp = self.y[-1]				
		self.y = np.vstack((self.y, y_temp))
		self.y = np.vstack((self.y, y_temp))
		y_temp = self.y[-1]		
		y_temp[number] = y_point

		# self.y.append(y_temp)
		# print self.y
		self.x.append(datetime.datetime.now())
		self.x.append(datetime.datetime.now())				
		self.plotpoints(widget,number)			

	
	def plotpoints(self,widget,c):	
		
		# self.ax[number].grid(True)
		x_labels = [self.x[i].time().strftime("%H:%M:%S") for i in range(len(self.x))]
		print x_labels

	
		self.ax[c].cla()
		self.ax[c].set_xticklabels(x_labels,rotation='vertical')
		self.ax[c].plot(self.x,self.y[:,c])		
		self.fig[c].canvas.draw_idle()	
	def ligar(self,widget):
		print "ligar"
		myAWSIoTMQTTClient.publish(PATH+"/pin/11", "1" , 1)	
	def desligar(self,widget):
		print "desligar"
		myAWSIoTMQTTClient.publish(PATH+"/pin/11", "0" , 1)	
		# self.ax[0].set_xticklabels(x_labels,rotation='vertical')
		# self.ax2[0].set_xticklabels(x_labels,rotation='vertical')
		# self.ax3[0].set_xticklabels(x_labels,rotation='vertical')

		# self.ax[0].plot(self.x,self.y[:,number])	
		# self.ax2[0].plot(self.x,self.y[:,number])	
		# self.ax3[0].plot(self.x,self.y[:,number])
		# # self.ax.xlabel(rotation='vertical')
		# self.fig.canvas.draw_idle()
		# self.fig2.canvas.draw_idle()
		# self.fig3.canvas.draw_idle()

		




logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)


identityPoolID = cognitoIdentityPoolID
region = host.split('.')[2]
cognitoIdentityClient = boto3.client('cognito-identity', region_name=region)
temporaryIdentityId = cognitoIdentityClient.get_id(IdentityPoolId=identityPoolID)
identityID = temporaryIdentityId["IdentityId"]
temporaryCredentials = cognitoIdentityClient.get_credentials_for_identity(IdentityId=identityID)
AccessKeyId = temporaryCredentials["Credentials"]["AccessKeyId"]
SecretKey = temporaryCredentials["Credentials"]["SecretKey"]
SessionToken = temporaryCredentials["Credentials"]["SessionToken"]


# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub_CognitoSTS", useWebsocket=True)

# AWSIoTMQTTClient configuration
myAWSIoTMQTTClient.configureEndpoint(host, 443)
myAWSIoTMQTTClient.configureCredentials(rootCAPath)
myAWSIoTMQTTClient.configureIAMCredentials(AccessKeyId, SecretKey, SessionToken)
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
myAWSIoTMQTTClient.connect()
myAWSIoTMQTTClient.subscribe(PUB, 1, customCallback)

# Connect and subscribe to AWS IoT
print myAWSIoTMQTTClient

mc = MainClass(myAWSIoTMQTTClient)
# mc.add_point(None,10)
# thread = RepeatEvery(1, mc.plotpoints2, "Hello World!")

# print "starting"
# thread.start()

# thread.join(2)  # allow thread to execute a while...

# thread.stop()

# print 'stopped'

# mc.window.connect("delete-event", Gtk.main_quit)
mc.window.show_all()

Gtk.main()
