import os

from subprocess import Popen

os.environ["FLASK_APP"] = "service/server.py"
flask_ps = Popen(["flask", "run"])
flask_ps.communicate()
