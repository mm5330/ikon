import sys

activate_this='/var/www/html/gamification/py3env/bin/activate_this.py'
with open(activate_this) as file__:
    exec(file__.read(), dict(__file__=activate_this))

sys.path.insert(0, '/var/www/html/gamification/konFinal/kon')

from app import app as application
