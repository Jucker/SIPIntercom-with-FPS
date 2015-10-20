# SIPIntercom-with-FPS
Raspberry IP intercom with ADH Tech GT511C3 finger print reader. All in Python v2

The intercom use a SIP client to perform call to a remote client via an internet proxy (VoIP provider). A 4 digits password must be send by the remote user to open the door. The fingerprint reader is used in replacement of a card reader or a key.
The FPS can store max. 200 fingerprint template to perform 1:N verification. Matching results open the door.

Diploma work for the ETML telecommunication high scool.
http://www.etml-es.ch/

This is a demonstrator not a ready to use product, more informations about issues later in this document. The demonstrator use LED to simulate the door opennig. A switch is used to simulate a door magnetic contact to supervise the door state (open/close), a open door turn the door state LED on.

This application use the liblinphone library for the SIP client.
http://www.linphone.org/technical-corner/liblinphone/overview
Documentation for this library is available at:
http://pythonhosted.org/linphone/
But beware ! It seems some informations are missing ! Some function are not described in this documentation.

GT511C3 offical page with datasheet:
http://www.adh-tech.com.tw/?9,gt-511c3-gt-511c31-%28uart%29
The original python library for the GT511C3 finger print reader is pyGT511C3 from the user jeanmachuca
https://github.com/QuickGroup/pyGT511C3

I have made some modifications to the original FPS library to imporve it and resolve some issues. Major modifications are:
- Modified the response paquet processing (error return process)
- Modified the time management to "wait" befor getting bytes from the serial buffer

A short manual (in french) is available in this repository (Manual_French.txt)
Schematics (shematic.txt)

Work well with my prototype.

Use changeBaudBaudRate.py to change the FPS baudRate. Use it each time the FPS is power on

Known issues:
- SIP client send DNS queries twices
- SIP client send INVITE and REGISTER without registration informations first, after error 407 response send it with all the informations. Mayby it's the desired behavior by the liblinphone library. Has pratically no incidence.
- SIP client dosen't encrypt video stream when using the ZRTP parameter (encrypt only audio RTP paquet) in the call.conf file. Use SRTP parameter with TLS encryption for SIP frames to perform full security call.
- SIP client send burst of REGISTER when the parameter Config_log: is set to True in the call.conf file, unknown reason
- The threading/process management probably need some improvement. 
- Due to the free id research mechanism during the enrollement process the enrollement process could be a bit long when the system as a lot of template stored or when some id has been erased.
