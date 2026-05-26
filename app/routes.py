from flask import Blueprint, render_template, jsonify, request
from app.cpu_monitor import CPUMonitor
from flask_socketio import emit
from app import socketio
import threading
import time

main_bp = Blueprint('main', __name__)
monitor = CPUMonitor()

@main_bp.route('/')
def index():
    return render_template('dashboard.html')

@main_bp.route('/api/current_stats')
def current_stats():
    return jsonify({
        'temperatures': monitor.get_temperatures(),
        'frequencies': monitor.get_frequencies(),
        'cpu_usage': monitor.get_cpu_usage(),
        'memory': monitor.get_memory_info(),
        'governor': monitor.get_governor(),
        'available_governors': monitor.get_available_governors()
    })

@main_bp.route('/api/set_governor', methods=['POST'])
def set_governor():
    governor = request.json.get('governor')
    result = monitor.set_governor(governor)
    return jsonify({'success': result is True, 'error': result if result is not True else None})

@main_bp.route('/api/stats')
def get_stats():
    return jsonify(monitor.get_stats())

@main_bp.route('/logs')
def logs():
    return render_template('logs.html')

@main_bp.route('/api/logs')
def get_logs():
    import os
    log_file = os.path.expanduser('~/.cpu-web-tuner/logs/cpu_data.jsonl')
    if not os.path.exists(log_file):
        return jsonify([])
    
    logs = []
    with open(log_file, 'r') as f:
        for line in f:
            logs.append(line.strip())
    return jsonify(logs[-100:])

@socketio.on('request_update')
def handle_update():
    def background_update():
        while True:
            data = {
                'temperatures': monitor.get_temperatures(),
                'frequencies': monitor.get_frequencies(),
                'cpu_usage': monitor.get_cpu_usage(),
                'governor': monitor.get_governor()
            }
            emit('cpu_update', data)
            time.sleep(2)
    
    thread = threading.Thread(target=background_update)
    thread.daemon = True
    thread.start()