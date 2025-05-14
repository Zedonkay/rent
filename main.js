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
        room1: {
            element: document.getElementById('room1'),
            label: "Backyard Window Room",
            value: ""
        },
        room2: {
            element: document.getElementById('room2'),
            label: "Small Room",
            value: ""
        },
        room3: {
            element: document.getElementById('room3'),
            label: "Middle Room",
            value: ""
        }
    };

    // Function to update remaining amount display
    function updateRemainingAmount() {
        const inputs = Object.values(roomInputs).map(room => room.element);
        const totalEntered = inputs.reduce((sum, input) => {
            const value = parseFloat(input.value) || 0;
            return sum + value;
        }, 0);
        const remaining = TOTAL_RENT - totalEntered;
        document.getElementById('remainingAmount').textContent = `Remaining to allocate: $${remaining.toFixed(2)}`;
        
        // Change color based on remaining amount
        const remainingElement = document.getElementById('remainingAmount');
        if (remaining < 0) {
            remainingElement.classList.remove('text-blue-600', 'text-green-600');
            remainingElement.classList.add('text-red-600');
        } else if (Math.abs(remaining) < 0.01) {
            remainingElement.classList.remove('text-blue-600', 'text-red-600');
            remainingElement.classList.add('text-green-600');
        } else {
            remainingElement.classList.remove('text-red-600', 'text-green-600');
            remainingElement.classList.add('text-blue-600');
        }
    }

    // Add input event listeners to all room inputs
    Object.values(roomInputs).forEach(room => {
        room.element.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value) || 0;
            if (value < 0) {
                e.target.value = 0;
            }
            room.value = e.target.value;
            updateRemainingAmount();
        });

        room.element.addEventListener('focus', (e) => {
            e.target.select();
        });
    });

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
            
            if (response.ok && (result.success || result.message)) {
                form.reset();
                // Reset room values
                Object.values(roomInputs).forEach(room => {
                    room.element.value = '';
                    room.value = '';
                });
                updateRemainingAmount();
                updateProgress();
            } else {
                alert(result.error || 'Error submitting valuations');
            }
        } catch (error) {
            console.error('Error submitting form:', error);
            alert('Error submitting valuations');
        }
    });

    // Update progress bar and check submissions
    async function updateProgress() {
        try {
            const response = await fetch('/api/submissions');
            const data = await response.json();
            
            const count = Array.isArray(data) ? data.length : 0;
            progressBar.style.width = `${(count / 3) * 100}%`;
            document.getElementById('submissionCount').textContent = `${count}/3`;
            
            if (count > 0) {
                currentSubmissions.classList.remove('hidden');
                submissionsList.innerHTML = data.map(sub => `
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

    // Calculate room assignments
    async function calculateAssignments() {
        try {
            const response = await fetch('/api/calculate');
            const data = await response.json();
            
            if (response.ok && data.success) {
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
    document.getElementById('resetButtonElement').addEventListener('click', async () => {
        try {
            const response = await fetch('/api/reset', { method: 'POST' });
            const data = await response.json();
            
            if (response.ok) {
                // Reset form
                form.reset();
                // Reset room values
                Object.values(roomInputs).forEach(room => {
                    room.element.value = '';
                    room.value = '';
                });
                // Update remaining amount
                updateRemainingAmount();
                // Hide results and reset button
                resultsSection.classList.add('hidden');
                resetButton.classList.add('hidden');
                // Update progress
                updateProgress();
            } else {
                alert(data.error || 'Error resetting submissions');
            }
        } catch (error) {
            console.error('Error resetting:', error);
            alert('Error resetting submissions');
        }
    });

    // Initialize values on page load
    updateRemainingAmount();
    updateProgress();
}); 