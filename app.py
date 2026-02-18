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

@app.route('/api/fight/get/<int:fight_id>', methods=['GET'])
def get_fight(fight_id):
    try:
        with open(FIGHT_DATA_PATH, 'r', encoding='utf-8') as f:
            fight_data = json.load(f)
            print(f"Fight data for ID {fight_id}:")
            print(json.dumps(fight_data, indent=4))
            return jsonify(fight_data)
    except FileNotFoundError:
        return jsonify({"error": "Fight data file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Running on port 7000 as requested
    app.run(host='0.0.0.0', port=7000, debug=True)
