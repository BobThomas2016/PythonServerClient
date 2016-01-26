#************************************************************************
#*  NAME:  Robert Thomas						
#*  Course:  CSC328							
#*  Instructor:  Dr. Frye						
#*  Assignment:  Concurrent TCP Client and Server				
#*  DUE DATE: 11/30/2015							
#*  Filename:  client.py							
#*  Purpose:  The purpose of these two programs is to create a concurrent TCP
#*		server and client.				
#************************************************************************


COMPILE INSTRUCTIONS:
Server:		Type python server.py <[port]>
Client:		Type python client.py <address> <[port]>

The port number on both the client side and server side is optional.  The client
side needs a host to connect to.  During my testing I used localhost.  

When the client connects to the server the server will send a hello instruction
along with instructions on what commands are viable.  The viable commands are
CD, DIR, DOWNLOAD, BYE.  These commands are preferably typed in capital letters
but the client and the server will both take the commands entered, convert them
to uppercase characters via .upper() to always look for an uppercase command, so
the commands are not actually case sensitive.

I chose to use threads for this assignment, using threads on demand, so that 
whenever a client connects it is automatically given its own thread to use.
The problem that I ran into with this choice was that python does not have a 
thread safe change directory command.  Every time any client changes their directory
it will change the directory of all of the threads.  

To get around this issue, when the client connects to the server, the server 
generates the new thread and gets the home directory from the client.  This 
directory is stored as newdirectory for later use.  By using listdir commands we
are able to "change" directories by updating newdirectory to the new value.  This
also allows us to travel backwards by using os.path.dirname when the client enters
CD '..' minus the single quotes.  the listdir and dirname command should both 
provide OSErrors if trying to access a bad directory, and that error is sent to the 
client.

To display the current directory we simply send listdir over the socket to the
client who prints out the buffer information.  There did not seem to be a need for 
letting the client know when the data was done transmitting.  I tried on many 
different directories and never had the listing get truncated.  The listdir command
starts and ends the directory commands with [ and ] respectively.

For downloading a file, the server sends the request to the server, which then checks
to see if that filename already exists in its home directory.  If the file does
exist it sends a request to the client for overwrite permission.  If the client 
consents then the download process begins, otherwise a termination message is sent 
to the server and the client breaks the loop to go back to waiting for more input.
If the file does not exist it simply downloads.  If the filename does not exist
that the user is attempting to download, then the server sends a bad filename notice
to the client who then alerts the user and returns to waiting on commands.

Instead of going line by line with the download I chose to do the download by sending
the filesize to the client first.  The client then uses this information to enter
a while loop where it will loop until it has gotten all of the bytes that the server
said the filesize was.

When the client sends the BYE command, the client closes the socket, as does the server.
The bye command is also transmitted and the socket closed when the client does a 
keyboard interrupt.
