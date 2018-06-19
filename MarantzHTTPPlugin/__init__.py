# -*- coding: utf-8 -*-
#
# plugins/MarantzHTTP/__init__.py
#
# This file is a plugin for EventGhost designed to control supported Marantz (and probably Denon) AV Receivers via HTTP.
# HTTP is more flexible than Telnet, because HTTP can maintain multiple connections, rather than the held-open, singular Telnet
#
# Original TCP/IP plugin  by Sam West <samwest.spam@gmail.com> # and Daniel Eriksson <daniel@clearminds.se>
#
#===============================================================================

import eg, sys, urllib, time
import new
import xml.dom.minidom
from xml.dom.minidom import parse

eg.RegisterPlugin(
    name = "Marantz HTTP",
    author = "Mark Bernard",
    original_author = "Daniel Eriksson <daniel@clearminds.se>",
    version = "0.1.0",
    kind = "external",
    description = "Controls Marantz Receivers Using HTTP.  Currently provides methods for sending arbitrary text commands using the Denon/Marantz telnet command set, but over an HTTP connection to allow multiple connections."+
                  "<p>See <a href=http://us.marantz.com/DocumentMaster/US/Marantz_AV_SR_NR_PROTOCOL_V01.xls>here</a> for a full list of supported commands. "+
                  "<p>Supported Marantz models include: AV7005, SR7005, SR6006, SR6005, SR5006, NR1602 (and probably others with an ethernet connection). "+
                  "<p>Might also support (untested) Denon models: AVR-3808, AVC-3808, command list <a href=http://usa.denon.com/US/Downloads/Pages/InstructionManual.aspx?FileName=DocumentMaster/US/AVR-3808CISerialProtocol_Ver5.2.0a.pdf>here</a>.",
    createMacrosOnAdd=False
)

