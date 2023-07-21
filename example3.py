"""
example2.py

This is a 'bare-bone' example of a TMQM client written in Python. 

I recomend that you also look at example1.py for a more 'usable'
example.

Please feel free to uses this file as a starting point
to create your own clients.

This work is licensed under the Creative Commons Attribution 4.0 International License.
To view a copy of this license, visit 
http://creativecommons.org/licenses/by/4.0/
or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

You are free to use this file in your own projects as long as you follow a
few simple rules. See license above for details. 

For documentation see:
https://www.gsw7.net/files/tmqm/readme.md   

"""
import socket, sys, os


# Get the IP address of the Host.
filename = "TMQM-HostIP.txt" # Created by setup.py
hostIP = ""
if os.path.exists(filename):
  hostIP = open(filename,"r").read()


# Example of sending a message.
m = "send,public,noReply,This is a test message sent to 'public'."
with socket.socket( socket.AF_INET, socket.SOCK_STREAM) as s:
  s.settimeout( 10 )   
  s.connect( ( hostIP, 65432 )  )
  s.sendall( bytes( str(m).encode() ))
  reply = s.recv(1024).decode()
  s.close()
  print( reply )


# Recieve all messages in the queue.
# This will include messages that were sent BEFORE
#   this script started, but have not yet expired. 
(Index, To, From, Text ) = ("0","","","")
while To != "None":
  with socket.socket( socket.AF_INET, socket.SOCK_STREAM) as s:
    s.settimeout( 10 )
    s.connect( ( hostIP, 65432 )  )
    s.sendall( bytes( str( "recv," + Index ).encode() ))
    reply = s.recv(1024).decode()
    s.close()
    (Index, To, From, Text ) = reply.split(",",3)
    print( reply )

    
# End of code.
        
