from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class TruckWeighing(db.Model):
    __tablename__ = 'truck_weighings'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    license_plate = db.Column(db.String(20), nullable=False)
    supplier = db.Column(db.String(100), nullable=False)
    driver_name = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text)
    first_weight = db.Column(db.Float, nullable=False)
    second_weight = db.Column(db.Float)
    net_weight = db.Column(db.Float)
    status = db.Column(db.String(20), default='draft')
    first_weighing_time = db.Column(db.DateTime, default=datetime.now)
    second_weighing_time = db.Column(db.DateTime)

    def calculate_net_weight(self):
        if self.first_weight is not None and self.second_weight is not None:
            self.net_weight = self.first_weight - self.second_weight
