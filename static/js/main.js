document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('valuationForm');
    const submissionsList = document.getElementById('submissionsList');
    const progressBar = document.getElementById('progressBar');
    const resultsSection = document.getElementById('results');
    const resetButton = document.getElementById('resetButton');
    const currentSubmissions = document.getElementById('currentSubmissions');

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
            valuations: {
                'Room A': parseFloat(formData.get('roomA')),
                'Room B': parseFloat(formData.get('roomB')),
                'Room C': parseFloat(formData.get('roomC'))
            }
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