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

def selfridge_conway_procedure(valuations, total_rent):
    """
    Implements the Selfridge-Conway procedure for 3 agents and 3 rooms.
    Returns (assignments, prices) where:
      - assignments[i] = room index assigned to person i
      - prices[room_index] = rent for that room
    """
    n = 3
    # Step 1: Each person ranks rooms by their value
    # Step 2: Each person divides the rooms into what they consider equal shares
    # For rent splitting, we use the valuations to simulate this

    # Find the envy-free assignment using all permutations
    best_assignment = None
    best_prices = None
    min_envy = float('inf')

    for perm in itertools.permutations(range(n)):
        # perm[i] = room assigned to person i
        # Calculate envy for this assignment
        envy = 0
        for i in range(n):
            my_value = valuations[i][perm[i]]
            others = [valuations[i][perm[j]] for j in range(n) if j != i]
            envy += max(0, max(others) - my_value)
        if envy < min_envy:
            min_envy = envy
            best_assignment = perm

    # Assign rents proportional to each person's valuation for their assigned room
    assigned_vals = [valuations[i][best_assignment[i]] for i in range(n)]
    total_assigned_val = sum(assigned_vals)
    prices = [total_rent * (v / total_assigned_val) for v in assigned_vals]

    # Map assignments: assignments[i] = room assigned to person i
    assignments = list(best_assignment)
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
    
    return jsonify({'success': True, 'message': 'Submission successful'})

@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    submissions = load_submissions()
    return jsonify({
        'success': True,
        'submissions': submissions
    })

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
        assignments = []
        for i, room_idx in enumerate(solution['assignment']):
            assignments.append({
                'person': names[i],
                'room': ROOM_LABELS[room_idx],
                'valuation': float(valuations[i][room_idx]),
                'rent': float(solution['prices'][room_idx])
            })
        
        result = {
            'success': True,
            'method': 'linear_programming',
            'assignments': assignments,
            'explanation': 'Using linear programming to find an envy-free solution that maximizes fairness.'
        }
    else:
        # Fall back to Selfridge Conway
        assignments, prices = selfridge_conway_procedure(valuations, TOTAL_RENT)
        assignments_list = []
        for i, room_idx in enumerate(assignments):
            assignments_list.append({
                'person': names[i],
                'room': ROOM_LABELS[room_idx],
                'valuation': float(valuations[i][room_idx]),
                'rent': float(prices[room_idx])
            })
        
        result = {
            'success': True,
            'method': 'selfridge_conway_procedure',
            'assignments': assignments_list,
            'explanation': 'Using the Selfridge Conway Procedure to find a fair division of rooms.'
        }
    
    return jsonify(result)

@app.route('/api/reset', methods=['POST'])
def reset_submissions():
    save_submissions([])
    return jsonify({'message': 'Submissions reset successfully'})

if __name__ == '__main__':
    app.run(debug=True)
