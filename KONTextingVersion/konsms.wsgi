import sys

activate_this='/var/www/html/konsms/venv3/bin/activate_this.py'
with open(activate_this) as file__:
    exec(file__.read(), dict(__file__=activate_this))

sys.path.insert(0, '/var/www/html/kon/KonSMSCodeBase')

from KONMessagingWithDb import app as application
