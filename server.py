#************************************************************************
#*  NAME:  Robert Thomas						
#*  Course:  CSC328							
#*  Instructor:  Dr. Frye						
#*  Assignment:  TCP Concurrent Server				
#*  DUE DATE: 12/6/2015							
#*  Filename:  server.py							
#*  Purpose:  The purpose of this program is to create a concurrent TCP Server 
#*		that takes a message from the client, identifies what the client
#*		wants (CD, DIR, DOWNLOAD) and then gives the client its hearts 
#*		desire.
#*  COMPILE INSTRUCTIONS: Type python server.py <[port]>						
#************************************************************************
import os
import socket
import sys
import subprocess
from sys import argv
from thread import *


if len(sys.argv)==2:
	script, PORT = argv
elif len(sys.argv)>2:
	print >>sys.stderr, 'Please use the format: %s <[port]>\n' % sys.argv[0]
	sys.exit()
else:
	PORT = '55536'
HOST = socket.gethostname()	



try :
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	print 'Socket created'
except socket.error, msg :
	print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	sys.exit()


# Bind socket to local host and port
try:
	s.bind((HOST, int(PORT)))
except socket.error, msg :
	print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	sys.exit()
	
try:
	s.listen(5)
	print 'Socket is listening.  \nHit Ctrl-C to close server.'
except socket.error, msg :
	print 'Listen failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	sys.exit()

def downloadfunction(newdirectory, data):  #does the grunt work
	while True:
		filewords=conn.recv(16)
		if filewords == 'stop':  #no go on overwrite
			print(str(addr[1])+': File transmission terminated')
			break
		elif filewords=='getfile':  #send it all
			with open(newdirectory+'/'+data[9:], 'rb') as f:
				filename = f.read()
			conn.sendall('%16d' % len(filename))
			conn.sendall(filename)
			print(str(addr[1])+': File transmission done.')
		elif filewords == 'end':  #client got it
			print(str(addr[1])+': "end" command received. Teminate.')
			break
	
#Function for handling connections. This will be used to create threads
def clientthread(conn):
	#Sending message to connected client
	conn.send('HELLO!  Commands: BYE, CD, DIR, DOWNLOAD.\n') #send only takes string
	newdirectory= conn.recv(1024)
	homedirectory = newdirectory
	print('Client ' +str(addr[1])+' home directory is: ' + newdirectory)
	#infinite loop so that function does not terminate and thread does not end.
	while True:
		
		#Receiving from client
		data = conn.recv(1024)
		information = data.upper()  #set all to uppercase for ease of use
	#	homedirectory=os.getcwd()
	#	newdirectory=homedirectory
	#	print '%s' % data
	#	if not data: 
	#		break
		if information == 'BYE':
			print str(addr[1])+': Client disconnected, closing socket.'
			conn.close()
			break
		elif information[:2] == 'CD':
			try:
				#os.chdir(newdirectory+'/'+ str(data[3:]))  Not needed.  listdir returns os errors
				if information[3:] == "..":  #allows backwards travel to make the newdirectory string look correct
					os.listdir(newdirectory + '/' + str(data[3:]))
					newdirectory= os.path.dirname(newdirectory)
					print str(addr[1])+': Client changed directory'
					conn.sendall(newdirectory)
				else:
					os.listdir(newdirectory + '/' + str(data[3:]))
					newdirectory= newdirectory + '/' + str(data[3:])
					print str(addr[1])+': Client changed directory'
					conn.sendall(newdirectory)
				#os.chdir(homedirectory)   Not needed.  listdir returns os errors
			except OSError, msg:
				print str(addr[1])+': Directory Error: ' + msg[1]
				conn.sendall('Directory Error: ' + msg[1])
		elif information[:3] == 'DIR' :	
			conn.sendall(str(os.listdir(newdirectory)))
			
		elif information[:8] == 'DOWNLOAD' and (data[9:] != None) :
			filenamed= data[9:]
			if os.path.isfile(homedirectory+'/'+filenamed):
				conn.sendall('overwrite')
				print(str(addr[1])+': Asking to Overwrite.')
				downloadfunction(newdirectory, data)
			elif os.path.isfile(newdirectory+'/'+filenamed) != True:
				print('Bad File Name')
				conn.sendall('badname')
			else:
				conn.sendall('nope')
				downloadfunction(newdirectory, data)

			
		else :
			print str(addr[1])+': Bad Command'
			conn.sendall('Bad Command please retry')
	
	#came out of loop
	conn.close()

#now keep talking with the client
try:
	while 1:
    #wait to accept a connection - blocking call
		conn, addr = s.accept()
		print 'Connected with ' + addr[0] + ':' + str(addr[1])
	
	#start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
		start_new_thread(clientthread ,(conn,))
except KeyboardInterrupt:  #Close the socket when user hits Ctrl-C
	s.close()
	print '\nClosing sockets and exiting'
	sys.exit()
