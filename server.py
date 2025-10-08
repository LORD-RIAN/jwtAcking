from flask import Flask, request
import subprocess, sys

app = Flask(__name__)

@app.route("/")
def index():
    return open("main.html").read()

@app.route("/run", methods=["POST"])
def run():
    data = request.form["payload"]
    result = subprocess.run(
        [sys.executable, "main.py"], input=data.encode(), capture_output=True
    )
    return f"<pre>{result.stdout.decode(errors='ignore')}</pre>"

app.run(port=5000)
