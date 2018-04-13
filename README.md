# EventGhost-Marantz_HTTP_Plugin
EventGhost Plugin to Control 2012 and newer Marantz Recievers via HTTP (mulitple controllers allowed)

I used the MarantzTCPPlugin as a template, and replaced all the telnet communications functions with HTTP requests.

Using HTTP allows multiple controllers to access the receiver at the same time, as opposed to the single-connection telnet interface used by MarantzTCPPlugin. Oddly, HTTP actually seems to be faster; strange because telnet holds the connect open, while HTTP does not (and also has a much higher data overhead).

END-USERS:
Just download and double-click on Marantz HTTP-0.1.egplugin, which will immediately install the plugin into EventGhost.  You'll have to provide the IP address of your receiver, add the plugin to your EventGhost project, and then add Marantz TCP/telnet actions like "MVUP" for volume up, and "SIBD" for selecting Blu-ray input. There are also some built-in actions that don't require using command codes, and the volume one lets you specify volume with more intuitive values.

You can see all the supported TCP/telnet commands at: http://us.marantz.com/DocumentMaster/US/Marantz_AV_SR_NR_PROTOCOL_V01.xls

DEVELOPERS:
Developers might add new built-in commands, maybe some better error detection, and even communications from the receiver back to EventGhost. I'll merge any useful branches into the master.
