# EventGhost-Marantz_HTTP_Plugin
EventGhost Plugin to Control 2012 and newer Marantz Recievers via HTTP (mulitple controllers allowed)

I used the MarantzTCPPlugin as a template, and replaced all the communications functions with HTTP requests.

Using HTTP allows multiple controllers to access the receiver at the same time, as opposed to the single-connection telnet interface used by MarantzTCPPlugin.

If you're simply an end-user, just download and double-click on Marantz HTTP-0.1.egplugin, which will immediately install the plugin into EventGhost.  You'll have to provide the IP address of your receiver, add the plugin to your EventGhost project, and then add Marantz HTTP actions.

You can see all the supported telnet commands at: http://us.marantz.com/DocumentMaster/US/Marantz_AV_SR_NR_PROTOCOL_V01.xls
