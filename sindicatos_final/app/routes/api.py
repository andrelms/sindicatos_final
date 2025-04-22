"""
Rotas da API da aplicação.
"""
from flask import jsonify, request
from app.routes import api_bp

@api_bp.route('/status')
def status():
    """Retorna o status da API"""
    return jsonify({
        'status': 'online',
        'version': '1.0.0'
    }) 