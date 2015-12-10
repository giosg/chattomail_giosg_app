# chattomail_giosg_app

* Adding app to OpenShift.

This example project contains setup.py and wsgi.py files, which are required by OpenShift.

1) Install rhc
2) rhc setup
3) rhc app create chattomail python-2.7 --from-code https://github.com/giosg/chattomail_giosg_app.git
4) rhc show-app chattomail
5) rhc tail -a chattomail
