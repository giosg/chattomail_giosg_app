# chattomail_giosg_app

Adding app to OpenShift.
--------

This example project contains setup.py and wsgi.py files, which are required by OpenShift.

- Install rhc (osx => brew install rhc)
- rhc setup
- rhc app create chattomail python-2.7 --from-code https://github.com/giosg/chattomail_giosg_app.git
- rhc show-app chattomail
- rhc tail -a chattomail
