// file: js/signup.js

// 1. Find the signup form on the page using its ID
const signupForm = document.getElementById('signup-form');

if (signupForm) {
    signupForm.addEventListener('submit', async function(event) {
        // 2. Prevent the page from reloading when the button is clicked
        event.preventDefault();

        // 3. Get the data from the form fields
        const fullName = document.getElementById('fullname').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const userType = document.getElementById('user-type').value;

        // 4. Structure the data into the JSON format our API expects
        const userData = {
            fullName: fullName,
            email: email,
            password: password,
            userType: userType
        };

        const apiUrl = 'http://127.0.0.1:8000/api/auth/register';

        try {
            // 5. Send the data to our backend registration endpoint
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData),
            });

            const data = await response.json();

            // 6. Handle the response from the server
            if (response.ok) {
                // If successful (Code 200)
                alert('Registration successful! Please log in.');
                window.location.href = 'login.html'; // Redirect to the login page
            } else {
                // If there's an error (e.g., email already registered)
                alert('Registration failed: ' + (data.detail || 'Unknown error'));
            }
        } catch (error) {
            // Handle network errors (e.g., if the server is down)
            console.error('Connection error:', error);
            alert('Could not connect to the server. Please make sure it is running.');
        }
    });
}