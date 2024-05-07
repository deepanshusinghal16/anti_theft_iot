from flask import Flask, render_template
from flask_cors import CORS
import os
import re

app = Flask(__name__, static_url_path='/static')
CORS(app)

@app.route('/')
def index():
    alert_folder = 'static/alert'
    image_files_with_timestamp = []

    timestamp_pattern = r'person_detected_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\.jpg'

    if os.path.exists(alert_folder):
        image_files = [f for f in os.listdir(alert_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        image_files.sort(reverse=True)

        for image_file in image_files:
            match = re.match(timestamp_pattern, image_file)
            if match:
                timestamp = match.group(1)
                image_files_with_timestamp.append({'filename': image_file, 'timestamp': timestamp})

    return render_template('index.html', image_files_with_timestamp=image_files_with_timestamp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
