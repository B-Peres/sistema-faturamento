from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com faturamentos
    billings = db.relationship('Billing', backref='client', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact': self.contact,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Billing(db.Model):
    __tablename__ = 'billings'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    product_service = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    billing_type = db.Column(db.String(20), nullable=False, default='unique')  # unique, recurring, installment
    payment_status = db.Column(db.String(20), nullable=False, default='pending')  # pending, paid, overdue, cancelled
    
    # Campos para cobrança recorrente
    recurring_frequency = db.Column(db.String(20))  # weekly, monthly, yearly
    recurring_end_date = db.Column(db.Date)
    
    # Campos para parcelamento
    installment_total = db.Column(db.Integer)  # número total de parcelas
    installment_current = db.Column(db.Integer)  # parcela atual
    installment_parent_id = db.Column(db.Integer, db.ForeignKey('billings.id'))  # referência à cobrança pai
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento para parcelas filhas
    installments = db.relationship('Billing', backref=db.backref('parent', remote_side=[id]), lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'client_name': self.client.name if self.client else None,
            'product_service': self.product_service,
            'price': self.price,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'billing_type': self.billing_type,
            'payment_status': self.payment_status,
            'recurring_frequency': self.recurring_frequency,
            'recurring_end_date': self.recurring_end_date.isoformat() if self.recurring_end_date else None,
            'installment_total': self.installment_total,
            'installment_current': self.installment_current,
            'installment_parent_id': self.installment_parent_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

