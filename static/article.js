let correctAnswers = [];

// Function to handle errors
function handleError(error) {
    console.error('An error occurred:', error);
    // You can add further error handling logic here, such as displaying an error message to the user
}

// Function to create HTML elements for questions and answer choices
function createQuestionElements(question, answerChoices, questionIndex) {
    const questionDiv = document.createElement('div');
    questionDiv.classList.add('question');

    const questionText = document.createElement('p');
    questionText.textContent = question;
    questionDiv.appendChild(questionText);

    const answerChoicesDiv = document.createElement('div');
    answerChoicesDiv.classList.add('answer-choices');

    answerChoices.forEach((choice, index) => {
        const choiceLabel = document.createElement('label');
        choiceLabel.textContent = choice;
        choiceLabel.setAttribute('for', `choice-${questionIndex}-${index}`);

        const choiceInput = document.createElement('input');
        choiceInput.type = 'radio';
        choiceInput.name = `answer-${questionIndex}`;
        choiceInput.id = `choice-${questionIndex}-${index}`;

        answerChoicesDiv.appendChild(choiceInput);
        answerChoicesDiv.appendChild(choiceLabel);
    });

    questionDiv.appendChild(answerChoicesDiv);

    return questionDiv;
}

// Function to fetch and display article text, questions, and answers
async function fetchAndDisplayArticleText() {
    try {
        console.log('Fetching article text and questions...');

        // Send a request to Flask server to fetch the article text, questions, and answers
        const response = await fetch('/fetch_article_text', {
            method: 'POST',
        });

        if (!response.ok) {
            throw new Error(`Fetch error: ${response.status} - ${response.statusText}`);
        }

        const responseData = await response.json();
        const articleText = responseData.articleText;
        const questions = responseData.questions;
        const answerChoices = responseData.answerChoices;
        correctAnswers = responseData.correctAnswers;

        console.log('Article text fetched:', articleText);
        console.log('Questions fetched:', questions);
        console.log('Answer choices fetched:', answerChoices);
        console.log('Correct answer fetched:', correctAnswers);

        // Display the fetched article text on the HTML page
        const articleTextElement = document.getElementById('article-text');
        articleTextElement.textContent = articleText;

        console.log('Article text displayed on page:', articleText);

        // Create HTML elements for each question and answer choices and append them to the HTML page
        const questionsContainer = document.getElementById('multiple-choice-questions');
        questions.forEach((question, index) => {
            const questionElement = createQuestionElements(question, answerChoices[index], index);
            questionsContainer.appendChild(questionElement);
        });

        console.log('Questions displayed on page');

    } catch (error) {
        handleError(error);
    }
}

// Call the function to fetch and display article text, questions, and answers when the page loads
document.addEventListener('DOMContentLoaded', fetchAndDisplayArticleText);

// Submit answers when the form is submitted
document.getElementById('questions-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    try {
        console.log('Submitting answers...');

        // Get the selected answers
        const selectedAnswers = [];
        const questions = document.querySelectorAll('.question');
        questions.forEach((question, index) => {
            const selectedInput = question.querySelector(`input[name="answer-${index}"]:checked`);
            if (selectedInput) {
                selectedAnswers.push(selectedInput.nextElementSibling.textContent);
            }
        });

        console.log('Selected answers:', selectedAnswers);

        console.log('Correct answers:', correctAnswers);

        // Compare selected answers with correct answers and style them accordingly
        questions.forEach((question, index) => {
            const selectedInput = question.querySelector(`input[name="answer-${index}"]:checked`);
            if (selectedInput) {
                const selectedAnswer = selectedInput.nextElementSibling.textContent;
                const correctAnswer = correctAnswers[index];
                if (selectedAnswer === correctAnswer) {
                    selectedInput.nextElementSibling.style.color = 'green';
                    selectedInput.nextElementSibling.style.fontWeight = 'bold';
                }
            }
        });

        console.log('Answers submitted and styled.');

    } catch (error) {
        handleError(error);
    }
});
