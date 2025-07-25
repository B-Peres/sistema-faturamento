from flask import Blueprint, request, jsonify
from src.models.billing import db, Client

clients_bp = Blueprint('clients', __name__)

@clients_bp.route('/api/clients', methods=['GET'])
def get_clients():
    try:
        clients = Client.query.all()
        return jsonify([client.to_dict() for client in clients])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/api/clients', methods=['POST'])
def create_client():
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Nome é obrigatório'}), 400
        
        client = Client(
            name=data['name'],
            contact=data.get('contact', ''),
            email=data.get('email', ''),
            phone=data.get('phone', '')
        )
        
        db.session.add(client)
        db.session.commit()
        
        return jsonify(client.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/api/clients/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    try:
        client = Client.query.get_or_404(client_id)
        data = request.get_json()
        
        client.name = data.get('name', client.name)
        client.contact = data.get('contact', client.contact)
        client.email = data.get('email', client.email)
        client.phone = data.get('phone', client.phone)
        
        db.session.commit()
        
        return jsonify(client.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/api/clients/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    try:
        client = Client.query.get_or_404(client_id)
        db.session.delete(client)
        db.session.commit()
        
        return jsonify({'message': 'Cliente excluído com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

