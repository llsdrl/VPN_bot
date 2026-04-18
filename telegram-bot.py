from flask import Flask, request
import os

app = Flask(__name__)

TOKEN = "8749332624:AAFyhffF1GElZxVBSdU-cb-GFmkSfdcDKkg"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    return "OK"

@app.route("/health")
def health():
    return "OK"

@app.route("/")
def index():
    return "VPN Bot Running"

if __name__ == "__main__":
    print("Starting Flask app...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))