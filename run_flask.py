import os
import sys
from subprocess import Popen

os.environ["FLASK_APP"] = "service/server.py"
flask_ps = Popen(["flask", "run", "--host=0.0.0.0"], stdout=sys.__stdout__, stderr=sys.__stderr__)
flask_ps.communicate()
