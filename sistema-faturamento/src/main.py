import os
import sys
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.billing import db
from src.routes.clients import clients_bp
from src.routes.billings import billings_bp

def create_app():
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Configurações
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sistema-faturamento-2025-dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Habilitar CORS para todas as rotas
    CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])
    
    # Configurar logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/sistema_faturamento.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Sistema de Faturamento iniciado')
    
    # Inicializar banco de dados
    db.init_app(app)
    
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.error(f'Erro ao criar tabelas do banco: {e}')
    
    # Registrar blueprints
    app.register_blueprint(clients_bp)
    app.register_blueprint(billings_bp)
    
    # Tratamento de erros globais
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Recurso não encontrado'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500
    
    # Rota para servir o frontend React
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return jsonify({'error': 'Pasta static não configurada'}), 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return jsonify({'error': 'Interface não encontrada'}), 404
    
    # Rota de health check
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'version': '2.0',
            'python_version': sys.version,
            'timestamp': datetime.now().isoformat()
        })
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