# Define commands
# (name, title, description (same as title if None), command)
commandsList = (
    ('Power',
        (
            ('PowerOn', 'Power on', None, '/power on', 'PWON'),
            ('PowerOff', 'Power off', None, '/power off', 'PWSTANDBY'),
        )
    ),

    ('Input',
        (
            ('InputPhono', 'Select Phono input', None, '/input phono', 'SIPHONO'),
            ('InputCD', 'Select CD input', None, '/input cd', 'SICD'),
            ('InputDVD', 'Select DVD input', None, '/input dvd', 'SIDVD'),
            ('InputBD', 'Select BD input', None, '/input bd', 'SIBD'),
            ('InputTV', 'Select TV input', None, '/input tv', 'SITV'),
            ('InputSAT/CBL', 'Select SAT/CBL input', None, '/input sat/cbl', 'SISAT/CBL'),
            ('InputSAT', 'Select SAT input', None, '/input sat', 'SISAT'),
            ('InputVCR', 'Select VCR input', None, '/input vcr', 'SIVCR'),
            ('InputGame', 'Select Game input', None, '/input game', 'SIGAME'),
            ('InputV.Aux', 'Select V.Aux input', None, '/input v.aux', 'SIV.AUX'),
            ('InputTuner', 'Select Tuner input', None, '/input tuner', 'SITUNER'),
            ('InputCDR', 'Select CDR input', None, '/input cdr', 'SICDR'),
            ('Input AUX1', 'Select AUX1 input', None, '/input aux1', 'SIAUX1'),
            ('Input AUX2', 'Select AUX2 input', None, '/input aux2', 'SIAUX2'),
            ('Input NET/USB', 'Select NET/USB input', None, '/input net/usb', 'SINET/USB'),
            ('Input M-XPORT', 'Select M-XPORT input', None, '/input m-xport', 'SIM-XPORT'),
            ('Input USB/IPOD', 'Select USB/IPOD input', None, '/input usb/ipod', 'SIUSB/IPOD'),
            ('Input MPLAY', 'Select MPLAY input', None, '/input mplay', 'SIMPLAY'),
        )
    ),

    ('Input mode',
        (
            ('InputmodeAuto', 'Inputmode auto', 'Sets inputmode to auto', '/inputmode auto', 'SDAUTO'),
            ('InputmodeAnalog', 'Inputmode analog', 'Sets inputmode to analog', '/inputmode analog', 'SDANALOG'),
            ('InputmodeHdmi', 'Inputmode HDMI', 'Sets inputmode to HDMI', '/inputmode hdmi', 'SDHDMI'),
            ('InputmodeDigital', 'Inputmode digital', 'Sets inputmode to digital', '/inputmode digital', 'SDDIGITAL')
        )
    ),

    ('Surround mode',
        (
            ('SurroundAuto', 'Select Auto surround mode', None, '/surround auto', 'MSAUTO'),
            ('SurroundStereo', 'Select Stereo surround mode', None, '/surround stereo', 'MSSTEREO'),
            ('SurroundMulti', 'Select Multi Channel Stereo surround mode', None, '/surround multi', 'MSMCH STEREO'),
            ('SurroundVirtual', 'Select Virtual surround mode', None, '/surround virtual', 'MSVIRTUAL'),
            ('SurroundDirect', 'Select Pure Direct surround mode', None, '/surround direct', 'MSDIRECT'),
            ('SurroundDolby', 'Select Dolby surround mode', None, '/surround dolby', 'MSDOLBY DIGITAL'),
            ('SurroundDolbyDigitalEx', 'Select Dolby Digital EX surround mode', None, '/surround ddex', 'MSDOLBY DIGITAL'),
            ('SurroundDolbyProLogic', 'Select Dolby ProLogic surround mode', None, '/surround dpl', 'MSDOLBY PRO LOGIC'),
            ('SurroundDTS', 'Select DTS surround mode', None, '/surround dts', 'MSDTS SURROUND'),
            ('SurroundDTSES', 'Select DTS ES surround mode', None, '/surround dtses', 'MSDTS SURROUND'),
        )
    ),

    ('HDMI Out',
        (
            ('HDMIMonitorOut-1', 'Sets Monitor to HDMI 1', None, '/hdmi out-1', 'VSMON1'),
            ('HDMIMonitorOut-2', 'Sets Monitor to HDMI 2', None, '/hdmi out-2', 'VSMON2'),
            ('HDMIMonitorOut-Auto', 'Sets Monitor to Auto', None, '/hdmi auto', 'VSMONAUTO'),
        )
    ),

    ('HDMI Audio Decode',
        (
            ('HDMIAudioDecodeAmp', 'Audo to AMP', 'Sets the HDMI Audio to the AMP', '/audio amp', 'VSAUDIOAMP'),
            ('HDMIAudioDecodeTV', 'Audo to TV', 'Sets the HDMI Audio to the TV', '/audio tv', 'VSAUDIOTV'),
        )
    ),

    ('Mute',
        (
            ('MuteOn', 'Mute on', None, '/mute on', 'MUON'),
            ('MuteOff', 'Mute off', None, '/mute off', 'MUOFF'),
        )
    ),

    ('Zone2 HDMI Commands',
        (
            ('Z2PowerOn', 'Zone2 Power on', None, '/power on', 'Z2ON'),
            ('Z2PowerOff', 'Zone2 Power off', None, '/power off', 'Z2OFF'),
            ('Z2Status', 'Zone2 Status', None, '/status', 'Z2?'),
            ('Z2InputPhono', 'Zone2 Phono input', None, '/input phono', 'Z2PHONO'),
            ('Z2InputCD', 'Zone2 CD input', None, '/input cd', 'Z2CD'),
            ('Z2InputDVD', 'Zone2 DVD input', None, '/input dvd', 'Z2DVD'),
            ('Z2InputBD', 'Zone2 BD input', None, '/input bd', 'Z2BD'),
            ('Z2InputMPLAY', 'Zone2 MPLAY input', None, '/input mplay', 'Z2MPLAY'),
            ('Z2InputSAT/CBL', 'Zone2 SAT/CBL input', None, '/input sat/cbl', 'Z2SAT/CBL'),
            ('Z2InputSAT', 'Zone2 SAT input', None, '/input sat', 'Z2SAT'),
            ('Z2InputVCR', 'Zone2 VCR input', None, '/input vcr', 'Z2VCR'),
            ('Z2InputGame', 'Zone2 Game input', None, '/input game', 'Z2GAME'),
            ('Z2InputV.Aux', 'Zone2 V.Aux input', None, '/input v.aux', 'Z2V.AUX'),
            ('Z2InputTuner', 'Zone2 Tuner input', None, '/input tuner', 'Z2TUNER'),
            ('Z2InputCDR', 'Zone2 CDR input', None, '/input cdr', 'Z2CDR'),
            ('Z2Input AUX1', 'Zone2 AUX1 input', None, '/input aux1', 'Z2AUX1'),
            ('Z2Input AUX2', 'Zone2 AUX2 input', None, '/input aux2', 'Z2AUX2'),
            ('Z2Input NET/USB', 'Zone2 NET/USB input', None, '/input net/usb', 'Z2NET/USB'),
            ('Z2Input M-XPORT', 'Zone2 M-XPORT input', None, '/input m-xport', 'Z2M-XPORT'),
            ('Z2Input USB/IPOD', 'Zone2 USB/IPOD input', None, '/input usb/ipod', 'Z2USB/IPOD'),
        )
    ),
)


