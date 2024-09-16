from flask import Flask
from flask_cors import CORS
import threading
import time
import datetime
import measure
import json

app = Flask(__name__)

# CORS(app, resources={r"/*": {"origins": "http://yourdomain.tld"}})
# CORS(app, resources={r"/*": {"origins": ["http://localhost:3546"]}})
CORS(app, resources={r"/*": {"origins": "*"}})

systemHistoryFile = "system.history.json"

@app.route("/")
def hello_world():
    return "{'Error':'Please connect to an endpoint'}"

# @app.route("/processes")
# def procs():
#     return sysDetails.processes

@app.route("/system")
def sys():
    return sysDetails.system

@app.route("/system/history")
def sysHistory():
    with open(systemHistoryFile, "r") as f:
        file = f.read()
    return file

class sysDetails:
    def __init__(self):
        # self.processes = {}
        self.system = {}

    def backgroundUpdater(self):
        while True:
            # self.processes = measure.processes()
            self.system = measure.system()

            try:
                with open(systemHistoryFile, 'r') as f:
                    systemHistory = json.load(f)
            except FileNotFoundError:
                with open(systemHistoryFile, "w") as f:
                    systemHistory = {"History":[]}
                    json.dump(systemHistory, f)

            systemHistory["History"].append({"time":str(datetime.datetime.now()), "system":self.system})

            if len(systemHistory["History"]) > 500:
                systemHistory["History"] = systemHistory["History"][-500:]
            with open(systemHistoryFile, 'w') as f:
                json.dump(systemHistory, f)

            time.sleep(2)
sysDetails = sysDetails()

if __name__ == '__main__':
    updateThread = threading.Thread(target=sysDetails.backgroundUpdater, daemon=True)
    updateThread.start()
    app.run(host="127.0.0.1", port=3545)