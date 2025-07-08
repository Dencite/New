import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

API_TOKEN = os.environ.get("CR_API_TOKEN")  # Set this in Render Dashboard

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}"
}


@app.route("/get-deck", methods=["POST"])
def get_deck():
    try:
        data = request.get_json()
        medals = int(data.get('medals'))

        # Step 1: Get leaderboard players
        CR_API_BASE_URL = "https://api.clashroyale.com/v1"
        leaderboard_url = f"{CR_API_BASE_URL}/locations/global/pathoflegend/players?limit=1000"
        res = requests.get(leaderboard_url, headers=HEADERS, timeout=10)

        if res.status_code != 200:
            return jsonify({"error": f"Leaderboard fetch failed: {res.status_code}"}), 500

        players = res.json().get("items", [])
        if not players:
            return jsonify({"error": "No leaderboard players found"}), 404

        matching_players = []

        for player in players:
            if player.get("eloRating") == medals:
                tag = player["tag"].replace("#", "%23")
                battle_url = f"{CR_API_BASE_URL}/players/{tag}/battlelog"
                battle_res = requests.get(battle_url, headers=HEADERS, timeout=10)

                if battle_res.status_code != 200:
                    continue  # Skip failed player

                battles = battle_res.json()
                for battle in battles:
                    if battle["gameMode"]["name"] == "Ranked1v1_NewArena2":
                        matching_player = [{
                            "name": card["name"],
                            "level": card["level"],
                            "player": player["name"],
                            "iconUrl": card["iconUrls"]["medium"]
                        } for card in battle["team"][0]["cards"]]
                        matching_players.append(matching_player)
                        break  # Only one deck per player

        if matching_players:
            return jsonify({"matching_players": matching_players})
        else:
            return jsonify({"error": "No matching players found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return "Backend is Running"


if __name__ == "__main__":
    app.run()
