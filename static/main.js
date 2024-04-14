// Constants
const SERVER_URL = '/submit';

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
            // Show loading animation
            showLoadingAnimation();

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
            if(responseData.edited_text == "reset") {
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

            // Hide loading animation after processing is complete
            hideLoadingAnimation();
        } catch (error) {
            handleError(error);
            // Hide loading animation if there's an error
            hideLoadingAnimation();
        }
    }
});

function showLoadingAnimation() {
    // Show the loading screen or animation here
    const loadingScreen = document.querySelector('.loading-screen');
    loadingScreen.style.display = 'flex'; // Display the loading screen
}

function hideLoadingAnimation() {
    // Hide the loading screen or animation here
    const loadingScreen = document.querySelector('.loading-screen');
    loadingScreen.style.display = 'none'; // Hide the loading screen
}


const numberButtons = document.querySelectorAll('.number-button');
const addConversationButton = document.getElementById('addConversation');

// Event listener for adding a new conversation
addConversationButton.addEventListener('click', function () {
    // Perform actions to add a new conversation
    // For example, you can append a new button with appropriate functionality
    const numberButtons = document.querySelectorAll('.number-button');
    const conversationCount = numberButtons.length + 1;
    const newButton = document.createElement('button');
    newButton.textContent = conversationCount;
    newButton.classList.add('number-button');

    // Append the new button after the last existing button
    const buttonColumn = document.querySelector('.button-column');
    const lastButton = buttonColumn.lastElementChild;
    lastButton.insertAdjacentElement('beforebegin', newButton);

    // Attach event listener to the new button
    newButton.addEventListener('click', loadConversation);
    newButton.click();
});


// Event listener for conversation buttons
numberButtons.forEach(function (button) {
    button.addEventListener('click', loadConversation);
    button.classList.remove('selected');
});

// Function to load conversation from JSON file
function loadConversation() {
    showLoadingAnimation();
    const chatWindow = document.getElementById('chat-window');
    chatWindow.innerHTML = '';

    // Get the conversation number from the button text
    const conversationNumber = this.textContent;

    // Read the JSON file for the selected conversation number
    fetch(`/submit/${conversationNumber}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Fetch error: ${response.status} - ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            data.forEach((message, index) => {
                // Alternate between user message and edited text based on index
                console.log(message);
                if (index % 2 === 0) {
                    appendChatMessage(message, 'user-message');
                } else {
                    appendChatMessage(message, 'edited-text');
                }
            });
            hideLoadingAnimation();
        })
        .catch(error => {
            console.error("Error reading conversation file:", error);
            hideLoadingAnimation();
        });

    // Iterate through number buttons and add click event listeners
    const numberButtons = document.querySelectorAll('.number-button');
    numberButtons.forEach(button => {
        button.classList.remove('selected');            
    });
    this.classList.add('selected');
}


window.addEventListener('load', function () {
    // Hide the loading screen when the content is fully loaded
    var loadingScreen = document.querySelector('.loading-screen');
    loadingScreen.style.display = 'none';

    // Fetch conversation count from the server
    fetch('/conversation/count')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to fetch conversation count: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            const conversationCount = data.conversation_count;

            // Add buttons based on conversationCount
            for (let i = 2; i <= conversationCount; i++) {
                const newButton = document.createElement('button');
                newButton.textContent = i;
                newButton.classList.add('number-button');

                // Attach event listener to the new button
                newButton.addEventListener('click', loadConversation);

                const buttonColumn = document.querySelector('.button-column');
                const lastButton = buttonColumn.lastElementChild;
                lastButton.insertAdjacentElement('beforebegin', newButton);
            }

            // Trigger click event on the first button if it exists
            const numberButtons = document.querySelectorAll('.number-button');
            if (numberButtons.length > 0) {
                numberButtons[0].click();
            }
        })
        .catch(error => {
            console.error("Error fetching conversation count:", error);
        });
});

