from app import db
from datetime import datetime, timedelta

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    cpf_id = db.Column(db.String(50), unique=True, nullable=True, index=True)  # Identifiant CPF unique
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    formation_id = db.Column(db.Integer, db.ForeignKey('formations.id'), nullable=False)
    bon_value = db.Column(db.Float, nullable=False, default=0.0)
    bon_percentage = db.Column(db.Float, nullable=False, default=30.0)  # Pourcentage par défaut (30%)
    use_fixed_bon = db.Column(db.Boolean, default=False)  # Utiliser une valeur fixe ou un pourcentage
    invoice_date = db.Column(db.DateTime, nullable=True)
    expected_payment_date = db.Column(db.DateTime, nullable=True)
    payment_received = db.Column(db.Boolean, default=False)
    start_date = db.Column(db.DateTime, nullable=True)  # Date de début de formation
    end_date = db.Column(db.DateTime, nullable=True)  # Date de fin de formation
    status = db.Column(db.String(50), default='accepté')  # Statut du dossier (accepté, en formation, etc.)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relation avec Product
    products = db.relationship('Product', backref='client', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Client {self.name}>'
    
    def update_expected_payment_date(self):
        """Calcule la date de paiement attendue (invoice_date + 30 jours)"""
        if self.invoice_date:
            self.expected_payment_date = self.invoice_date + timedelta(days=30)
    
    def update_bon_value(self):
        """Met à jour la valeur du bon d'achat en fonction du prix de la formation"""
        if self.formation:
            if self.use_fixed_bon:
                # Utiliser la valeur fixe déjà définie
                pass
            else:
                # Calculer en fonction du pourcentage
                self.bon_value = round(self.formation.price * (self.bon_percentage / 100), 2)
    
    def get_status_display(self):
        """Retourne le statut du client formaté pour l'affichage"""
        if self.payment_received:
            return 'service_fait_validé'
        elif self.invoice_date:
            return 'service_fait_déclaré'
        elif self.end_date and self.end_date < datetime.utcnow():
            return 'sortie_formation'
        elif self.start_date and self.start_date <= datetime.utcnow():
            return 'en_formation'
        else:
            return 'accepté' 