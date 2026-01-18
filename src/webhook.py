from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook/alert', methods=['POST'])
def handle_grafana_alert():
    data = request.json
    print('dupa')
    
    if data.get('status') == 'firing':
        pass
    return jsonify({'status': 'ok'}), 200

def run_flask():
    app.run(host='0.0.0.0', port=5000)
