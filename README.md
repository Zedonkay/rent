# 🏠 Fair Rent Split Tool

A modern web application that helps three roommates find an envy-free rent split using advanced fair division algorithms. The tool ensures that each person gets a room they value at least as much as any other room, while maintaining the total rent constraint.

## ✨ Features

- **Modern UI/UX**: Clean, responsive design with smooth animations and intuitive interface
- **Two-Step Solution**:
   1. Linear Programming: Attempts to find the most efficient envy-free allocation
   2. Selfridge-Conway Algorithm: Fallback method that guarantees a fair solution
- **Real-time Progress Tracking**: Visual feedback on submission status
- **Privacy-Focused**: Submissions are only revealed after all three participants have submitted
- **Detailed Explanations**: Clear breakdown of the method used and each person's valuation
- **Mobile Responsive**: Works seamlessly on all devices

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/rent-split.git
    cd rent-split
    ```

2. Create a virtual environment (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the application:
    ```bash
    python app.py
    ```

5. Open your browser and navigate to `http://localhost:5000`

## 🎯 How It Works

1. **Submission Phase**:
    - Each roommate enters their name and valuations for all three rooms
    - The total of valuations must equal the total rent
    - Submissions are kept private until all three have submitted

2. **Calculation Phase**:
    - The system first attempts to find an optimal solution using linear programming
    - If no solution is found, it falls back to the Selfridge-Conway algorithm
    - Results show each person's assigned room, their valuation, and the rent they'll pay

3. **Results**:
    - Clear explanation of the method used
    - Detailed breakdown of assignments and valuations
    - Option to start a new round

## 🛠️ Technical Details

- **Frontend**: HTML5, CSS3, JavaScript (with Tailwind CSS for styling)
- **Backend**: Python (Flask)
- **Algorithms**:
   - Linear Programming (using SciPy)
   - Selfridge-Conway Algorithm
- **Data Storage**: JSON file-based storage

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter) - email@example.com

Project Link: [https://github.com/yourusername/rent-split](https://github.com/yourusername/rent-split) 