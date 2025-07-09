
import requests
from flask import Flask, jsonify, request

app = Flask('name')

API_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjU2NjQ2YzhjLTk1ZjQtNDNjNS05MTI0LWQ3YjcxMDQ1MDUzYiIsImlhdCI6MTc1MTk3MDA0Niwic3ViIjoiZGV2ZWxvcGVyLzQ3MTBkOGUwLTY0ZjYtYzA2Ny0xZTI4LTQwOGU1OTA5YzQ0YiIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyIxMDYuMjA1LjE3MS4yNyJdLCJ0eXBlIjoiY2xpZW50In1dfQ.IpJ1LyOzT6OzfiXYPCrkySh_u10iNPw5zD4EJ52dzZCWtKbFG4rukYEDXAi8DNYAiInW81LK_mkukNqJ2tIOEA"# Set this in Render Dashboard

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}"
}


@app.route("/get-deck", methods=["POST"])
def get_deck():
    try:
        data = request.get_json()
        medals = int(data.get('medals'))

        # Step 1: Get leaderboard players
        limit = 300
        CR_API_BASE_URL = "https://api.clashroyale.com/v1"
        leaderboard_url = f"{CR_API_BASE_URL}/locations/global/pathoflegend/players?limit={limit}"
        res = requests.get(leaderboard_url, headers=HEADERS, timeout=10)

        if res.status_code != 200:
            print('error')
            return jsonify({"error": f"Leaderboard fetch failed: {res.status_code} (reason: {res.reason})"}), 500

        players = res.json().get("items", [])

        # Step 2: Match exact medals and fetch deck
        matching_players = []
        for player in players:
            if player.get("eloRating") == medals:
                tag = player["tag"].replace("#", "%23")
                battle_url = f"https://api.clashroyale.com/v1/players/{tag}/battlelog"
                battle_res = requests.get(battle_url, headers=HEADERS, timeout=10)

                if battle_res.status_code != 200:
                    return jsonify({"error": "Battle log fetch failed"}), 500

                battles = battle_res.json()
                for battle in battles:
                    if battle["gameMode"]['name'] in ["Ranked1v1_NewArena2", "Ladder"]:
                        deck = [{"name": c["name"], "level": c["level"], "iconUrl": c["iconUrls"]["medium"]} for c in battle["team"][0]["cards"]]
                        matching_players.append({"player_name": player['name'], "deck": deck})
                        # Skip to next player if we found a valid battle
                        break

        if len(matching_players) > 0:
            return jsonify({"matching_players": matching_players})
        return jsonify({"error": "Player not found with exact medals"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return "Backend is Running"


if __name__ == "__main__":
    app.run()
