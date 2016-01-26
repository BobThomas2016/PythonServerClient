#************************************************************************
#*  NAME:  Robert Thomas						
#*  Course:  CSC328							
#*  Instructor:  Dr. Frye						
#*  Assignment:  TCP Client				
#*  DUE DATE: 12/6/2015							
#*  Filename:  client.py							
#*  Purpose:  The purpose of this program is to create a client that connects
#*		to a server designated by the user and communicates with it.
#*		User will be able to input commands:  CD, DIR, and
#*		DOWNLOAD to allow the user to change directory, view the 
#*		files of the current directory and download a specified file.
#*  COMPILE INSTRUCTIONS: Type python client.py <address> <[port]> 						
#************************************************************************
import socket
import sys
import os
import shutil

#if no arguments are passed in then we cannot connect, let them know the format
if len(sys.argv)<2:
	print >>sys.stderr, 'Please use the format: %s <address> <[port]>\n' % sys.argv[0]
	sys.exit()

from sys import argv
# Script and Host only passed, set Port to 55536
if len(sys.argv)==2:
	script, addr = argv
	port=55536

# Script, Host and Port all passed in, set the values
if len(sys.argv)==3:
	script, addr, port = argv

	
def DownloadScript(filename):
	if '/' in filename:
		dir = os.path.dirname(filename)
		try:
			os.stat(dir)
		except:
			print('Directory does not exist. Creating directory.')
			os.mkdir(dir)
	f = open('tempfile', 'w+')
	print('Filename: ' + filename)
	while True:
		sock.sendall('getfile')
		size = int(sock.recv(16))
		print('Total size: ' + str(size))
		#path = str(sock.recv(64))
		#print(path)
		recvd = ''
		while size > len(recvd):
			data = sock.recv(1024)
			if not data: 
				break
			recvd += data
			f.write(data)
		break
	sock.sendall('end')
	print('File received.')
	f.close()
	shutil.copy('tempfile', filename)  # shutil.copy('tempfile', str(directory)+'/'+filename)  will allow copy into the same folder as the file.
	os.remove('tempfile')


def overwriteclause(filename):
#	sock.send('exists')
#	overwrite=sock.recv(16)  			#These 3 lines did extra sends and receives that I have deemed not necessary.
#	if overwrite == 'overwrite':		#Don't need to send to the server to let them know about overwriting, just check clientside
	response = raw_input('Do you want to overwrite the current file:  ')
	#print(response.upper())			#making sure I received the information correctly
	if response.upper() == ('N' or 'NO'):
		sock.sendall('stop')
		print("Terminating file transfer")
	elif response.upper() == ("Y" or 'YES'):
		DownloadScript(filename)	
		
		
# Create a TCP/IP socket
try:
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error , msg:
	print 'Socket failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	sys.exit()

# Connect the socket to the port on the server given by the caller converting string to int for port
server_address = (addr, int(port))
try:
	sock.connect(server_address)
except socket.error , msg:
	print 'Connect failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	sys.exit()

		
# Connection, should get a hello from server
try:
	data = sock.recv(1024)
	print >>sys.stderr, '%s' % data
	_directory = os.getcwd()
	sock.send(os.getcwd())
	while 1:
		ClientString = raw_input("Command: ") 
		download = ClientString[:8]
		cd = ClientString[:2]
		if ClientString.upper() == "BYE":
			sock.sendall('BYE') 
			sock.close()
			break
		elif download.upper() == "DOWNLOAD":
			sock.send(ClientString)
			filename = ClientString[9:]
			overwrite=sock.recv(16)
			if overwrite == 'overwrite':
				overwriteclause(filename)
			elif overwrite == 'badname' :
				print('Bad File Name')
			else:	
				DownloadScript(filename)
		elif cd.upper() == "CD":	
			sock.send(ClientString)
			directory = sock.recv(1024)		#this saves the current directory for use in other functions if desired
			print >>sys.stderr, '%s' % directory
		else:
			sock.sendall(ClientString)
			data = sock.recv(1024)
			print >>sys.stderr, '%s' % data
except KeyboardInterrupt:  #Close the socket when user hits Ctrl-C
	sock.sendall('BYE')
	sock.close()
	print '\nClosing sockets and exiting'
	sys.exit()
