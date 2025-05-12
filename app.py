from flask import Flask, request, jsonify, render_template, send_from_directory
import numpy as np
import itertools
from scipy.optimize import linprog
import json
import os
from datetime import datetime

app = Flask(__name__, static_url_path='')

ROOM_LABELS = ["Backyard Window Room", "Small Room", "Middle Room"]
TOTAL_RENT = 2380

# Data storage functions
def load_submissions():
    data_file = 'submissions.json'
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            return json.load(f)
    return []

def save_submissions(submissions):
    with open('submissions.json', 'w') as f:
        json.dump(submissions, f, indent=2)

def get_user_submission(submissions, name):
    for sub in submissions:
        if sub['name'].lower() == name.lower():
            return sub
    return None

def linear_programming_solution(valuations, total_rent):
    room_indices = [0, 1, 2]
    best_solution = None

    for perm in itertools.permutations(room_indices):
        A = []
        b = []

        for i in range(3):
            for j in range(3):
                if i != j:
                    pi = perm[i]
                    pj = perm[j]
                    vi = valuations[i]
                    A.append(np.eye(3)[pi] - np.eye(3)[pj])
                    b.append(vi[pi] - vi[pj])

        A_eq = [[1, 1, 1]]
        b_eq = [total_rent]

        res = linprog(
            c=[0, 0, 0],
            A_ub=A,
            b_ub=b,
            A_eq=A_eq,
            b_eq=b_eq,
            bounds=[(0, total_rent)] * 3,
            method='highs'
        )

        if res.success:
            prices = res.x
            best_solution = {
                "assignment": perm,
                "prices": prices.tolist()
            }
            break

    return best_solution

def last_diminisher_algorithm(valuations, total_rent):
    n = len(valuations)
    assignments = [-1] * n
    prices = [0] * n
    remaining_rent = total_rent
    
    # First person gets their most valued room
    first_person = 0
    first_room = np.argmax(valuations[first_person])
    assignments[first_person] = first_room
    prices[first_room] = valuations[first_person][first_room]
    remaining_rent -= prices[first_room]
    
    # Second person's turn
    second_person = 1
    second_room = np.argmax(valuations[second_person])
    if valuations[second_person][first_room] > valuations[second_person][second_room]:
        assignments[second_person] = first_room
        assignments[first_person] = second_room
        prices[first_room] = valuations[second_person][first_room]
        prices[second_room] = valuations[first_person][second_room]
    else:
        assignments[second_person] = second_room
        prices[second_room] = valuations[second_person][second_room]
    
    # Third person gets remaining room
    third_person = 2
    remaining_room = [r for r in range(n) if r not in assignments][0]
    assignments[third_person] = remaining_room
    prices[remaining_room] = total_rent - sum(prices)
    
    return assignments, prices

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def style():
    return send_from_directory('.', 'style.css')

@app.route('/main.js')
def script():
    return send_from_directory('.', 'main.js')

@app.route('/api/submit', methods=['POST'])
def submit_valuation():
    data = request.json
    name = data.get('name')
    values = data.get('values')
    
    if not name or not values:
        return jsonify({'error': 'Missing name or values'}), 400
    
    if len(values) != 3:
        return jsonify({'error': 'Must provide exactly 3 values'}), 400
    
    total = sum(values)
    if abs(total - TOTAL_RENT) > 1e-3:
        return jsonify({'error': f'Total must equal {TOTAL_RENT}'}), 400
    
    submissions = load_submissions()
    if get_user_submission(submissions, name):
        return jsonify({'error': 'You have already submitted your valuations'}), 400
    
    submission = {
        'name': name,
        'values': values,
        'timestamp': datetime.now().isoformat()
    }
    submissions.append(submission)
    save_submissions(submissions)
    
    return jsonify({'message': 'Submission successful'})

@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    submissions = load_submissions()
    return jsonify(submissions)

@app.route('/api/calculate', methods=['GET'])
def calculate_assignments():
    submissions = load_submissions()
    if len(submissions) != 3:
        return jsonify({'error': 'Need exactly 3 submissions'}), 400
    
    names = [sub['name'] for sub in submissions]
    valuations = np.array([sub['values'] for sub in submissions])
    
    # Try linear programming first
    solution = linear_programming_solution(valuations, TOTAL_RENT)
    
    if solution:
        result = {
            'method': 'linear_programming',
            'assignments': solution['assignment'],
            'prices': solution['prices'],
            'names': names,
            'valuations': valuations.tolist()
        }
    else:
        # Fall back to Last Diminisher
        assignments, prices = last_diminisher_algorithm(valuations, TOTAL_RENT)
        result = {
            'method': 'last_diminisher',
            'assignments': assignments,
            'prices': prices,
            'names': names,
            'valuations': valuations.tolist()
        }
    
    return jsonify(result)

@app.route('/api/reset', methods=['POST'])
def reset_submissions():
    save_submissions([])
    return jsonify({'message': 'Submissions reset successfully'})

if __name__ == '__main__':
    app.run(debug=True)
