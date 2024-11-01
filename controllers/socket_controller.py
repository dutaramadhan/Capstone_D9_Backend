from flask import Blueprint, request, jsonify
from flask_socketio import SocketIO, emit
from threading import Event
from services.weighing_service import get_weight_data 

socketio = SocketIO(cors_allowed_origins="*")
socket_controller = Blueprint('socket', __name__)

active_clients = 0
should_stream = Event()

def stream_weight_data():
    socketio.emit('status', {'message': 'Starting weight stream for all clients'})
    
    while not should_stream.is_set():
        try:
            weight_data = get_weight_data() 
            socketio.emit('weight_data', weight_data)
            socketio.sleep(2)
        except Exception as e:
            socketio.emit('error', {'message': 'Error in weight stream'})
            break

    socketio.emit('status', {'message': 'Stopped weight stream for all clients'})

@socketio.on('connect')
def handle_connect():
    global active_clients
    
    client_id = request.sid
    active_clients += 1
    
    if active_clients == 1: 
        should_stream.clear()
        socketio.start_background_task(stream_weight_data)

    emit('status', {'message': f'Client {client_id} connected.'}, status=200)

@socketio.on('disconnect')
def handle_disconnect():
    global active_clients
    
    client_id = request.sid
    active_clients = max(0, active_clients - 1)
    
    emit('status', {'message': f'Client disconnected. ID: {client_id}. Active clients: {active_clients}'}, status=200)
    
    if active_clients == 0:
        should_stream.set()

@socketio.on_error_default
def default_error_handler(e):
    error_message = f'SocketIO error: {str(e)}'
    socketio.emit('error', {'message': error_message})
    return jsonify({"message": error_message, "status": 500})

def stop_all_streams():
    should_stream.set()