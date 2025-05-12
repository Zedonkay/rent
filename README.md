# Fair Rent Split Tool

A Streamlit application that helps three roommates find an envy-free rent split. The tool uses linear programming to ensure that each person gets their preferred room at a fair price.

## Features

- Input personal valuations for each room
- Automatic calculation of envy-free room assignments
- Fair rent distribution based on room preferences
- Clean and intuitive user interface
- Real-time feedback and validation

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/fair-rent-split.git
cd fair-rent-split
```

2. Create a virtual environment and activate it:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the URL shown in the terminal (usually http://localhost:8501)

3. Each roommate should:
   - Enter their name
   - Assign their personal value to each room (total must equal the rent)
   - Submit their valuations

4. Once all three roommates have submitted their valuations, the app will automatically calculate and display the envy-free room assignments and rent splits.

## How It Works

The application uses linear programming to find an envy-free solution where:
- Each person gets assigned to exactly one room
- No person would prefer another person's room at the other person's rent
- The total rent is distributed fairly based on room preferences

## License

MIT License 