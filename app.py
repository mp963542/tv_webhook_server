from flask import Flask, request, jsonify
import json, time, os

app = Flask(__name__)
SIGNAL_FILE = "signals.json"
RETENTION_SECONDS = 30  # 只保留 30 秒內訊號

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    data.setdefault("timestamp", time.time())
    # 若是 ISO 格式字串，轉換為 float timestamp（確保 downstream 可以用）
    if isinstance(data["timestamp"], str):
        try:
            dt = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
            data["timestamp"] = dt.timestamp()
        except Exception:
            data["timestamp"] = time.time()
    data["signal_id"] = str(int(data["timestamp"] * 1000))
    
    print("✅ 收到 TradingView 訊號：", data)

    # 讀取現有訊號陣列（如無則初始化）
    if os.path.exists(SIGNAL_FILE):
        with open(SIGNAL_FILE, "r") as f:
            signals = json.load(f)
    else:
        signals = []

    # 保留 30 秒內的訊號
    now = time.time()
    signals = [s for s in signals if now - s.get("timestamp", 0) <= RETENTION_SECONDS]

    signals.append(data)

    with open(SIGNAL_FILE, "w") as f:
        json.dump(signals, f)

    return jsonify({"status": "ok", "received": data["signal_id"]})

@app.route("/signals.json", methods=["GET"])
def get_signals():
    if os.path.exists(SIGNAL_FILE):
        with open(SIGNAL_FILE, "r") as f:
            return jsonify(json.load(f))
    else:
        return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