class SetVolumeAbsolute(eg.ActionBase):
    name='Set absolute volume'
    description='Sets the absolute volume'

    def __call__(self, volume):
        return self.plugin.setVolumeAbsolute(volume)

    def GetLabel(self, volume):
        return "Set Absolute Volume to %d" % volume

    def Configure(self, volume=25):
        panel = eg.ConfigPanel(self)

        valueCtrl = eg.SmartSpinIntCtrl(panel, -1, 0, min=0)
        panel.AddLine("Set absolute volume to", valueCtrl)
        while panel.Affirmed():
            panel.SetResult(valueCtrl.GetValue())


class MarantzAction(eg.ActionClass):

    def __call__(self):
        self.plugin.sendCommand(self.cmd)

''' Sends a raw text command to the receiver.  See http://us.marantz.com/DocumentMaster/US/Marantz_AV_SR_NR_PROTOCOL_V01.xls for details '''
class SendCommandText(eg.ActionBase):
    name='Send Text Command'
    description='Send a manual command'

    def __call__(self, cmd):
        print 'Sending command: '+cmd
        return self.plugin.sendCommand(str(cmd))

    def GetLabel(self, cmd):
        return "Send Command '%s'" % cmd

    def Configure(self, volume=25):
        panel = eg.ConfigPanel(self)

        cmdCtrl = wx.TextCtrl(panel,-1, '')
        desc = wx.StaticText(panel,-1, 'See http://us.marantz.com/DocumentMaster/US/Marantz_AV_SR_NR_PROTOCOL_V01.xls for a list of commands')

        panel.AddLine(desc)
        panel.AddLine("Send Command: ", cmdCtrl)
        while panel.Affirmed():
            panel.SetResult(cmdCtrl.GetValue())


''' Sends a status request command to the receiver. '''
class GetStatus(eg.ActionBase):
    name='Get Status'
    description='Send a status request, general events on results'

    def __call__(self):
        print 'Sending status request'
        return self.plugin.getStatusRaw()


