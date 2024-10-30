from flask import Blueprint, request, jsonify, make_response
from models.weighing_record import db, TruckWeighing
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest, NotFound
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

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
        weighings = TruckWeighing.query.all()
        
        if not weighings:
            return jsonify({
                'message': 'No weighing records found.',
                'status_code': 200,
                'data': []
            }), 200
    
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
        } for weighing in weighings]

        return jsonify({
            'message': 'Weighing records retrieved successfully!',
            'status_code': 200,
            'data': weighing_list
        }), 200

    except SQLAlchemyError as e:
        return jsonify({'message': 'Failed to retrieve weighing records.', 'error': str(e)}), 500
    except Exception as e:
        return jsonify({'message': 'An unexpected error occurred.', 'error': str(e)}), 500
    
@weighing_controller.route('/api/weighing/<id>/pdf', methods=['GET'])
def generate_weighing_pdf(id):
    try:
        weighing = TruckWeighing.query.get(id)
        if not weighing:
            raise NotFound(f"Weighing record with ID {id} not found.")

        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 20)
        c.drawString(100, height - 80, "TPST Sinduadi")
        c.setFont("Helvetica", 12)
        c.drawString(100, height - 100, "Jl. Sinduadi No. 123, Sleman, Yogyakarta")
        c.drawString(100, height - 115, "Tel: +62 123 456 789 | Email: info@tpstsinduadi.com")
        c.line(40, height - 125, width - 40, height - 125)

        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, height - 160, "Nota Penimbangan")
        
        c.setFont("Helvetica", 12)
        y_position = height - 200
        details = [
            f"Nomor Polisi: {weighing.license_plate}",
            f"Supplier: {weighing.supplier}",
            f"Supir: {weighing.driver_name}",
            f"Timbangan Pertama: {weighing.first_weight} kg",
            f"Timbangan Kedua: {weighing.second_weight or 'N/A'} kg",
            f"Berat Bersih: {weighing.net_weight or 'N/A'} kg",
            f"Waktu Penimbangan Pertama: {weighing.first_weighing_time.strftime('%d-%m-%Y %H:%M:%S')}",
            f"Waktu Penimbangan Kedua: {weighing.second_weighing_time.strftime('%d-%m-%Y %H:%M:%S') if weighing.second_weighing_time else 'N/A'}",
            f"Catatan: {weighing.notes or '-'}"
        ]

        for detail in details:
            c.drawString(100, y_position, detail)
            y_position -= 20

        y_position -= 40 
        c.drawString(100, y_position, "Petugas:")
        c.line(150, y_position - 5, 300, y_position - 5) 

        c.showPage()
        c.save()
        pdf_buffer.seek(0)

        response = make_response(pdf_buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=nota_penimbangan_{id}.pdf'
        return response

    except NotFound as e:
        return jsonify({'message': 'Not found.', 'error': str(e), 'status_code': 404}), 404
    except SQLAlchemyError as e:
        return jsonify({'message': 'Failed to generate PDF.', 'error': str(e), 'status_code': 500}), 500
    except Exception as e:
        return jsonify({'message': 'An unexpected error occurred.', 'error': str(e)}), 500
    
@weighing_controller.route('/api/weighing/filter', methods=['GET'])
def get_filtered_weighings():
    try:
        date = request.args.get('date')
        month = request.args.get('month')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = TruckWeighing.query

        if date:
            try:
                specific_date = datetime.strptime(date, '%Y-%m-%d')
                query = query.filter(db.func.date(TruckWeighing.first_weighing_time) == specific_date.date())
            except ValueError:
                raise BadRequest("Invalid date format. Use YYYY-MM-DD.")
        
        elif month:
            try:
                specific_month = datetime.strptime(month, '%Y-%m')
                query = query.filter(
                    db.func.extract('year', TruckWeighing.first_weighing_time) == specific_month.year,
                    db.func.extract('month', TruckWeighing.first_weighing_time) == specific_month.month
                )
            except ValueError:
                raise BadRequest("Invalid month format. Use YYYY-MM.")
        
        elif start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
                query = query.filter(TruckWeighing.first_weighing_time >= start, TruckWeighing.first_weighing_time <= end)
            except ValueError:
                raise BadRequest("Invalid date format. Use YYYY-MM-DD for start_date and end_date.")
        
        weighings = query.all()

        if not weighings:
            return jsonify({
                'message': 'No weighing records found.',
                'status_code': 200,
                'data': []
            }), 200
        
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
        } for weighing in weighings]

        return jsonify({
            'message': 'Filtered weighing records retrieved successfully!',
            'status_code': 200,
            'data': weighing_list
        }), 200

    except BadRequest as e:
        return jsonify({'message': 'Bad request.', 'error': str(e), 'status_code': 400}), 400
    except SQLAlchemyError as e:
        return jsonify({'message': 'Failed to retrieve weighing records.', 'error': str(e), 'status_code': 500}), 500
    except Exception as e:
        return jsonify({'message': 'An unexpected error occurred.', 'error': str(e)}), 500