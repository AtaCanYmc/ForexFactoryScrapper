from flask import Flask, jsonify, request
from forexFactoryScrapper import getRecords, getURL

app = Flask(__name__)


@app.route('/api/hello', methods=['GET'])
def hello():
    response_data = {
        'message': 'Hello, World!',
        'status': 'success'
    }
    return jsonify(response_data), 200


@app.route('/api/forex/daily', methods=['GET'])
def daily_data():
    day = request.args.get('day')
    month = request.args.get('month')
    year = request.args.get('year')

    if not (day and month and year):
        return jsonify({
            'error': 'Missing one or more required parameters: day, month, year'
        }), 400  # HTTP 400 Bad Request

    url = getURL(day, month, year, 'day')
    record_json = getRecords(url)
    return jsonify(record_json), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