''' The EventGhost plugin class. '''
class MarantzHTTPPlugin(eg.PluginBase):

    telnet=None
    reader=None
    host=None
    port=None
    timeout=None
    maxDb=12
    disabled=True
    urlHandle=None
    lastVolume=None
    lastInput=None
    lastSurround=None

    def __init__(self):
        for groupname, list in commandsList:
            group = self.AddGroup(groupname)
            for classname, title, desc, app, cmd in list:
                if desc is None:
                    desc = title
                clsAttributes = dict(name=title, description=desc, appcmd=app, cmd=cmd)
                cls = new.classobj(classname, (MarantzAction,), clsAttributes)
                group.AddAction(cls)

        group = self.AddGroup('Volume')
        group.AddAction(SetVolumeAbsolute)
        self.AddAction(SendCommandText)
        self.AddAction(GetStatus)

    def __start__(self, host, port, timeout, maxDb):
        self.host=host
        self.port=port
        self.timeout=timeout
        self.maxDb=maxDb
        self.disabled = False
        print "MarantzHTTPPlugin started"

    def __stop__(self):
        self.disabled = True
        print "MarantzHTTPPlugin stopped."

    def __close__(self):
        print "MarantzHTTPPlugin closing."
        self.disabled = True
        print "MarantzHTTPPlugin closed."

    def roundTo(self, n, precision):
        correction = 0.5 if n >= 0 else -0.5
        return int(n/precision+correction)*precision

    ''' Rounds n to nearest 0.5 '''
    def roundToHalf(self, n):
        return self.roundTo(n, 0.5)

    '''Converts a percentage volume (0,100) to a MV code to set the receiver to that volume'''
    def volumePercentToMV(self, perc):
        if (self.disabled == True):
            return
        if (perc < 0.0 or perc > 100.0):
            print 'perc must be a float in range [0,100]'
            return None

        maxMV = self.maxDb + 80
        mvNum = self.roundToHalf((perc/100.0)*maxMV)
        sys.stdout.write('Setting receiver volume to {0}dB '.format(mvNum-80))

        #Build the correct MVXX or MVXXX string to set the volume.
        if (mvNum<10):
            cmd = 'MV' + ('%2.1f' % mvNum)
            cmd=cmd.replace('MV','MV0')
            cmd=cmd.replace('.', '')
        else:
            cmd = 'MV' + str(mvNum).replace('.5', '5').replace('.', '')

        if (cmd.endswith('0')): cmd=cmd[0:4]

        if (len(cmd) < 4): cmd = cmd + '0'
        return cmd

    def sendCommand(self, cmd):
        if (self.disabled == True):
            return

        self.urlHandle = urllib.urlopen('http://' + self.host + ':' + str(self.port) + '/goform/formiPhoneAppDirect.xml?' + cmd)

    def getStatusRaw(self):            # request status and send volume, input, and surround mode as EV events
        if (self.disabled == True):
            return
        self.urlHandle = urllib.urlopen('http://' + self.host + ':' + str(self.port) + '/goform/formMainZone_MainZoneXml.xml?_=' + format(time.clock()))
        dom = parse (self.urlHandle)
        # <MasterVolume><value>-45.5</value></MasterVolume>
        volume = dom.getElementsByTagName('MasterVolume')[0].getElementsByTagName('value')[0].firstChild.data
        if (volume is not None):
            if (volume != self.lastVolume):
                eg.TriggerEvent('MarantzHTTP.Volume', payload=volume)	# trigger an event with the volume as a payload
                self.lastVolume = volume
        # <InputFuncSelect><value>Blu-ray</value></InputFuncSelect>
        input = dom.getElementsByTagName('InputFuncSelect')[0].getElementsByTagName('value')[0].firstChild.data
        if (input is not None):
            if (input != self.lastInput):
                eg.TriggerEvent('MarantzHTTP.Input', payload=input)		# trigger an event with the input as a payload
                self.lastInput = input
        # <selectSurround><value>Multi Ch Stereo                </value></selectSurround>
        surround = dom.getElementsByTagName('selectSurround')[0].getElementsByTagName('value')[0].firstChild.data
        if (surround is not None):
            surround = surround.strip()
            if (surround != self.lastSurround):
                eg.TriggerEvent('MarantzHTTP.Surround', payload=surround)	# trigger an event with the surround mode as a payload
                self.lastSurround = surround

    def setVolumeAbsolute(self, percentage):
        if (self.disabled == True):
            return

        cmd = self.volumePercentToMV(percentage)
        print '('+str(percentage)+"%), command="+cmd
        self.sendCommand(cmd)

    def Configure(self, host="192.168.66.60", rport=80, timeout=2, maxDb=12):
        text = self.text
        panel = eg.ConfigPanel()
        panel.GetParent().GetParent().SetIcon(self.info.icon.GetWxIcon())

        hostCtrl = wx.TextCtrl(panel,-1, host)
        rportCtrl = eg.SpinIntCtrl(panel, -1, rport, max=65535)
        timeoutCtrl = eg.SpinIntCtrl(panel, -1, timeout, min=1, max=10)
        maxDbCtrl = eg.SpinIntCtrl(panel, -1, maxDb, min=-80, max=12)

        panel.AddLine("Marantz Receiver IP Address:", hostCtrl)
        panel.AddLine("Marantz Receiver HTTP Port: ", rportCtrl)
        panel.AddLine("Send Timeout (secs, unused):", timeoutCtrl)
        panel.AddLine("Max Allowed Volume (dB):    ", maxDbCtrl)

        while panel.Affirmed():
            panel.SetResult(
                hostCtrl.GetValue(),
                rportCtrl.GetValue(),
                timeoutCtrl.GetValue(),
                maxDbCtrl.GetValue()
            )

