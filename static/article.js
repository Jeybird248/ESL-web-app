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
        choiceInput.setAttribute('required', true);

        const choiceContainer = document.createElement('div');
        choiceContainer.classList.add('answer-choice-container');
        choiceContainer.appendChild(choiceInput);
        choiceContainer.appendChild(choiceLabel);

        answerChoicesDiv.appendChild(choiceContainer);
    });

    questionDiv.appendChild(answerChoicesDiv);

    return questionDiv;
}
function createShortAnswerQuestionElement(question, questionIndex) {
    const questionDiv = document.createElement('div');
    questionDiv.classList.add('SA-question');

    const questionText = document.createElement('p');
    questionText.textContent = question;
    questionDiv.appendChild(questionText);

    const answerInput = document.createElement('textarea');
    answerInput.name = `short-answer-${questionIndex}`;
    answerInput.id = `short-answer-${questionIndex}`;
    answerInput.placeholder = 'Your answer...';    

    questionDiv.appendChild(answerInput);

    return questionDiv;
}

// Function to fetch and display article text, questions, and answers
async function fetchAndDisplayArticleText() {
    showLoadingAnimation();
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
        console.log(responseData);
        const articleText = responseData.articleText;
        const questions = responseData.questions;
        const shortAnswers = responseData.shortAnswer;
        const answerChoices = responseData.answerChoices;
        correctAnswers = responseData.correctAnswers;

        console.log('Article text fetched:', articleText);
        console.log('Questions fetched:', questions);
        console.log('Answer choices fetched:', answerChoices);
        console.log('Correct answer fetched:', correctAnswers);

        // Display the fetched article text on the HTML page
        const articleTextElement = document.getElementById('article-text');

        // Create a <pre> element
        const preElement = document.createElement('pre');

        // Set the text content of the <pre> element to the fetched article text
        preElement.textContent = articleText;
        preElement.style.whiteSpace = 'pre-wrap';

        // Append the <pre> element to the articleTextElement
        articleTextElement.appendChild(preElement);
        console.log('Article text displayed on page:', articleText);

        // Create HTML elements for each question and answer choices and append them to the HTML page
        const questionsContainer = document.getElementById('multiple-choice-questions');
        questions.forEach((question, index) => {
            const questionElement = createQuestionElements(question, answerChoices[index], index);
            questionsContainer.appendChild(questionElement);
            console.log("question added mc")
        });
        shortAnswers.forEach((question, index) => {
            const shortAnswerQuestionElement = createShortAnswerQuestionElement(question, index);
            questionsContainer.appendChild(shortAnswerQuestionElement);
            console.log("question added frq")
        });
        const submitButton = document.createElement('button');
        submitButton.type = 'submit';
        submitButton.textContent = 'Submit Answers';
        submitButton.addEventListener('click', () => {
            console.log('New button clicked');
        });
        questionsContainer.appendChild(submitButton);
        
        const newButton = document.createElement('button');
        newButton.type = 'button';
        newButton.textContent = 'Restart';
        newButton.addEventListener('click', () => {
            const response = fetch('/fetch_article_text/reset', {
                method: 'POST',
            });
    
            if (!response.ok) {
                throw new Error(`Fetch error: ${response.status} - ${response.statusText}`);
            }
        });
        questionsContainer.appendChild(newButton);

        console.log('Questions displayed on page');
        hideLoadingAnimation();

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
        const incorrectAnswersInfo = [];
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
                incorrectAnswersInfo.push({
                    question: question.querySelector('p').textContent,
                    correctAnswer: correctAnswer
                });
            }
        });

        const shortAnswers = [];
        const SAquestions = document.querySelectorAll('.SA-question');
        // Compare selected answers with correct answers and style them accordingly
        SAquestions.forEach((question, index) => {
            const selectedInput = question.querySelector(`textarea[name="short-answer-${index}"]`);
            if (selectedInput) {
                const userAnswer = selectedInput.value;
                shortAnswers.push({
                    SAquestion: question.querySelector('p').textContent,
                    userAnswer: userAnswer
                });
            }
        });

        const response = await fetch('/fetch_article_text/incorrect_answers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                questions: incorrectAnswersInfo.map(({ question }) => question),
                correctAnswers: incorrectAnswersInfo.map(({ correctAnswer }) => correctAnswer),
                SAquestion: shortAnswers.map(({ SAquestion }) => SAquestion),
                userAnswer: shortAnswers.map(({ userAnswer }) => userAnswer)
            })
        })
        if (!response.ok) {
            throw new Error(`Fetch error: ${response.status} - ${response.statusText}`);
        }

        const responseData = await response.json();
        const answerExplanations = responseData.answer_explanations;
        // Find existing question elements and append answer text under each radio button
        const questionDivs = document.querySelectorAll('.question');
        questionDivs.forEach((questionDiv, questionIndex) => {
            const answerChoicesDiv = questionDiv.querySelector('.answer-choices');
            const choiceContainers = answerChoicesDiv.querySelectorAll('.answer-choice-container');

            // Find the last radio button container
            const lastChoiceContainer = choiceContainers[choiceContainers.length - 1];

            // Append answer explanation after the last radio button container
            const answerExplanation = document.createElement('p');
            answerExplanation.textContent = answerExplanations[questionIndex];
            console.log(answerExplanations[questionIndex]);
            lastChoiceContainer.parentNode.insertBefore(answerExplanation, lastChoiceContainer.nextSibling);
        });

        const SAanswerExplanations = responseData.SA_answer_explanations;
        // Find existing question elements and append answer text under each radio button
        const SAquestionDivs = document.querySelectorAll('.SA-question');
        SAquestionDivs.forEach((questionDiv, questionIndex) => {
            const selectedInput = questionDiv.querySelector(`textarea[name="short-answer-${questionIndex}"]`);

            const answerExplanation = document.createElement('p');
            answerExplanation.textContent = SAanswerExplanations[questionIndex];
            console.log(SAanswerExplanations[questionIndex]);
            selectedInput.parentNode.insertBefore(answerExplanation, selectedInput.nextSibling);
        });


        console.log('Answers submitted and styled.');

    } catch (error) {
        handleError(error);
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