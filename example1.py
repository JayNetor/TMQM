"""
example1.py
Written by Joe Roten, 2023/07/19

This is a simple TMQM Client in Python.

Tinny Message Queue Manager (TMQM) allows clients
to 'broadcast' messages and data, to ALL the other clients
on the network. 

The Host program (tmqm) needs to be running on this computer,
or on another computer on the same WiFi network.
Also, you need to run setup.py before running this
example srript.

This work is licensed under the Creative Commons Attribution 4.0 International License.
To view a copy of this license, visit 
http://creativecommons.org/licenses/by/4.0/
or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

You are free to use this script as a starting point to create your own,
as long as you follow a few simple rules. See license above for details. 

For documentation see:
https://www.gsw7.net/files/tmqm/README.html 

"""

# The file pytmqm.py needs to be either in the
# current directory, or in a folder that is on
# Python module path.

import pytmqm

if __name__ == "__main__":

    # Start the client.
    # Note: These are double Under-Lines, not just '_'.
    mq = pytmqm.Client( __file__ )


    # Show some information about the client.
    print("My client ID is: ", mq.ID )
    print("The current Index is: ", mq.Index )
    print("My IP address is: ",mq.IP )
    print("My script name is: ",mq.Name )
    print("This host's IP is: ", mq.HostIP )
    print("My channels are: ", mq.Channels )
    # Note that the next one is a function, not a value.
    print("Is the host running: ", mq.isHostUp() )
    print( "----------------")


    print( "--------------- Working with channels.")

    # Remember that client names are case-sensitive.
    # Also see the dropall() function.

    # Add 'group5' to the list of channels.
    mq.join( "group5" )

    # Remove 2 channels ( if they are being monitored ).
    mq.drop( "group6", "floor5" )

    print("My channels are now: ", mq.Channels )



    # Change my client-ID from the default, to a new string.
    # This is optional. Just makes the console a bit easier
    #   to read.
    mq.alias("Test-Client-One")


    
    print( "---------------- Sending a few test messages.")

    # Examples of a few test messages.
    mq.send( "public",  "Test sent to the 'public' channel." )
    mq.send( "me",  "This message is sent only to myself." )
    mq.send( mq.ID,  "Another message sent only to myself." )
    mq.send( mq.IP,  f"This message is sent to clients on computer {mq.IP}." )
    mq.send( "group7",   "Test message sent to clients in 'group7'." )
    mq.send( "group5",   "Test message sent to clients in 'group5'." )
    mq.send( "console",  "Test message sent to the 'console'." )
    mq.send( "147",  "Test message sent to client who's ID is 147." )
    mq.send( "noReply",  "No one will recieve this message." )
    mq.send( mq.Name,  f"Test message sent to all instances of {mq.Name}." )
 
    # Send a '+ping' to all the other clients on the network. 
    # Note that the first 5 character of the text is '+ping'.
    # This will trigger a '+pong' message from the other clients.
    mq.send( "all", "+ping, A +ping request to all clients." )
    
    # Testing to see if any other instances of this script are running
    #   on any other computer on the network, by using 'echo'.
    # Each reply will have a different Message.From value (client ID).
    mq.send( mq.Name, f"+echo: Testing for {mq.Name}" )



    print( "---------------- Pending messages sent to ME.")

    # Retrieve next messages from the queue that are intended for ME
    #   or were sent to a channel that is in my list of channels.
    # Note the difference between fetch() and recv().
    while mq.fetch():
      print( f"Message: [{mq.To}], <{mq.From}>, {mq.Text} " )



    print( "---------------- Pending messages sent to ANYONE.")

    # Retrieve next message from the queue, reguardless if they are
    #   itended for me or not.
    while mq.recv():
      print( f"Message: [{mq.To}], <{mq.From}>, {mq.Text} " )



    print( "---------------- Dump the entire queue:")

    # Retrieve EVERYTHING from the queue, from top to bottom,
    #  reguardless if you have alreay recieved it,
    #  or of 'To' who it was sent.
    # Remember that messages will 'expire' out of the queue
    #  when they are 10 minutes old.
    
    mq.Index = "0" # Set the Index to the top of the queue.
    while mq.recv():
      print( f"Message: [{mq.To}], <{mq.From}>, {mq.Text} " )



    print( "---------------- BYE.")

    # Let all other clients know we are leaving. 
    # This is optional, but is 'best practices' to do so.
    mq.bye()

# End of code.

