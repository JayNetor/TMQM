"""
example2.py
Written by Joe Roten, 2023/07/19

Note: This script is intended to run so that it's output is sent to
the screen, not an IDE window. So to run this script:
  python ./example2.py

The Host program (tmqm) needs to be running on this computer,
or on another computer on the same WiFi network.
Also, you need to run setup.py before running this
example script.

This work is licensed under the Creative Commons Attribution 4.0 International License.
To view a copy of this license, visit 
http://creativecommons.org/licenses/by/4.0/
or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

You are free to use this script as a starting point to create your own,
as long as you follow a few simple rules. See license above for details. 

For documentation see:
https://www.gsw7.net/files/tmqm/readme.md   

"""

# The file pytmqm.py needs to be either in the
# current directory, or in a folder that is on
# Python module path.

import pytmqm
import time
import datetime

# Escape codes to print in colors on the screen.
dGreen = chr(27) + "[92m"
dYellow = chr(27) + "[93m"
dBlue = chr(27) + "[94m"
dRed = chr(27) + "[91m"
dWarning = chr(27) + "[5m" + chr(27) + "[97;101m"
dReset = chr(27) + "[0m" 


if __name__ == "__main__":

 # Start the client.
 # Note: These are double Under-Lines, not just '_'.
 mq = pytmqm.Client( __file__ )

 # Join "console" and "logging" channels.
 mq.join( "console", "logging" )

 # Change my client-ID to 'console'.
 mq.alias( "console" )

 while True:

   # Sleep for 2 seconds.
   # Allow other proccesses a chance to run.
   time.sleep(2)
   
   while mq.fetch():
     now = datetime.datetime.now()
     iso = now.strftime("%H:%M:%S")

     # Show the message on the screen, in color.
     print( f"{dGreen}{iso}: {dBlue}{mq.From} --> {mq.To} {dReset}", end="")
     if mq.Text.startswith("!"): print( f"{dWarning}WARNING {dReset}", end="" )
     if mq.Text.startswith("+"): print( dGreen, end="" )
     if mq.To == "console": print( dYellow, end="" )
     print( f"{mq.Text}{dReset}" )        


     # Record anything sent to channel 'logging' to the logs.
     if mq.To == "logging":
       print("** logging: " , mq.Text )
       # Add code here to record mq.Text to your logs.



    # Add code here to do anything else to this message.


        
   # End of fetch() loop.



   # Examples of timmers and scheduling events.
   
   # Broadcast a 'heartbeat' message every 60 seconds.
   # Just to tell all others that this one is still running.
   if mq.onTimmer("timmer01", 60 ):
     mq.send("public", f"+heartbeat, {mq.Name}, {mq.IP}" )

   # Broadcast a '+signal' at 5 minutes past the hour, every hour.      
   if mq.onTrigger("schedule02", now.minute == 5 ):
     mq.send("public", f"+signal, schedule02, {mq.Name}, {mq.IP}" )  

   # Broadcast a '+signal' at 6:00am every Monday morning.
   if mq.onTrigger("schedule03", now.hour == 6 and now.weekday == 1 ):
     mq.send("public", f"+signal, schedule03, {mq.Name}, {mq.IP}" )  



# End of code.

