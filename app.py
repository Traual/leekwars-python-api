import json
from flask import Flask, jsonify
from flask_cors import CORS
from constants import FIGHT_DATA_PATH

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "success",
        "message": "Flask API is running on port 7000"
    })

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({
        "message": "Hello from your basic Flask API!"
    })

@app.route('/api/fight/get-logs/<int:fight_id>', methods=['GET'])
def get_fight_logs(fight_id):
    return jsonify({})

import time

@app.route('/api/fight/get/<int:fight_id>', methods=['GET'])
def get_fight(fight_id):
    try:
        # 1. Load the raw generator output
        with open(FIGHT_DATA_PATH, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
        fight = raw_data.get('fight', {})
        leeks_list = fight.get('leeks', [])
        
        # 2. Try to supplement with scenario metadata for "real" IDs and names
        # Default fallback is using turn IDs as real IDs
        scenario_data = None
        scenario_path = "C:\\Users\\aurel\\leek-wars-generator\\test\\scenario\\scenario1.json"
        try:
            with open(scenario_path, 'r', encoding='utf-8') as sf:
                scenario_data = json.load(sf)
        except:
            pass
            
        real_farmers = {}
        real_leek_ids = {} # turn_id -> real_id
        if scenario_data:
            # Map farmers
            for f in scenario_data.get('farmers', []):
                real_farmers[f['id']] = f
            # Map leeks by name (heuristic)
            scenario_entities = []
            for team_entities in scenario_data.get('entities', []):
                scenario_entities.extend(team_entities)
            
            for l in leeks_list:
                name = l.get('name')
                # Find matching entity in scenario
                match = next((e for e in scenario_entities if e.get('name') == name), None)
                if match:
                    real_leek_ids[l.get('id')] = match.get('id')
                else:
                    real_leek_ids[l.get('id')] = l.get('id')
        else:
            for l in leeks_list:
                real_leek_ids[l.get('id')] = l.get('id')

        # 3. Process Winner
        winner_id = fight.get('winner', -1)
        api_winner = winner_id if winner_id != -1 else 0
        
        # 4. Split and Format Entities
        leeks1_data = [l for l in leeks_list if l.get('team') == 1]
        leeks2_data = [l for l in leeks_list if l.get('team') == 2]
        
        def format_top_leek(l):
            rid = real_leek_ids.get(l.get('id'))
            return {
                "id": rid,
                "name": l.get('name'),
                "level": l.get('level'),
                "talent": 0,
                "hat": l.get('hat'),
                "skin": l.get('skin'),
                "farmer": l.get('farmer'),
                "weapon": None,
                "title": [],
                "metal": l.get('metal', False),
                "face": l.get('face', 0)
            }
        
        def format_report_leek(l):
            rid = real_leek_ids.get(l.get('id'))
            # Check dead status using scenario ID (if available in fight['dead'])
            dead_map = fight.get('dead', {})
            is_dead = dead_map.get(str(rid), dead_map.get(str(l.get('id')), False))
            
            return {
                "id": rid,
                "name": l.get('name'),
                "dead": is_dead,
                "td": 0,
                "resources": {},
                "talent": 0,
                "talent_gain": 0,
                "xp": 0,
                "cur_xp": 0,
                "next_xp": 0,
                "prev_xp": 0,
                "level": l.get('level'),
                "money": 0,
                "appearance": 9,
                "xp_locked": False
            }

        # Farmers
        def get_farmers_for_team(leeks):
            f_dict = {}
            for l in leeks:
                f_id = l.get('farmer')
                if f_id:
                    scene_f = real_farmers.get(f_id, {})
                    f_dict[str(f_id)] = {
                        "id": f_id,
                        "name": scene_f.get('name', f"Farmer {f_id}"),
                        "avatar_changed": int(time.time()),
                        "muted": False
                    }
            return f_dict

        # 5. Build Final Response
        response = {
            "id": fight_id,
            "date": int(time.time()),
            "year": 2026,
            "type": 0,
            "context": 3,
            "status": 2,
            "winner": api_winner,
            "leeks1": [format_top_leek(l) for l in leeks1_data],
            "leeks2": [format_top_leek(l) for l in leeks2_data],
            "farmers1": get_farmers_for_team(leeks1_data),
            "farmers2": get_farmers_for_team(leeks2_data),
            "report": {
                "duration": fight.get('duration', 0),
                "win": api_winner,
                "leeks1": [format_report_leek(l) for l in leeks1_data],
                "leeks2": [format_report_leek(l) for l in leeks2_data],
                "bonus": 0,
                "flags1": [],
                "flags2": []
            },
            "comments": [],
            "tournament": 0,
            "views": 0,
            "starter": None,
            "trophies": [],
            "seed": 0,
            "team1_name": leeks1_data[0].get('name') if leeks1_data else "Team 1",
            "team2_name": leeks2_data[0].get('name') if leeks2_data else "Team 2",
            "data": {
                "leeks": leeks_list, # Remains 0, 1, 2, 3 for actions
                "map": fight.get('map'),
                "actions": fight.get('actions')
            }
        }
        
        print(f"Generated fight response for ID {fight_id} from {FIGHT_DATA_PATH}")
        return jsonify(response)
        
    except FileNotFoundError:
        return jsonify({"error": f"Fight data file not found at {FIGHT_DATA_PATH}"}), 404
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Running on port 7000 as requested
    app.run(host='0.0.0.0', port=7000, debug=True)
