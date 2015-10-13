# SIPIntercom-with-FPS
Raspberry IP intercom with ADH Tech GT511C3 finger print reader. All in Python v2

Diploma work for the ETML telecommunication high scool.
http://www.etml-es.ch/

This is a demonstrator not a ready to use product, more informations about issues later in this document

This application use the liblinphone library for the SIP client.
http://www.linphone.org/technical-corner/liblinphone/overview
Documentation for this library is available at:
http://pythonhosted.org/linphone/
But beware ! It seems some information are missing ! Some function are not described in this documentation.

GT511C3 offical page with datasheet:
http://www.adh-tech.com.tw/?9,gt-511c3-gt-511c31-%28uart%29
The original python library for the GT511C3 finger print reader is pyGT511C3 from the user jeanmachuca
https://github.com/QuickGroup/pyGT511C3
