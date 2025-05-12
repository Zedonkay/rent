document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('valuationForm');
    const submissionsList = document.getElementById('submissionsList');
    const progressBar = document.getElementById('progressBar');
    const resultsSection = document.getElementById('results');
    const resetButton = document.getElementById('resetButton');
    const currentSubmissions = document.getElementById('currentSubmissions');
    const TOTAL_RENT = 2380;

    // Initialize room values
    const roomInputs = {
        room1: document.getElementById('room1'),
        room2: document.getElementById('room2'),
        room3: document.getElementById('room3')
    };

    // Set initial values
    Object.values(roomInputs).forEach(input => {
        input.value = (TOTAL_RENT / 3).toFixed(2);
    });

    // Function to calculate remaining values
    function updateRemainingValues(changedInput) {
        const filledInputs = Object.entries(roomInputs)
            .filter(([_, input]) => input.value && input !== changedInput)
            .map(([_, input]) => parseFloat(input.value));

        const remainingInputs = Object.entries(roomInputs)
            .filter(([_, input]) => !input.value || input === changedInput)
            .map(([_, input]) => input);

        if (filledInputs.length === 0) {
            // If no values are filled, set all to equal
            Object.values(roomInputs).forEach(input => {
                input.value = (TOTAL_RENT / 3).toFixed(2);
            });
        } else if (filledInputs.length === 1) {
            // If one value is filled, split remaining equally
            const remaining = TOTAL_RENT - filledInputs[0];
            remainingInputs.forEach(input => {
                input.value = (remaining / 2).toFixed(2);
            });
        } else if (filledInputs.length === 2) {
            // If two values are filled, set last to remaining
            const remaining = TOTAL_RENT - filledInputs.reduce((a, b) => a + b, 0);
            remainingInputs[0].value = remaining.toFixed(2);
        }
    }

    // Add event listeners for input changes
    Object.values(roomInputs).forEach(input => {
        input.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value) || 0;
            if (value < 0) {
                e.target.value = 0;
            }
            updateRemainingValues(e.target);
        });

        input.addEventListener('focus', (e) => {
            e.target.select();
        });
    });

    // Update progress bar and check submissions
    async function updateProgress() {
        try {
            const response = await fetch('/api/submissions');
            const data = await response.json();
            
            const count = data.submissions.length;
            progressBar.style.width = `${(count / 3) * 100}%`;
            
            if (count > 0) {
                currentSubmissions.classList.remove('hidden');
                submissionsList.innerHTML = data.submissions.map(sub => `
                    <div class="room-card fade-in">
                        <p class="font-semibold">${sub.name}</p>
                        <p class="text-sm text-gray-600">Submitted ${new Date(sub.timestamp).toLocaleString()}</p>
                    </div>
                `).join('');
            }

            if (count === 3) {
                calculateAssignments();
            }
        } catch (error) {
            console.error('Error updating progress:', error);
        }
    }

    // Handle form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(form);
        const data = {
            name: formData.get('name'),
            values: [
                parseFloat(formData.get('room1')),
                parseFloat(formData.get('room2')),
                parseFloat(formData.get('room3'))
            ]
        };

        try {
            const response = await fetch('/api/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            
            if (result.success) {
                form.reset();
                // Reset room values to initial state
                Object.values(roomInputs).forEach(input => {
                    input.value = (TOTAL_RENT / 3).toFixed(2);
                });
                updateProgress();
            } else {
                alert(result.error || 'Error submitting valuations');
            }
        } catch (error) {
            console.error('Error submitting form:', error);
            alert('Error submitting valuations');
        }
    });

    // Calculate room assignments
    async function calculateAssignments() {
        try {
            const response = await fetch('/api/calculate');
            const data = await response.json();
            
            if (data.success) {
                resultsSection.classList.remove('hidden');
                document.getElementById('methodUsed').textContent = data.method;
                document.getElementById('methodExplanation').textContent = data.explanation;
                
                const assignmentsList = document.getElementById('assignmentsList');
                assignmentsList.innerHTML = data.assignments.map(assignment => `
                    <div class="room-card fade-in">
                        <p class="font-semibold">${assignment.person}</p>
                        <p>Assigned to: ${assignment.room}</p>
                        <p>Valuation: $${assignment.valuation.toFixed(2)}</p>
                        <p>Rent: $${assignment.rent.toFixed(2)}</p>
                    </div>
                `).join('');
                
                resetButton.classList.remove('hidden');
            } else {
                alert(data.error || 'Error calculating assignments');
            }
        } catch (error) {
            console.error('Error calculating assignments:', error);
            alert('Error calculating assignments');
        }
    }

    // Handle reset
    resetButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/api/reset', { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                location.reload();
            } else {
                alert(data.error || 'Error resetting submissions');
            }
        } catch (error) {
            console.error('Error resetting:', error);
            alert('Error resetting submissions');
        }
    });

    // Initial progress update
    updateProgress();
}); 