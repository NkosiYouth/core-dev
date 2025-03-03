======================
 Odoo WebRTC SIP phone
======================
This is a WEB Phone based on WebRTC SIP protocol for the Asterisk Plus application.
It can be used to place and receive calls in Odoo.

Installation & Configuration
============================
Go to PBX - Settings - WebRTC tab.

By defalt the module is disable. To disable the module set "false" in the Enabled field.

Specify here your SIP server hostname:port and WebSocker URL.

Next go to PBX Users and add PJSIP channels with WebRTC profile.

Auto answer
===========
The phone supports auto answer mode.

In order to make it automatically accept incoming calls set ``Answer-Mode: Auto`` header.

Known limitations
=================
* Only 1 SIP line is supported and 1 call at a time.

Bugs, feature requests and support
==================================
The module price does not include any kind of your PBX configuration or troubleshooting.

Asterisk WebRTC setup is not a trivial task. Before contacting the support make sure your other WebRTC solution works as expected.




