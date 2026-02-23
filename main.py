from flask import Flask, jsonify, request
from forexFactoryScrapper import getRecords, getURL
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/api/hello', methods=['GET'])
def hello():
    response_data = {
        'message': 'Hello, World!',
        'status': 'success'
    }
    return jsonify(response_data), 200


@app.route('/api/health', methods=['GET'])
def health():
    """Health endpoint for quick liveness check."""
    return jsonify({'status': 'ok'}), 200


@app.route('/api/forex/daily', methods=['GET'])
def daily_data():
    # validate presence
    day = request.args.get('day')
    month = request.args.get('month')
    year = request.args.get('year')

    if not (day and month and year):
        return jsonify({
            'error': 'Missing one or more required parameters: day, month, year'
        }), 400  # HTTP 400 Bad Request

    # validate types
    try:
        day_i = int(day)
        month_i = int(month)
        year_i = int(year)
    except ValueError:
        return jsonify({'error': 'Parameters day, month and year must be integers'}), 400

    # simple range checks
    if not (1 <= day_i <= 31 and 1 <= month_i <= 12 and 1900 <= year_i <= 2100):
        return jsonify({'error': 'Parameters out of reasonable range'}), 400

    try:
        url = getURL(day_i, month_i, year_i, 'day')
        record_json = getRecords(url)
    except Exception as e:
        logger.exception('Failed to fetch or parse records')
        return jsonify({'error': 'Failed to fetch records', 'detail': str(e)}), 502

    return jsonify(record_json), 200


if __name__ == '__main__':
    # Keep debug configurable via env if desired; default to False in production
    app.run(host='0.0.0.0', port=5000, debug=True)
