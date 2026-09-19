from flask import Flask, jsonify, request, send_from_directory, render_template_string
import os, json, subprocess, glob
import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

app = Flask(__name__, static_folder='.')

# Load library
LIB_PATH = '/home/user/videforsleep/voices_library/library.json'
with open(LIB_PATH, 'r', encoding='utf-8') as f:
    library = json.load(f)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/tool')
def tool():
    return send_from_directory('.', 'voice_selector_tool.html')

@app.route('/api/voices')
def api_voices():
    return jsonify(library)

@app.route('/api/generate', methods=['POST'])
def api_generate():
    data = request.get_json()
    voice_id = data.get('voice_id', 'voice-26')
    script_type = data.get('script', 'v2_mysterious')  # v2_mysterious, premium, original
    
    # Save request for assistant to process
    os.makedirs('/tmp/voice_requests', exist_ok=True)
    req_file = f'/tmp/voice_requests/{voice_id}_{script_type}.json'
    with open(req_file, 'w') as f:
        json.dump({"voice_id": voice_id, "script": script_type, "status": "pending"}, f)
    
    return jsonify({"status": "queued", "voice_id": voice_id, "script": script_type, "message": f"تم حفظ طلبك: إنشاء فيديو بصوت {voice_id} وسكريبت {script_type}. سيقوم المساعد بإنشائه الآن."})

@app.route('/voices_library/<path:path>')
def serve_voices(path):
    return send_from_directory('voices_library', path)

@app.route('/assets/<path:path>')
def serve_assets(path):
    return send_from_directory('assets', path)

@app.route('/assets_v2/<path:path>')
def serve_assets_v2(path):
    return send_from_directory('assets_v2', path)

@app.route('/output/<path:path>')
def serve_output(path):
    return send_from_directory('output', path)

@app.route('/<path:path>')
def serve_static(path):
    # Try to serve from root
    if os.path.exists(path):
        return send_from_directory('.', path)
    return "Not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
