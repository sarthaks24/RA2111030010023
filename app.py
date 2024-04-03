from flask import Flask, jsonify
from collections import deque
import requests
import time

app = Flask(__name__)

# Window size
WINDOW_SIZE = 10

# Window data structure (Deque is used for efficient removal of oldest element)
window = deque(maxlen=WINDOW_SIZE)

# Mapping of number types
number_types = {'p': 'prime', 'f': 'fibonacci', 'e': 'even', 'r': 'random'}

@app.route('/numbers/<numberid>', methods=['GET'])
def get_number(numberid):
    global window

    # Check if numberid is valid
    if numberid not in number_types:
        return jsonify(error="Invalid numberid"), 400

    # Fetch number from the test server
    start_time = time.time()
    response = requests.get(f'http://20.244.56.144/test/{number_types[numberid]}')
    elapsed_time = time.time() - start_time

    # Check response time
    if elapsed_time > 0.5:
        return jsonify(error="Test server response time exceeded 500ms"), 503

    # Check response status
    if response.status_code != 200:
        return jsonify(error="Error occurred while fetching number from test server"), 500

    # Get the numbers
    numbers = response.json().get('numbers')

    # Save the previous state of the window
    prev_window_state = list(window)

    # Add the numbers to the window
    for number in numbers:
        # Check if number is already in the window
        if number not in window:
            window.append(number)

    # Calculate the average
    avg = sum(window) / len(window)

    # Prepare the response
    result = {
        "numbers": numbers,
        "windowPrevState": prev_window_state,
        "windowCurrState": list(window),
        "avg": avg
    }

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=9876)
