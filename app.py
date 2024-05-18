from flask import Flask, request, jsonify
from utils import mock_model_predict
from redis import Redis
from rq import Queue
from rq.job import Job
from rq.exceptions import NoSuchJobError

app = Flask(__name__)

redis_conn = Redis(host='redis', port=6379)

q = Queue(connection=redis_conn)


@app.route('/predict', methods=['POST'])
def predict():
    """
    Perform prediction either in Sync or Async Mode.

    Headers:
        Async-Mode: true/false (Optional)

    Request Body (JSON):
        input (str)

    Returns:
        response (JSON)
        status_code (int)
    """
    
    data = request.get_json()

    async_mode = request.headers.get('Async-Mode', 'false').lower() == 'true'

    if async_mode:
        prediction = q.enqueue(mock_model_predict, data['input'])
    else:
        prediction = mock_model_predict(data['input'])

    response = {}

    if async_mode:
        response['message'] = 'Request received. Processing asynchronously.'
        response['prediction_id'] = prediction.id
    else: 
        response = prediction
    
    return jsonify(response), 201 if async_mode else 200

@app.route('/predict/<prediction_id>', methods=['GET'])
def get_prediction(prediction_id):
    """
    Get result from Async prediction.

    Args:
        prediction_id (str)

    Returns:
        response (JSON)
        status_code (int)
    """
    try:
        prediction = Job.fetch(prediction_id, connection=redis_conn)
        if prediction.is_finished:
            result = {
                'prediction_id': prediction_id,
                'output': prediction.result
            }

            return jsonify(result)
        else:
            result = {
                'error': 'Prediction is still being processed.'
            }

            return jsonify(result), 400
    
    except NoSuchJobError as e:

        result = {
            'error': 'Prediction ID not found.'
        }
        return jsonify(result), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
