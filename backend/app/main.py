from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['ENV'] = os.getenv('FLASK_ENV', 'development')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', False)

@app.route('/', methods=['GET'])
def home():
     return jsonify({'message': 'Welcome to Sentexa Backend'})

@app.route('/health', methods=['GET'])
def health():
     return jsonify({'status': 'healthy'}), 200

@app.errorhandler(404)
def not_found(error):
     return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
     return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
     app.run(
          host=os.getenv('HOST', '0.0.0.0'),
          port=int(os.getenv('PORT', 5000)),
          debug=app.config['DEBUG']
     )