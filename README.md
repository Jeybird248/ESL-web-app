# ESL Learning Assistant

## Description

This Flask-based web application serves as an ESL (English as a Second Language) Learning Assistant. It provides various features to help users improve their English skills, including grammar correction, article reading comprehension, and interactive Q&A sessions.

## Features

- **Grammar Correction**: Analyzes user input for grammatical errors and provides corrections with explanations.
- **Article Reading**: Fetches random news articles and generates comprehension questions.
- **Multiple Choice Questions**: Creates multiple-choice questions based on article content.
- **Short Answer Questions**: Generates short answer questions and evaluates user responses.
- **Conversation Storage**: Saves user interactions for future reference.

## Technologies Used

- Flask
- CORS (Cross-Origin Resource Sharing)
- FuzzyWuzzy (for string matching)
- PyGoogleNews (for fetching news articles)
- Newspaper3k (for article parsing)
- NLTK (Natural Language Toolkit)
- Requests (for API calls)
- Mixtral API (for AI-powered text processing)

## Installation

1. Clone the repository:

>  git clone https://github.com/yourusername/esl-learning-assistant.git

2. Navigate to the project directory:

>  cd esl-learning-assistant

3. Install the required dependencies:

>  pip install -r requirements.txt


4. Set up environment variables:
- `MIXTRAL_URL`: URL for the Mixtral API
- `MIXTRAL_USERNAME`: Your Mixtral API username
- `MIXTRAL_PASSWORD`: Your Mixtral API password

## Usage

1. Run the Flask application:

>  python app.py


2. Open a web browser and navigate to `http://localhost:5000`

3. Use the different features of the application:
- Grammar correction
- Article reading and comprehension
- Q&A sessions

## API Endpoints

- `/`: Home page
- `/grammar`: Grammar correction page
- `/article`: Article reading page
- `/about`: About page
- `/fetch_article_text`: Fetches and processes a random news article
- `/submit`: Handles user input for grammar correction and Q&A

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- [Mixtral API](https://mixtral.com) for AI-powered text processing
- [PyGoogleNews](https://github.com/kotartemiy/pygooglenews) for news article fetching
- [Newspaper3k](https://newspaper.readthedocs.io/) for article parsing

## Contact

For any queries or suggestions, please open an issue on this repository.
