"""
setup.py

This script will scan your network for the
Tinny Message Queue Manager ( tmqm ) program,
and will save the IP address to a local text file
called TMQM-HostIP.txt.

The Client programs can then uses this info to send
messages and data between each other. 

The Host program ( tmqm ) should be started on a computer
on this WiFi router, before you run this script.

If for any reason the IP address of the host computer should
change, just run this script again to update the text file.

This work is licensed under the Creative Commons Attribution 4.0 International License.
To view a copy of this license, visit 
http://creativecommons.org/licenses/by/4.0/
or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

You are free to use this file in your own projects as long as you follow a
few simple rules. See license above for details. 

For documentation see:
https://www.gsw7.net/files/tmqm/readme.md   

"""
import socket, sys, os, time, threading

def _Check4Conn(ip,port):
    global hostIP
    try:
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.settimeout(5)
      if sock.connect_ex((str(ip), port)) == 0: hostIP = ip  
    except:
      pass
    try:
      sock.close()
    except:
      pass

def scan(mask):
    for x in range(1,255):
      testIP = mask.replace("x", str(x).strip() )
      #print( testIP )
      threading.Thread(target=_Check4Conn, args=(testIP,65432)).start()
    time.sleep(10)
    return True


if __name__ == "__main__":
   hostIP = ""
   print( __doc__ )
   print("Now scanning for the Host.")
   print("This may take a few minutes.\n")
   
   scan("192.168.0.x")
   if hostIP == "": scan("192.168.1.x")  
   if hostIP == "": scan("192.168.2.x")
   if hostIP == "": scan("192.168.3.x")
   
   if hostIP == "":
     print("Sorry, I was unable to find the Host.")
     print("Please ensure that the the Host ( C++ program tmqh.cpp )")
     print("  is running and try again.")
   else:
     print("The Host was found on " + hostIP )
     filename = "TMQM-HostIP.txt"
     open(filename,"w").write(hostIP)
     
# End of code.
