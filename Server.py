from flask import Flask, request, jsonify
import pandas as pd
from datetime import datetime
import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt
import os

def performance_label(speed):
    if speed >= 45:
        return "Excellent"
    elif speed >= 35:
        return "Good"
    else:
        return "Needs Improvement"


app = Flask(__name__)

CSV_FILE = "game_data.csv"

# Create CSV if not exists
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=[
        "player_id",
        "distance",
        "max_speed",
        "collided",
        "session_time"
    ])
    df.to_csv(CSV_FILE, index=False)


@app.route("/gameover", methods=["POST"])
def gameover():
    data = request.json

    # Create clean analytics row
    row = {
        "timestamp": pd.to_datetime(data["session_time"]),
        "distance": data["distance"],
        "max_speed": data["max_speed"]
    }

    df = pd.DataFrame([row])
    df.to_csv("game_data.csv", mode="a", header=False, index=False)

    print("✅ SAVED ROW:", row)

    return jsonify({"status": "success"})



@app.route("/dashboard")
def dashboard():
    df = pd.read_csv("game_data.csv")

    df["session"] = range(1, len(df) + 1)

    # Add performance label
    df["performance"] = df["max_speed"].apply(performance_label)

    last_performance = df["performance"].iloc[-1]
    total_sessions = len(df)


    # ✅ Generate plot EVERY time dashboard loads
    plt.figure(figsize=(8, 4))
    plt.plot(df["session"], df["max_speed"], marker="o")
    plt.xlabel("Session Number")
    plt.ylabel("Max Speed")
    plt.title("Player Learning Progress")
    plt.tight_layout()
    plt.savefig("static/speed_plot.png")
    plt.close()

    return f"""
    <html>
    <head>
        <title>Game Analytics Dashboard</title>
        <style>
            body {{
                font-family: Arial;
                background: #111;
                color: white;
                text-align: center;
            }}
            .box {{
                background: #222;
                padding: 20px;
                margin: 20px;
                border-radius: 10px;
                font-size: 22px;
            }}
            img {{
                width: 70%;
                margin-top: 20px;
                border-radius: 10px;
            }}
        </style>
    </head>
    <body>
        <h1>🎮 Game Performance Dashboard</h1>
        <div class="box">🧠 Last Performance: {last_performance}</div>
        <div class="box">🎮 Total Sessions Played: {total_sessions}</div>
        <div class="box">🚀 Highest Speed Ever: {df['max_speed'].max():.2f}</div>
        <div class="box">📊 Average Speed: {df['max_speed'].mean():.2f}</div>
        <div class="box">⏱ Latest Session Speed: {df['max_speed'].iloc[-1]:.2f}</div>

        <h2>📈 Speed Trend</h2>
        <img src="/static/speed_plot.png?{pd.Timestamp.now().value}">

        <p><b>Generated from real gameplay data</b></p>
    </body>
    </html>
    """



if __name__ == "__main__":
    app.run(debug=True)


