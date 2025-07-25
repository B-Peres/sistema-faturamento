from flask import Blueprint, request, jsonify
from src.models.billing import db, Billing, Client
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

billings_bp = Blueprint('billings', __name__)

@billings_bp.route('/api/billings', methods=['GET'])
def get_billings():
    try:
        billings = Billing.query.all()
        
        # Atualizar status vencidos automaticamente
        today = datetime.now().date()
        for billing in billings:
            if billing.payment_status == 'pending' and billing.due_date < today:
                billing.payment_status = 'overdue'
        
        db.session.commit()
        
        return jsonify([billing.to_dict() for billing in billings])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@billings_bp.route('/api/billings', methods=['POST'])
def create_billing():
    try:
        data = request.get_json()
        
        # Validações básicas
        required_fields = ['client_id', 'product_service', 'price', 'due_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} é obrigatório'}), 400
        
        # Verificar se o cliente existe
        client = Client.query.get(data['client_id'])
        if not client:
            return jsonify({'error': 'Cliente não encontrado'}), 404
        
        # Converter data de vencimento
        due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        
        billing_type = data.get('billing_type', 'unique')
        
        if billing_type == 'installment':
            # Criar parcelamento
            installment_total = int(data.get('installment_total', 1))
            price_per_installment = float(data['price']) / installment_total
            
            # Criar cobrança pai
            parent_billing = Billing(
                client_id=data['client_id'],
                product_service=data['product_service'],
                price=float(data['price']),
                due_date=due_date,
                billing_type='installment',
                payment_status=data.get('payment_status', 'pending'),
                installment_total=installment_total,
                installment_current=0  # Cobrança pai não é uma parcela
            )
            
            db.session.add(parent_billing)
            db.session.flush()  # Para obter o ID
            
            # Criar parcelas
            for i in range(installment_total):
                installment_due_date = due_date + relativedelta(months=i)
                
                installment = Billing(
                    client_id=data['client_id'],
                    product_service=f"{data['product_service']} - Parcela {i+1}/{installment_total}",
                    price=price_per_installment,
                    due_date=installment_due_date,
                    billing_type='installment',
                    payment_status=data.get('payment_status', 'pending'),
                    installment_total=installment_total,
                    installment_current=i+1,
                    installment_parent_id=parent_billing.id
                )
                
                db.session.add(installment)
            
            db.session.commit()
            return jsonify(parent_billing.to_dict()), 201
            
        else:
            # Criar cobrança única ou recorrente
            billing = Billing(
                client_id=data['client_id'],
                product_service=data['product_service'],
                price=float(data['price']),
                due_date=due_date,
                billing_type=billing_type,
                payment_status=data.get('payment_status', 'pending'),
                recurring_frequency=data.get('recurring_frequency'),
                recurring_end_date=datetime.strptime(data['recurring_end_date'], '%Y-%m-%d').date() if data.get('recurring_end_date') else None
            )
            
            db.session.add(billing)
            db.session.commit()
            
            return jsonify(billing.to_dict()), 201
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@billings_bp.route('/api/billings/<int:billing_id>', methods=['PUT'])
def update_billing(billing_id):
    try:
        billing = Billing.query.get_or_404(billing_id)
        data = request.get_json()
        
        # Atualizar campos permitidos
        if 'product_service' in data:
            billing.product_service = data['product_service']
        if 'price' in data:
            billing.price = float(data['price'])
        if 'due_date' in data:
            billing.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        if 'payment_status' in data:
            billing.payment_status = data['payment_status']
        if 'recurring_frequency' in data:
            billing.recurring_frequency = data['recurring_frequency']
        if 'recurring_end_date' in data:
            billing.recurring_end_date = datetime.strptime(data['recurring_end_date'], '%Y-%m-%d').date() if data['recurring_end_date'] else None
        
        db.session.commit()
        
        return jsonify(billing.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@billings_bp.route('/api/billings/<int:billing_id>', methods=['DELETE'])
def delete_billing(billing_id):
    try:
        billing = Billing.query.get_or_404(billing_id)
        
        # Se for uma cobrança pai de parcelamento, excluir todas as parcelas
        if billing.billing_type == 'installment' and billing.installment_current == 0:
            installments = Billing.query.filter_by(installment_parent_id=billing.id).all()
            for installment in installments:
                db.session.delete(installment)
        
        db.session.delete(billing)
        db.session.commit()
        
        return jsonify({'message': 'Faturamento excluído com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@billings_bp.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    try:
        # Atualizar status vencidos automaticamente
        today = datetime.now().date()
        overdue_billings = Billing.query.filter(
            Billing.payment_status == 'pending',
            Billing.due_date < today
        ).all()
        
        for billing in overdue_billings:
            billing.payment_status = 'overdue'
        
        db.session.commit()
        
        # Calcular totais
        total_to_receive = db.session.query(db.func.sum(Billing.price)).filter_by(payment_status='pending').scalar() or 0
        total_overdue = db.session.query(db.func.sum(Billing.price)).filter_by(payment_status='overdue').scalar() or 0
        total_paid = db.session.query(db.func.sum(Billing.price)).filter_by(payment_status='paid').scalar() or 0
        total_cancelled = db.session.query(db.func.sum(Billing.price)).filter_by(payment_status='cancelled').scalar() or 0
        
        return jsonify({
            'total_to_receive': total_to_receive,
            'total_overdue': total_overdue,
            'total_paid': total_paid,
            'total_cancelled': total_cancelled
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

