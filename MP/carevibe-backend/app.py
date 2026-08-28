from flask import Flask, jsonify
from flask_cors import CORS
from config import Config, config_by_name
import database
from routes import api
import os

def create_app(config_name=None):
    """Application factory"""
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    config = config_by_name.get(config_name, config_by_name['development'])
    app.config.from_object(config)
    
    # Initialize CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize database
    database.init_db()
    
    # Register blueprints
    app.register_blueprint(api)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'message': 'Internal server error'}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'message': 'Bad request'}), 400
    
    # Root route
    @app.route('/')
    def index():
        return jsonify({
            'message': 'CAREVIBE Backend API',
            'version': '1.0.0',
            'status': 'running'
        }), 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
