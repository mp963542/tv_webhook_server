from flask import Flask, request, jsonify
import json, time, os

app = Flask(__name__)
SIGNAL_FILE = "signals.json"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    data["timestamp"] = time.time()
    data["signal_id"] = str(int(data["timestamp"]))
    print("✅ 收到 TradingView 訊號：", data)
    with open(SIGNAL_FILE, "w") as f:
        json.dump(data, f)
    return jsonify({"status": "ok", "signal_id": data["signal_id"]})

@app.route("/signals.json", methods=["GET"])
def get_signals():
    if not os.path.exists(SIGNAL_FILE):
        return jsonify({"status": "no signal"})
    with open(SIGNAL_FILE, "r") as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
