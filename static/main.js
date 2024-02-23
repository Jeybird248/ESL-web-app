// Constants
const SERVER_URL = 'http://localhost:5000/submit';

// Function to handle errors
const handleError = error => {
    console.error('Error:', error);
    alert('Error: ' + error.message);
};

// Function to append chat messages to the chat window
const appendChatMessage = (message, className) => {
    const chatWindow = document.getElementById('chat-window');
    chatWindow.innerHTML += `<div class="chat-message ${className}">${message}</div>`;
    chatWindow.scrollTop = chatWindow.scrollHeight; // Scroll to the bottom of the chat window
};

const submitButton = document.getElementById('submit');

// Event listener for submit button
submitButton.addEventListener('click', async function () {
    const textInput = userInput.value.trim();

    if (textInput) {
        try {
            console.log('Sending user input to server:', textInput);

            // Send input text to Flask server for processing
            const response = await fetch(SERVER_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ userInput: textInput }),
            });

            if (!response.ok) {
                throw new Error(`Fetch error: ${response.status} - ${response.statusText}`);
            }

            const responseData = await response.json();

            if (!Array.isArray(responseData.edited_text)) {
                throw new TypeError('Invalid server response format');
            }
            
            appendChatMessage(textInput, 'user-message');
            // Display edited text as chat bubbles
            for (const editedText of responseData.edited_text) {
                appendChatMessage(editedText, 'edited-text');
                console.log('Received input:', editedText);
            }

        } catch (error) {
            handleError(error);
        }
    }
});

