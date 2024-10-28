from flask import Blueprint, request, jsonify
from models.weighing_record import db, TruckWeighing
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest, NotFound

weighing_controller = Blueprint('weighing_controller', __name__)

@weighing_controller.route('/api/weighing', methods=['POST'])
def add_weighing():
    try:
        data = request.json
        # Check for required fields
        required_fields = ['license_plate', 'supplier', 'driver_name', 'first_weight']
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"Missing required field: {field}")

        new_weighing = TruckWeighing(
            license_plate=data['license_plate'],
            supplier=data['supplier'],
            driver_name=data['driver_name'],
            notes=data.get('notes', ''),
            first_weight=data['first_weight']
        )

        db.session.add(new_weighing)
        db.session.commit()
        return jsonify({
            'message': 'Truck added successfully!',
            'status_code': 201,
            'data': {
                'id': new_weighing.id,
                'license_plate': new_weighing.license_plate,
                'first_weight': new_weighing.first_weight,
                'second_weight': new_weighing.second_weight,
                'net_weight': new_weighing.net_weight,
                'status': new_weighing.status
            }
        }), 201

    except BadRequest as e:
        return jsonify({'message': 'Bad request.', 'error': str(e), 'status_code': 400}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to add truck.', 'error': str(e), 'status_code': 500}), 500
    except Exception as e:
        return jsonify({'message': 'An unexpected error occurred.', 'error': str(e), 'status_code': 500}), 500

@weighing_controller.route('/api/weighing/<id>', methods=['PUT'])
def update_weighing(id):
    try:
        weighing = TruckWeighing.query.get(id)
        if not weighing:
            raise NotFound(f"Weighing record with ID {id} not found.")

        data = request.json
        if 'second_weight' in data:
            weighing.second_weight = data['second_weight']
            weighing.second_weighing_time = datetime.utcnow()
            weighing.net_weight = weighing.first_weight - weighing.second_weight
            weighing.status = 'completed'

        db.session.commit()
        return jsonify({
            'message': 'Truck updated successfully!',
            'status_code': 200,
            'data': {
                'id': weighing.id,
                'license_plate': weighing.license_plate,
                'first_weight': weighing.first_weight,
                'second_weight': weighing.second_weight,
                'net_weight': weighing.net_weight,
                'status': weighing.status
            }
        }), 200

    except NotFound as e:
        return jsonify({'message': 'Not found.', 'error': str(e), 'status_code': 404}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update truck.', 'error': str(e), 'status_code': 500}), 500
    except KeyError as e:
        return jsonify({'message': f'Missing required field in request data: {str(e)}' , 'status_code': 400}), 400
    except Exception as e:
        return jsonify({'message': 'An unexpected error occurred.', 'error': str(e), 'status_code': 500}), 500

@weighing_controller.route('/api/weighing/<id>', methods=['DELETE'])
def delete_weighing(id):
    try:
        weighing = TruckWeighing.query.get(id)
        if not weighing:
            raise NotFound(f"Weighing record with ID {id} not found.")

        db.session.delete(weighing)
        db.session.commit()
        return jsonify({
            'message': 'Truck deleted successfully!',
            'status_code': 200,
            'data': {
                'id': weighing.id,
                'license_plate': weighing.license_plate,
                'first_weight': weighing.first_weight,
                'second_weight': weighing.second_weight,
                'net_weight': weighing.net_weight,
                'status': weighing.status
            }
        }), 200

    except NotFound as e:
        return jsonify({'message': 'Not found.', 'error': str(e), 'status_code': 404}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to delete truck.', 'error': str(e), 'status_code': 500}), 500
    except Exception as e:
        return jsonify({'message': 'An unexpected error occurred.', 'error': str(e)}), 500
