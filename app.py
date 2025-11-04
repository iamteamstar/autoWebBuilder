from flask import Flask, render_template, request, jsonify, send_file
import os, zipfile, io
from mock_data import generate_mock_templates

app = Flask(__name__)

# Ana sayfa
@app.route('/')
def index():
    return render_template('index.html')

# Mock site alternatiflerini döndür
@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    topic = data.get('topic', '')
    if not topic:
        return jsonify({'error': 'Konu girilmedi'}), 400

    templates = generate_mock_templates(topic)
    return jsonify({'templates': templates})

# Seçilen şablonu zip olarak indirme
@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    html = data.get('html', '')
    css = data.get('css', '')

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('index.html', html)
        zf.writestr('style.css', css)
    zip_buffer.seek(0)

    return send_file(zip_buffer, as_attachment=True, download_name='website.zip')

if __name__ == '__main__':
    app.run(debug=True)
