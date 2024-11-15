document.getElementById('signupForm').addEventListener('submit', async function(event) {
    event.preventDefault(); // Prevents the form from redirecting
    await submitSignupForm();
});
    
async function submitSignupForm() {
// Get values from the form fields
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirm_password = document.getElementById('confirm_password').value;
    const user_type = document.getElementById('user_type').value;

    // Create the data object to send in the request
    const data = {
        username,
        email,
        password,
        confirm_password,
        user_type
    };

    try {
        // Send the data to the API using fetch
        const response = await fetch('http://127.0.0.1:8000/api/signup/', { // Replace with your actual API endpoint
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        // Check if the signup was successful
        if (response.ok) {
            document.getElementById('message').innerText = result.message;
            
            // Redirect to login page after a short delay
            setTimeout(() => {
                window.location.href = '/login/'; // Replace '/login/' with the actual URL of your login page
            }, 2000); // Redirects after 2 seconds (2000 ms) to allow user to see success message

        } else {
            // Display any validation errors returned by the API
            document.getElementById('message').innerText = `Error: ${JSON.stringify(result)}`;
        }
    } catch (error) {
        document.getElementById('message').innerText = 'An error occurred. Please try again later.';
        console.error('Error:', error);
    }
};
