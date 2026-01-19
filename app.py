from flask import Flask, render_template, request, jsonify
import requests
import json
from datetime import datetime

app = Flask(__name__)

# Home Route
@app.route('/')
def index():
    return render_template('index.html')

# API Route to fetch player info
@app.route('/get_player_info', methods=['GET', 'POST'])
def get_player_info():
    if request.method == 'POST':
        uid = request.form.get('uid')
        region = request.form.get('region', 'IND')
    else:
        uid = request.args.get('uid')
        region = request.args.get('region', 'IND')
    
    if not uid:
        return jsonify({"error": "UID is required"}), 400
    
    try:
        # API URL
        api_url = f"https://info-flax-beta.vercel.app/info?uid={uid}&region={region}"
        
        # Fetch data from API
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Format timestamps
            if 'basicInfo' in data:
                if 'createAt' in data['basicInfo']:
                    data['basicInfo']['createAt_formatted'] = format_timestamp(data['basicInfo']['createAt'])
                if 'lastLoginAt' in data['basicInfo']:
                    data['basicInfo']['lastLoginAt_formatted'] = format_timestamp(data['basicInfo']['lastLoginAt'])
            
            if 'captainBasicInfo' in data:
                if 'createAt' in data['captainBasicInfo']:
                    data['captainBasicInfo']['createAt_formatted'] = format_timestamp(data['captainBasicInfo']['createAt'])
                if 'lastLoginAt' in data['captainBasicInfo']:
                    data['captainBasicInfo']['lastLoginAt_formatted'] = format_timestamp(data['captainBasicInfo']['lastLoginAt'])
            
            # Calculate days since creation
            if 'basicInfo' in data and 'createAt' in data['basicInfo']:
                create_date = datetime.fromtimestamp(int(data['basicInfo']['createAt']))
                current_date = datetime.now()
                days_played = (current_date - create_date).days
                data['basicInfo']['days_played'] = days_played
            
            return render_template('result.html', data=data, uid=uid, region=region)
        else:
            error_msg = f"API Error: {response.status_code}"
            return render_template('index.html', error=error_msg)
            
    except requests.exceptions.RequestException as e:
        return render_template('index.html', error=f"Network Error: {str(e)}")
    except Exception as e:
        return render_template('index.html', error=f"Error: {str(e)}")

def format_timestamp(timestamp):
    """Convert Unix timestamp to readable date"""
    try:
        dt = datetime.fromtimestamp(int(timestamp))
        return dt.strftime("%d %B %Y %I:%M %p")
    except:
        return timestamp

# API endpoint for JSON response
@app.route('/api/player/<uid>')
@app.route('/api/player/<uid>/<region>')
def api_player_info(uid, region='IND'):
    try:
        api_url = f"https://info-flax-beta.vercel.app/info?uid={uid}&region={region}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Failed to fetch data", "status_code": response.status_code}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Health check route for Vercel
@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "Free Fire Info API"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)