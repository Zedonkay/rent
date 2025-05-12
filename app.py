import streamlit as st
import numpy as np
import itertools
from scipy.optimize import linprog
import json
import os
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Fair Rent Split",
    page_icon="🏠",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 0.5rem;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .success-box {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🏠 Fair Rent Split Tool")
st.markdown("""
This tool helps three roommates find an envy-free rent split. Each person should:
1. Enter their name
2. Assign their personal value to each room (total must equal the rent)
3. Submit their valuations
""")

ROOM_LABELS = ["Backyard Window Room", "Small Room", "Middle Room"]
TOTAL_RENT = 2380

# Data storage functions
def load_submissions():
    if os.path.exists('submissions.json'):
        with open('submissions.json', 'r') as f:
            return json.load(f)
    return []

def save_submissions(submissions):
    with open('submissions.json', 'w') as f:
        json.dump(submissions, f, indent=2)

# Initialize session state
if "submissions" not in st.session_state:
    st.session_state.submissions = load_submissions()

# Input form
with st.form("valuation_form"):
    st.subheader("📝 Enter Your Room Valuations")
    name = st.text_input("Your name", placeholder="Enter your name")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        val1 = st.number_input(f"{ROOM_LABELS[0]}", min_value=0.0, value=800.0, help="How much do you value this room?")
    with col2:
        val2 = st.number_input(f"{ROOM_LABELS[1]}", min_value=0.0, value=700.0, help="How much do you value this room?")
    with col3:
        val3 = st.number_input(f"{ROOM_LABELS[2]}", min_value=0.0, value=880.0, help="How much do you value this room?")

    submitted = st.form_submit_button("Submit Valuations")

    if submitted:
        total = val1 + val2 + val3
        if abs(total - TOTAL_RENT) > 1e-3:
            st.markdown(f"""
            <div class="error-box">
                ❌ Please make sure your total valuation sums to ${TOTAL_RENT}
            </div>
            """, unsafe_allow_html=True)
        else:
            submission = {
                "name": name,
                "values": [val1, val2, val3],
                "timestamp": datetime.now().isoformat()
            }
            st.session_state.submissions.append(submission)
            save_submissions(st.session_state.submissions)
            st.markdown(f"""
            <div class="success-box">
                ✅ Thanks {name}! Your valuations have been recorded.
            </div>
            """, unsafe_allow_html=True)

# Display submissions
if st.session_state.submissions:
    st.subheader("👥 Submitted Valuations")
    for sub in st.session_state.submissions:
        st.markdown(f"""
        **{sub['name']}**'s valuations (submitted at {datetime.fromisoformat(sub['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}):
        - {ROOM_LABELS[0]}: ${sub['values'][0]:.2f}
        - {ROOM_LABELS[1]}: ${sub['values'][1]:.2f}
        - {ROOM_LABELS[2]}: ${sub['values'][2]:.2f}
        """)

# Envy-free allocation once 3 submissions received
if len(st.session_state.submissions) == 3:
    names = [sub["name"] for sub in st.session_state.submissions]
    valuations = np.array([sub["values"] for sub in st.session_state.submissions])
    total_rent = TOTAL_RENT

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
                "prices": prices
            }
            break

    if best_solution:
        st.markdown("""
        <div class="success-box">
            🎉 Envy-free allocation found!
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("📊 Final Room Assignments")
        for i, person in enumerate(names):
            room_index = best_solution["assignment"][i]
            room_label = ROOM_LABELS[room_index]
            rent = best_solution["prices"][room_index]
            st.markdown(f"""
            **{person}** → {room_label}
            - Monthly Rent: **${rent:.2f}**
            """)
    else:
        st.markdown("""
        <div class="error-box">
            ❌ Could not find an envy-free solution.
        </div>
        """, unsafe_allow_html=True)

# Reset button
if st.button("🔄 Reset All Submissions"):
    st.session_state.submissions = []
    save_submissions([])
    st.experimental_rerun()
