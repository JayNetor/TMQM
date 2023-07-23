"""
pytmqm.py
version 4.0.0
Written by Joe Roten
Last Updated: 2023/07/19

This file contains the Python Client class for the
Tinny Message Queue Manager.

This Class will allow clients to pass messages
and data between each other.

This work is licensed under the Creative Commons Attribution 4.0 International License.
To view a copy of this license, visit 
http://creativecommons.org/licenses/by/4.0/
or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

You are free to use this file in your own projects as long as you follow a
few simple rules. See license above for details. 

For documentation see:
https://www.gsw7.net/files/tmqm/README.html

"""

class Client():

    import socket as _socket
    import sys as _sys
    import os as _os
    import time as _time

    # Object names that start with uppercase letters
    #   are variables accessable by the parent.

    # Object names that start with lowercase letters
    #   are functions accessable by the parent.

    # Object names that start with '_' are hidden
    #   from the parent.

    Version = "4.0.0"

    To = "None"    # Message To address
    From = "None"  # Message From address
    Text = "None"  # Message body.

    Name = "Unknown" # Will hold filename of parent script.
    Index = "0"      # Messages in the Queue use an Index.
    IP = "None"      # Will hold the IP address of this client.
    ID = "noReply"   # Will hold the client-ID string.
    HostIP = "None"  # Will hold the IP address of the Host.
    Channels = ""    # A comma delimited string of Channels.
    
    _channels = [ 'public', 'all' ]
    _myData = {}
    _AutoReplyFlag = True


    def query( self, m, timeout=10, debug=False ):
      """Send a string to the Host, and recieve a reply. """
      reply = ",,,"
      if debug: print("client: " + m)
      try:
        with self._socket.socket( self._socket.AF_INET, self._socket.SOCK_STREAM) as s:
          s.settimeout( timeout )  
          s.connect( ( self.HostIP, 65432 )  )
          s.sendall( bytes( str(m).encode() ))
          reply = s.recv(1024).decode()
          s.close()
      except Exception as e:
        reply = "Error: " + str(e)
      if debug: print("host: " + reply )  
      return reply.strip()

    def send(self, To, Text, From="me"):
      """Broadcast a message to other clients. Will return 'OK' if sucessful. """
      if To.lower() == "me": To = self.ID
      if From.lower() == "me": From = self.ID
      return self.query( f"send,{To},{From},{Text}" )

    def recv(self):
      """Retrieve next message from the queue. Returns True if successful. """
      # Message values are returned in self.To, self.From, self.Text, self.Index
      responce = self.query( "recv," + self.Index.strip() )
      if not responce.startswith("Error:"):  
        ( self.Index, self.To, self.From, self.Text ) = responce.split(",",3)
        if self._AutoReplyFlag: self._autoReply()
      return ( self.From != "None" )

    def fetch(self):
      """Retrieve next message that is intended for ME. Returns True if successful. """
      # This is nothing more than a filter loop based on recv().
      # Message values are returned in self.To, self.From, self.Text, self.Index
      self._AutoReplyFlag = False   # Tells recv() to NOT autoReply.
      while self.recv() :
        if self.To in self._channels:
          self._autoReply()  # autoReply only if its a match.
          break    # We have a match, break out of the loop.
      self._AutoReplyFlag = True   # Tells recv() next call is safe to autoReply.  
      return ( self.From != "None" )

    def join(self, *arguments):
        """Add one or more channels to the list that fetch() is monitoring. """
        for channelName in arguments:
          channelName = str( channelName ).strip()  
          if not channelName in self._channels:
             self._channels.append( channelName )
        self.Channels = ", ".join( self._channels )     
        return True   

    def drop(self, *arguments):
        """Remove one or more channels from the list that fetch() is monitoring. """
        for channelName in arguments:
          channelName = str( channelName ).strip()  
          if channelName in self._channels:
             self._channels.remove( channelName )
        self.Channels = ", ".join( self._channels )     
        return True

    def dropall(self):
        """Remove ALL of the channels from the list that fetch() is monitoring. """
        self._channels = []
        self.Channels = ""
        return True

    def alias(self, Name):
        """Change the client-ID from the default, to the given string. """
        Name = str( Name ).strip()
        self.send("public", f"Client {self.ID} is changing it's client-ID to '{Name}'.")
        self.send("public", f"+redefind , client , {Name} , {self.Name} , {self.IP}")
        self.ID = Name
        self.join( Name )
        return True

    def isHostUp(self):
        """Will return True if the Host is responding to requests. """
        return ( not "Error" in self.query("helo") )

    def bye(self):
        """Tell the other clients on the network that we are leaving. """
        self.send( "public", f"+bye, {self.Name}, {self.IP}" )
        return True

    def onTrigger(self, Name, Value):
        """Returns True if, and only if, Value changes from False to True. """
        # See:  https://en.wikipedia.org/wiki/If_and_only_if
        Name = "trigger." + str(Name).strip()
        P = bool( Value )
        Q = self._myData.get(Name,True)
        answer = False
        if P and not Q:
          answer = True
          self._myData[Name] = True
        if not P:
          self._myData[Name] = False  
        return answer

    def onTimmer(self, Name, Seconds, Offset=0):
        """Will return True once every X seconds. """
        Seconds = float( Seconds ) # Insure its a number
        Offset =  float( Offset )
        Epoch = self._time.time()
        x1 = ( Epoch + Offset ) % Seconds 
        x2 = Seconds / 2         
        return self.onTrigger(Name, ( x1 < x2 ) )

    def _autoReply(self):
        """Automatically takes care of any ping or echo requests. """
        m = self.Text 
        if m.startswith("+ping"): 
          self.send( self.From, f"+pong, {self.Index}, {self.Name}, {self.IP}")
          self.send( "me", f"A reply to +ping request was sent to {self.From}. Message ID: {self.Index}." )
        if m.startswith("+echo") and len(m)>6:      
          self.send( self.From, "+reply" +  m[5:] )
          self.send( "me", f"A reply to a +echo request was sent to {self.From}. Message ID: {self.Index}." )
        return True


    def __init__(self, name=""):

      # Get the IP address of the Host.
      filename = "TMQM-HostIP.txt" # Created by setup.py
      if self._os.path.exists(filename):
        self.HostIP = open(filename,"r").read()
      else:
        print("Error: Unable to find file " + filename)
        print("Please run setup.py to create this file.")
        self._sys.exit(0)

      # Will return the filename of the parent script.  
      # This is passed to init() by '__file__' in __main__.
      if name != "":
        self.Name = self._os.path.basename( name ) 

      # Check the connection to the Host.
      if "Error" in self.query("helo"):
        print("Sorry, the Host is not responding.")
        self._sys.exit(0)
    
      # Get the client info from the Host.
      (self.ID, self.Index, self.IP) = self.query("init").split(",",3)

      # Define the channels to be monitored by fetch().
      self._channels = [ 'public', 'all', self.ID, self.IP, self.Name ]
      self.Channels = ", ".join( self._channels )

      # Finally, Introduced ourselfs to the other clients on the network.
      self.send("public",   f"+startup , {self.Name} , {self.IP}"   )

      # End of init()
      
# End of Class Client.


if __name__ == "__main__":
    print( __doc__ )
    
# End of code.
