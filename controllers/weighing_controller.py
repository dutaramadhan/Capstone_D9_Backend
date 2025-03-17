from flask import Blueprint, request, jsonify, make_response
from models.weighing_record import db, TruckWeighing

from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest, NotFound
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
from sqlalchemy import extract

A5 = A5 = (A4[0] / 2, A4[1] / 2)

weighing_controller = Blueprint('weighing_controller', __name__)

@weighing_controller.route('/api/weighing', methods=['POST'])
def add_weighing():
    try:
        data = request.json
        required_fields = ['license_plate', 'supplier', 'driver_name', 'first_weight']
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"Missing required field: {field}")

        new_weighing = TruckWeighing(
            license_plate=data['license_plate'],
            supplier=data['supplier'],
            driver_name=data['driver_name'],
            notes=data.get('notes', ''),
            first_weight=data['first_weight'],
            first_weighing_time = datetime.now()
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
            weighing.second_weighing_time = datetime.now()
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

@weighing_controller.route('/api/weighing', methods=['GET'])
def get_all_weighings():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)

        query = TruckWeighing.query

        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(TruckWeighing.first_weighing_time >= start_date_obj)
            except ValueError:
                return jsonify({'message': 'Invalid start_date format. Use YYYY-MM-DD format.'}), 400

        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                query = query.filter(TruckWeighing.first_weighing_time <= end_date_obj)
            except ValueError:
                return jsonify({'message': 'Invalid end_date format. Use YYYY-MM-DD format.'}), 400

        weighings = query.order_by(TruckWeighing.second_weighing_time.desc()).paginate(page=page, per_page=per_page, error_out=False)

        if weighings.total == 0:
            return jsonify({
                'message': 'No weighing records found.',
                'status_code': 400,
                'data': []
            }), 400

        weighing_list = [{
            'id': weighing.id,
            'license_plate': weighing.license_plate,
            'supplier': weighing.supplier,
            'driver_name': weighing.driver_name,
            'notes': weighing.notes,
            'first_weight': weighing.first_weight,
            'second_weight': weighing.second_weight,
            'net_weight': weighing.net_weight,
            'status': weighing.status,
            'first_weighing_time': weighing.first_weighing_time,
            'second_weighing_time': weighing.second_weighing_time
        } for weighing in weighings.items]

        return jsonify({
            'message': 'Weighing records retrieved successfully!',
            'status_code': 200,
            'data': weighing_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': weighings.total,
                'total_pages': weighings.pages,
            }
        }), 200

    except SQLAlchemyError as e:
        return jsonify({'message': 'Failed to retrieve weighing records.', 'error': str(e)}), 500
    except Exception as e:
        return jsonify({'message': 'An unexpected error occurred.', 'error': str(e)}), 500

@weighing_controller.route('/api/weighing/<id>', methods=['GET'])
def get_weighing_by_id( id):
    try:
        weighing = TruckWeighing.query.get(id)
        if not weighing:
            raise NotFound(f"Weighing record with ID {id} not found.")
        weighing_data = {
            'id': weighing.id,
            'license_plate': weighing.license_plate,
            'supplier': weighing.supplier,
            'driver_name': weighing.driver_name,
            'notes': weighing.notes,
            'first_weight': weighing.first_weight,
            'second_weight': weighing.second_weight,
            'net_weight': weighing.net_weight,
            'status': weighing.status,
            'first_weighing_time': weighing.first_weighing_time,
            'second_weighing_time': weighing.second_weighing_time
        } 
        return jsonify({
            'message': 'Weighing records retrieved successfully!',
            'status_code': 200,
            'data': weighing_data,
        }), 200

    except NotFound as e:
        return jsonify({'message': 'Not found.', 'error': str(e), 'status_code': 404}), 404
    except SQLAlchemyError as e:
        return jsonify({'message': 'Failed to generate PDF.', 'error': str(e), 'status_code': 500}), 500
    except Exception as e:
        return jsonify({'message': 'An unexpected error occurred.', 'error': str(e)}), 500

