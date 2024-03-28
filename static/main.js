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
    userInput.value = "";

    // If the user input is not to start a new conversation, proceed with regular processing
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
            if(response.edited_text == "reset") {
                console.log("Resetting the conversation");
                appendChatMessage(textInput, 'user-message');
                appendChatMessage("Understood. Please give me the next set of text to analyze.", 'edited-text');
            }
            else {
                appendChatMessage(textInput, 'user-message');
                // Display edited text as chat bubbles
                // for (const editedText of responseData.edited_text) {
                //     appendChatMessage(editedText, 'edited-text');
                //     console.log('Received input:', editedText);
                // }
                appendChatMessage(responseData.edited_text, 'edited-text');
                console.log('Received the following correction:', responseData.edited_text);
                if(responseData.explanation) {
                    console.log('Received the following explanation:', responseData.explanation);
                    appendChatMessage(responseData.explanation, 'edited-text');
                }
            }
        } catch (error) {
            handleError(error);
        }
    }
});

const numberButtons = document.querySelectorAll('.number-button');

numberButtons.forEach(function (button) {
    button.addEventListener('click', async function () {
        const chatWindow = document.getElementById('chat-window');
        chatWindow.innerHTML = '';

        // Get the conversation number from the button text
        var conversationNumber = button.textContent;

        // Read the JSON file for the selected conversation number
        fetch(`/submit/${conversationNumber}`)
            .then(response => response.json())
            .then(data => {
                console.log(typeof data)
                data.forEach(function (entry) {
                    // Append user message with 'user-message' class
                    appendChatMessage(entry.user_input, 'user-message');
                    appendChatMessage(entry.edited_sentences, 'edited-text');
            })
            .catch(error => {
                console.error("Error reading conversation file:", error);
            });
        });
    });
}); 