# Response from a get status HTTP request of /goform/formMainZone_MainZoneXml.xml
#    <?xml version="1.0" encoding="utf-8" ?>
#    <item>
#    <FriendlyName><value>Marantz SR6011</value></FriendlyName>
#    <Power><value>ON</value></Power>
#    <ZonePower><value>ON</value></ZonePower>
#    <RCSourceSelect><value>POS</value></RCSourceSelect>
#    <RenameZone><value>MAIN ZONE 
#    </value></RenameZone>
#    <TopMenuLink><value>ON</value></TopMenuLink>
#    <VideoSelectDisp><value>OFF</value></VideoSelectDisp>
#    <VideoSelect><value></value></VideoSelect>
#    <VideoSelectOnOff><value>OFF</value></VideoSelectOnOff>
#    <VideoSelectLists>
#    <value index='ON' >On</value>
#    <value index='OFF' >Off</value>
#    <value index='SAT/CBL'>CBL/SAT     </value>
#    <value index='DVD'>DVD         </value>
#    <value index='BD'>Blu-ray     </value>
#    <value index='GAME'>Game        </value>
#    <value index='AUX1'>AUX1        </value>
#    <value index='AUX2'>AUX2        </value>
#    <value index='MPLAY'>Media Player</value>
#    </VideoSelectLists>
#    <ECOModeDisp><value>ON</value></ECOModeDisp>
#    <ECOMode><value>OFF</value></ECOMode>
#    <ECOModeLists>
#    <value index='ON'  table='ECO : ON' param=''/>
#    <value index='OFF'  table='ECO : OFF' param=''/>
#    <value index='AUTO'  table='ECO : AUTO' param=''/>
#    </ECOModeLists>
#    <AddSourceDisplay><value>FALSE</value></AddSourceDisplay>
#    <ModelId><value>10</value></ModelId>
#    <BrandId><value>MARANTZ_MODEL</value></BrandId>
#    <SalesArea><value>0</value></SalesArea>
#    <InputFuncSelect><value>Blu-ray</value></InputFuncSelect>
#    <NetFuncSelect><value>FAVORITES</value></NetFuncSelect>
#    <selectSurround><value>Multi Ch Stereo                </value></selectSurround>
#    <VolumeDisplay><value>Relative</value></VolumeDisplay>
#    <MasterVolume><value>-45.5</value></MasterVolume>
#    <Mute><value>off</value></Mute>
#    <RemoteMaintenance><value></value></RemoteMaintenance>
#    <SubwooferDisplay><value>FALSE</value></SubwooferDisplay>
#    <Zone2VolDisp><value>TRUE</value></Zone2VolDisp>
#    <SleepOff><value>Off</value></SleepOff>
#    </item>
