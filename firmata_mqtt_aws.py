'''
/*
 * Copyright 2010-2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import sys
import logging
import time
from pyfirmata import Arduino, util

# Custom MQTT message callback
def customCallback(client, userdata, message):
	print("MESSAGES: "+message.topic+" "+str(message.payload))
	msg_list = message.topic.split("/")

	if msg_list[2] == "pin" : 
		pino = msg_list[3] 
		valor = message.payload
		board.digital[int(pino)].write(int(valor))



A0_enable = False
A1_enable = True
A2_enable = False
A3_enable = False
A4_enable = False
A5_enable = False
DeadBand = 10

# Read in command-line parameters
useWebsocket = False
host = "a1235sx9xlme6.iot.us-west-2.amazonaws.com"
rootCAPath = "root-CA.crt"
certificatePath = "Raspberry.cert.pem"
privateKeyPath = "Raspberry.private.key"

board = Arduino('/dev/ttyACM0')
Arduino_number = 1
PATH = "arduino/"+str(Arduino_number)
PUB = PATH+"/analog/"
TOPIC = PATH+"/pin/#"
pins = [None]*14


it = util.Iterator(board)
it.start()
board.analog[0].enable_reporting()
board.analog[1].enable_reporting()
board.analog[2].enable_reporting()
board.analog[3].enable_reporting()
board.analog[4].enable_reporting()
board.analog[5].enable_reporting()
time.sleep( 1 )

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub")
myAWSIoTMQTTClient.configureEndpoint(host, 8883)
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
myAWSIoTMQTTClient.subscribe(TOPIC, 1, customCallback)
time.sleep(2)


A0_ant = 0
A1_ant = 0
A2_ant = 0
A3_ant = 0
A4_ant = 0
A5_ant = 0
while True:
	A0 = board.analog[0].read()*1000
	A1 = board.analog[1].read()*1000
	A2 = board.analog[2].read()*1000
	A3 = board.analog[3].read()*1000
	A4 = board.analog[4].read()*1000
	A5 = board.analog[5].read()*1000

	if A0_enable == False:
		A0 = 0
	if A1_enable == False:
		A1 = 0
	if A2_enable == False:
		A2 = 0
	if A3_enable == False:
		A3 = 0
	if A4_enable == False:
		A4 = 0
	if A5_enable == False:
		A5 = 0


	if (A0 > A0_ant+DeadBand or A0 < A0_ant-DeadBand):
		try:
			myAWSIoTMQTTClient.publish(PUB+"0", A0, 1)
			A0_ant = A0
		except:
			continue
	if (A1 > A1_ant+DeadBand or A1 < A1_ant-DeadBand):
		try:
			myAWSIoTMQTTClient.publish(PUB+"1", A1, 1)
			A1_ant = A1
		except:
			continue
	if (A2 > A2_ant+DeadBand or A2 < A2_ant-DeadBand):
		try:
			myAWSIoTMQTTClient.publish(PUB+"2", A2, 1)
			A2_ant = A2
		except:
			continue
	if (A3 > A3_ant+DeadBand or A3 < A3_ant-DeadBand):
		try:
			myAWSIoTMQTTClient.publish(PUB+"3", A3, 1)
			A3_ant = A3
		except:
			continue
	if (A4 > A4_ant+DeadBand or A4 < A4_ant-DeadBand):
		try:
			myAWSIoTMQTTClient.publish(PUB+"4", A4, 1)
			A4_ant = A4
		except:
			continue
	if (A5 > A5_ant+DeadBand or A5 < A5_ant-DeadBand):
		try:
			myAWSIoTMQTTClient.publish(PUB+"5", A5, 1)
			A5_ant = A5
		except:
			continue