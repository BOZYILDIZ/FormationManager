from app import db
from datetime import datetime

class Formation(db.Model):
    __tablename__ = 'formations'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)  # validé, accepté, refusé
    code = db.Column(db.String(20), nullable=True)  # Code RS de la formation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relation avec Client
    clients = db.relationship('Client', backref='formation', lazy=True)
    
    def __repr__(self):
        return f'<Formation {self.title}>'
    
    def calculate_bon_value(self):
        """Calcule la valeur du bon d'achat (30% du prix de la formation)"""
        return round(self.price * 0.3, 2) 