@weighing_controller.route('/api/weighing/<id>/pdf', methods=['GET'])
def generate_weighing_pdf(id):
    try:
        weighing = TruckWeighing.query.get(id)
        if not weighing:
            raise NotFound(f"Weighing record with ID {id} not found.")

        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A5)
        width, height = A5

        
        c.setFont("Helvetica-Bold", 18)
        c.drawString(40, height - 40, "TPST Sinduadi")
        c.setFont("Helvetica", 10)
        c.drawString(40, height - 60, "Kutu Wates, Kragilan, Sinduadi, Mlati, Sleman")
        c.drawString(40, height - 75, "Tel: +62 123 456 789 | Email: info@tpstsinduadi.com")
        c.line(40, height - 85, width - 30, height - 85)

      
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, height - 110, "Nota Penimbangan")
        
        # Content
        c.setFont("Helvetica", 10)
        y_position = height - 130
        details = [
            ("Nomor Polisi", weighing.license_plate),
            ("Supplier", weighing.supplier),
            ("Supir", weighing.driver_name),
            ("Timbangan Pertama", f"{weighing.first_weight} kg"),
            ("Timbangan Kedua", f"{weighing.second_weight or 'N/A'} kg"),
            ("Berat Bersih", f"{weighing.net_weight or 'N/A'} kg"),
            ("Waktu Penimbangan Pertama", weighing.first_weighing_time.strftime('%d-%m-%Y %H:%M:%S')),
            ("Waktu Penimbangan Kedua", weighing.second_weighing_time.strftime('%d-%m-%Y %H:%M:%S') if weighing.second_weighing_time else 'N/A'),
            ("Catatan", weighing.notes or '-')
        ]

        for label, value in details:
            c.setFont("Helvetica-Bold", 8)
            c.drawString(40, y_position, f"{label}:")
            c.setFont("Helvetica", 8)
            c.drawString(160, y_position, str(value))
            y_position -= 18

        c.showPage()
        c.save()
        pdf_buffer.seek(0)

        response = make_response(pdf_buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=nota_penimbangan_{id}.pdf'
        return response

    except NotFound as e:
        return jsonify({'message': 'Not found.', 'error': str(e), 'status_code': 404}), 404
    except SQLAlchemyError as e:
        return jsonify({'message': 'Failed to generate PDF.', 'error': str(e), 'status_code': 500}), 500
    except Exception as e:
        return jsonify({'message': 'An unexpected error occurred.', 'error': str(e)}), 500
    
@weighing_controller.route('/api/weighing/total_waste', methods=['GET'])
def get_total_weighing_per_day():
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        total_waste = (
            db.session.query(
                db.func.date(TruckWeighing.first_weighing_time).label('date'),
                db.func.sum(TruckWeighing.net_weight).label('total_weight')
            )
            .filter(TruckWeighing.first_weighing_time >= start_date)
            .filter(TruckWeighing.first_weighing_time <= end_date)
            .group_by(db.func.date(TruckWeighing.first_weighing_time))
            .order_by(db.func.date(TruckWeighing.first_weighing_time))
            .all()
        )

        if not total_waste:
            return jsonify({
                'message': 'No weighing records found for the last month.',
                'status_code': 200,
                'data': []
            }), 200
        
        waste_data = [{'date': record.date.strftime('%d-%m-%Y'), 'total_weight': record.total_weight} for record in total_waste]

        return jsonify({
            'message': 'Total waste per day retrieved successfully!',
            'status_code': 200,
            'data': waste_data
        }), 200

    except SQLAlchemyError as e:
        return jsonify({'message': 'Failed to retrieve total waste records.', 'error': str(e), 'status_code': 500}), 500
    except Exception as e:
        return jsonify({'message': 'An unexpected error occurred.', 'error': str(e), 'status_code': 500}), 500
