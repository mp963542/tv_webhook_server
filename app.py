from flask import Flask, request, jsonify
import json, time, os
from datetime import datetime

app = Flask(__name__)
SIGNAL_FILE = "signals.json"
RETENTION_SECONDS = 30  # 只保留 30 秒內訊號（以 server_timestamp 判斷）

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    # 保留 TradingView 傳來的原始 timestamp，如無則補一個 ISO 格式字串
    data.setdefault("timestamp", datetime.utcnow().isoformat() + "Z")

    # 新增 server 端實際接收到 webhook 的 timestamp（float 秒）
    data["server_timestamp"] = time.time()

    # 用 server_timestamp 產生唯一 ID
    data["signal_id"] = str(int(data["server_timestamp"] * 1000))

    print("✅ 收到 TradingView 訊號：", data)

    # 讀取現有訊號陣列（如無則初始化）
    if os.path.exists(SIGNAL_FILE):
        with open(SIGNAL_FILE, "r") as f:
            signals = json.load(f)
    else:
        signals = []

    # 過濾掉超過 30 秒的舊訊號（根據 server_timestamp）
    now = time.time()
    signals = [s for s in signals if now - s.get("server_timestamp", 0) <= RETENTION_SECONDS]

    # 加入新訊號
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
