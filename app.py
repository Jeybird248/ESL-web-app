# Import necessary modules
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from fuzzywuzzy import fuzz
from pygooglenews import GoogleNews
from newspaper import Article
import nltk
import logging
import requests
import base64
import json
import os
import re
import random

# Initialize Flask app
MIXTRAL_URL = ''
MIXTRAL_USERNAME = ''
MIXTRAL_PASSWORD = ''

# Download NLTK data
nltk.download('punkt')
# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO)
# Initialize Google News API
gn = GoogleNews(lang='en', country='US')
# Initialize Flask app
app = Flask(__name__)
# Enable CORS
CORS(app)

# Global variables for storing data
stored_variable = None
current_conversation = 1
article_text = None
questions = None
answer_choices = None
short_answers = None
correct_answers = None

# JSON templates for questions, answer explanations, and short answers
template_json = {
    "questions": [
        "Question 1",
        "Question 2",
        "Question 3",
        "Question 4",
        "Question 5"
    ],
    "short_answer_questions": [
        "Question 1",
        "Question 2",
        "Question 3"
    ],
    "answer_choices": [
        ["Choice 1", "Choice 2", "Choice 3", "Choice 4"],
        ["Choice 1", "Choice 2", "Choice 3", "Choice 4"],
        ["Choice 1", "Choice 2", "Choice 3", "Choice 4"],
        ["Choice 1", "Choice 2", "Choice 3", "Choice 4"],
        ["Choice 1", "Choice 2", "Choice 3", "Choice 4"]
    ],
    "correct_answers": [
        "Correct Answer 1",
        "Correct Answer 2",
        "Correct Answer 3",
        "Correct Answer 4",
        "Correct Answer 5"
    ]
}
template_json_str = json.dumps(template_json)
answer_template_json = {
    "questions": [
        "Question 1",
        "Question 2",
        "Question 3",
        "Question 4",
        "Question 5"
    ],
    "answer_explanations": [
        "Explanation for Answer 1",
        "Explanation for  Answer 2",
        "Explanation for  Answer 3",
        "Explanation for  Answer 4",
        "Explanation for  Answer 5"
    ]
}
answer_template_json_str = json.dumps(answer_template_json)
short_answer_template_json = {
    "questions": [
        "Question 1",
        "Question 2",
        "Question 3"
    ],
    "answer_explanations": [
        "Explanation for Answer 1",
        "Explanation for  Answer 2",
        "Explanation for  Answer 3"
    ]
}
short_answer_template_json_str = json.dumps(short_answer_template_json)

# Route for home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for grammar page
@app.route('/grammar')
def grammar():
    return render_template('grammar.html')

# Route for article page
@app.route('/article')
def article():
    return render_template('article.html')

# Route for about page
@app.route('/about')
def about():
    return render_template('about.html')

# Route for fetching article text
@app.route('/fetch_article_text/<path:url>', methods=['POST'])
@app.route('/fetch_article_text', methods=['POST'])
def fetch_article_text(url = False):
    global article_text
    global questions
    global answer_choices 
    global short_answers 
    global correct_answers 

    # Reset article data if requested
    reset = url == 'reset'
    if not reset and (article_text and questions and answer_choices):
        print("Loading in existing article...")
        print(article_text[:50])
        print(answer_choices)
        return jsonify({
            'articleText': article_text,
            'questions': questions,
            'shortAnswer': short_answers,
            'answerChoices': answer_choices,
            'correctAnswers': correct_answers
        })
    for _ in range(5):
        try:
            # Fetch top news articles from Google News
            s = gn.top_news()
            # Choose a random article
            url = s['entries'][random.randint(0, len(s['entries']))].link
            # Download and parse the article
            article = Article(url, language='en')
            article.download()
            article.parse()
            article_text = article.text
            print("Gathered the article text.")
            # Make a request to MIXTRAL API to generate questions
            response = requests.post(
                MIXTRAL_URL,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Basic {base64.b64encode(f"{MIXTRAL_USERNAME}:{MIXTRAL_PASSWORD}".encode()).decode()}'
                },
                json={
                    'prompt' : '<s>[INST]Q&A Generation Task: You will receive: 1. A paragraph of English text. The model is expected to output only a JSON file and nothing else in the following format: {} Make sure the property names are wrapped in double quotations. 1. Generate 5 multiple choice questions and 3 short answer questions from the text; 2. Generate 4 answer options for each multiple choice question, with one and only one correct answer; 3. The correct answer choice for each multiplce choice question; Format the output as a JSON file where the questions, answer choices, and the correct answers are stored in their respective arrays with the keys multiple choice questions, short answer questions, answer_choices, and correct answers, respectively. Encapsulate the json property names with double quotes. This is the article you need to generate questions from: {}</s>'.format(template_json, article_text),
                    'n_predict': 1000,
                    'temp':0.8
                }
            )

            # Handle MIXTRAL response
            if response.status_code != 200:
                raise Exception(f'MIXTRAL API request failed with status code {response.status_code}')
            
            # Parse MIXTRAL response
            mixtral_data = response.json()
            mixtral_data = mixtral_data.get('content', "")
            print("Request successfully received, the contents are: \n", mixtral_data)
            # Clean MIXTRAL response
            json_start_index = mixtral_data.find('{')
            json_end_index = mixtral_data.find('}')
            mixtral_data = mixtral_data[json_start_index:json_end_index + 1]

            mixtral_data = re.sub("'", '"', mixtral_data)
            mixtral_data = re.sub(r"\\", "", mixtral_data)
            mixtral_data = re.sub(r'\"\"', '', mixtral_data)
            mixtral_data = re.sub(r'\n', '', mixtral_data)
            mixtral_data = re.sub(r'\s+', ' ', mixtral_data)
            
            invalid_char_pattern = r"[^a-zA-Z0-9\s,{}[]:.\-\'\"!@#$%^&*()]"
            mixtral_data = re.sub(invalid_char_pattern, "", mixtral_data)

            remove_pattern = r'([a-zA-Z])"([^\],:])' 
            remove_pattern2 = r'([a-zA-Z])"([a-zA-Z])' # remove contractions i.e. I can't
            remove_pattern3 = r'(?<!, |\{\s|\[\s)(?<!\{|\[|\n)(?<!", )"([^",.:\]| ]])'
            remove_pattern4 = r'(?<!", |\], )(?<!\{|\[)"([a-zA-Z])' 

            mixtral_data = re.sub(remove_pattern, r'\1\2', mixtral_data)
            mixtral_data = re.sub(remove_pattern2, r"\1\2", mixtral_data)
            mixtral_data = re.sub(remove_pattern3, r"\1", mixtral_data)
            mixtral_data = re.sub(remove_pattern4, r"\1", mixtral_data)
            
            # Parse cleaned MIXTRAL response
            mixtral_json = json.loads(mixtral_data)

            # Extract questions, answer choices, and correct answers from MIXTRAL response
            questions = mixtral_json.get('questions', [])
            short_answers = mixtral_json.get('short_answer_questions', [])
            answer_choices = mixtral_json.get('answer_choices', [])
            correct_answers = mixtral_json.get('correct_answers', [])

            # Return article data
            return jsonify({
                'articleText': article_text,
                'questions': questions,
                'shortAnswer': short_answers,
                'answerChoices': answer_choices,
                'correctAnswers': correct_answers
            })
        except Exception as e:
            # Log error and retry
            print(f'Error fetching article: {e}')
            continue
    # Return error if article fetching fails
    return jsonify({'error': 'Failed to fetch article'})
# Route for fetching article text along with incorrect answers
@app.route('/fetch_article_text/incorrect_answers', methods=["POST"])
def query_incorrect():
    print("Attempting to grab explanations...")
    # Global variables for storing article data and questions
    global article_text
    global questions
    global answer_choices 
    global short_answers 
    global correct_answers 

    # Attempt to fetch article and questions five times
    for _ in range(5):
        try:
            # Send request for multiple choice questions
            response = requests.post(
                MIXTRAL_URL,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Basic {base64.b64encode(f"{MIXTRAL_USERNAME}:{MIXTRAL_PASSWORD}".encode()).decode()}'
                },
                json={
                    'prompt' : '<s>[INST]Q&A Explanation Task: You will receive: 1. A paragraph of English text. 2. A set of questions. 3. A set of correct answers. The model is expected to output only a JSON file and nothing else in the following format: {} Make sure the property names are wrapped in double quotations. 1. Generate explanations for why each answer to the multiple choice questions is correct; Format the output as a JSON file where the explanations are stored in their respective arrays with the keys respectively. This is the article you need to generate explanations from: {}. These are the questions about the text: {}, and these are the answers to those questions: {}</s>'.format(answer_template_json, article_text, questions, correct_answers),
                    'n_predict': 600,
                }
            )
            # Raise exception if request fails
            if response.status_code != 200:
                raise Exception(f'MIXTRAL API request failed with status code {response.status_code}')
            
            # Parse MIXTRAL response
            mixtral_data = response.json()['content']
            print("Request successfully received for MC, the contents are: \n", mixtral_data)
            # Clean MIXTRAL response
            json_start_index = mixtral_data.find('{')
            json_end_index = mixtral_data.find('}')
            mixtral_data = mixtral_data[json_start_index:json_end_index + 1]

            mixtral_data = re.sub("'", '"', mixtral_data)
            mixtral_data = re.sub(r"\\", "", mixtral_data)
            mixtral_data = re.sub(r'\"\"', '', mixtral_data)
            mixtral_data = re.sub(r'\n', '', mixtral_data)
            mixtral_data = re.sub(r'\s+', ' ', mixtral_data)
            
            invalid_char_pattern = r"[^a-zA-Z0-9\s,{}[]:.\-\'\"!@#$%^&*()]"
            mixtral_data = re.sub(invalid_char_pattern, "", mixtral_data)

            remove_pattern = r'([a-zA-Z])"([^\],:])' 
            remove_pattern2 = r'([a-zA-Z])"([a-zA-Z])' # remove contractions i.e. I can't
            remove_pattern3 = r'(?<!, |\{\s|\[\s)(?<!\{|\[|\n)(?<!", )"([^",.:\]| ]])'
            remove_pattern4 = r'(?<!", |\], )(?<!\{|\[)"([a-zA-Z])' 

            mixtral_data = re.sub(remove_pattern, r'\1\2', mixtral_data)
            mixtral_data = re.sub(remove_pattern2, r"\1\2", mixtral_data)
            mixtral_data = re.sub(remove_pattern3, r"\1", mixtral_data)
            mixtral_data = re.sub(remove_pattern4, r"\1", mixtral_data)
            print("Cleaning successfully done for MC: \n", mixtral_data)
            # Parse cleaned MIXTRAL response
            mixtral_data = json.loads((mixtral_data)).get('answer_explanations', [])
            break
        except Exception as e:
            # Retry if an error occurs
            print(f"An error occurred when grabbing explanations for the questions for MC: {e}. Trying again...")
    for _ in range(5):
        try:
            # Get user short answers
            data = request.json
            user_short_answers = data.get('userAnswer', [])
            print("Attempting to grab short answer explanations\n")
            # Send request for short answer explanations
            short_answer_response = requests.post(
                MIXTRAL_URL,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Basic {base64.b64encode(f"{MIXTRAL_USERNAME}:{MIXTRAL_PASSWORD}".encode()).decode()}'
                },
                json={
                    'prompt' : '<s>[INST]Q&A Explanation Task: You will receive: 1. A paragraph of English text. 2. A set of short answer questions. 3. Answers for the short answer questions that may be incorrect. The model is expected to output only a JSON file and nothing else in the following format: {} Make sure the property names are wrapped in double quotations. 1. Generate explanations for each short answer question. State if the user was correct. If not, give an explanation as to why.; Format the output as a JSON file where the explanations are stored in their respective arrays with the keys respectively. This is the article you need to generate explanations from: {}. These are the short answer questions about the text: {}, and these are the user answers to those questions that you need to correct: {}</s>'.format(short_answer_template_json, article_text, short_answers, user_short_answers),
                    'n_predict': 600,
                }
            )
            # Raise exception if request fails
            if short_answer_response.status_code != 200:
                raise Exception(f'MIXTRAL API request failed with status code {short_answer_response.status_code}')
            
            # Parse short answer MIXTRAL response
            SA_mixtral_data = short_answer_response.json()['content']
            print("Request successfully received for SA, the contents are: \n", SA_mixtral_data)
            json_start_index = SA_mixtral_data.find('{')
            json_end_index = SA_mixtral_data.find('}')
            SA_mixtral_data = SA_mixtral_data[json_start_index:json_end_index + 1]

            SA_mixtral_data = re.sub("'", '"', SA_mixtral_data)
            SA_mixtral_data = re.sub(r"\\", "", SA_mixtral_data)
            SA_mixtral_data = re.sub(r'\"\"', '', SA_mixtral_data)
            SA_mixtral_data = re.sub(r'\n', '', SA_mixtral_data)
            SA_mixtral_data = re.sub(r'\s+', ' ', SA_mixtral_data)
            
            invalid_char_pattern = r"[^a-zA-Z0-9\s,{}[]:.\-\'\"!@#$%^&*()]"
            SA_mixtral_data = re.sub(invalid_char_pattern, "", SA_mixtral_data)

            remove_pattern = r'([a-zA-Z])"([^\],:])' 
            remove_pattern2 = r'([a-zA-Z])"([a-zA-Z])' # remove contractions i.e. I can't
            remove_pattern3 = r'(?<!, |\{\s|\[\s)(?<!\{|\[|\n)(?<!", )"([^",.:\]| ]])'
            remove_pattern4 = r'(?<!", |\], )(?<!\{|\[)"([a-zA-Z])' 

            SA_mixtral_data = re.sub(remove_pattern, r'\1\2', SA_mixtral_data)
            SA_mixtral_data = re.sub(remove_pattern2, r"\1\2", SA_mixtral_data)
            SA_mixtral_data = re.sub(remove_pattern3, r"\1", SA_mixtral_data)
            SA_mixtral_data = re.sub(remove_pattern4, r"\1", SA_mixtral_data)
            print("Cleaning successfully done for SA: \n", SA_mixtral_data)

            # Parse short answer MIXTRAL response
            SA_mixtral_data = json.loads((SA_mixtral_data)).get('answer_explanations', [])
            # Return explanations for multiple choice and short answer questions
            return jsonify({
                'answer_explanations': mixtral_data,
                'SA_answer_explanations': SA_mixtral_data
            })
        except Exception as e:
            # Retry if an error occurs
            print(f"An error occurred when grabbing explanations for the questions for SA: {e}. Trying again...")

# Route for getting conversation count
@app.route('/conversation/count', methods=['GET'])
def get_conversation_count():
    # File path for storing conversations
    file_path = 'conversations/conversations.json'
    # Check if conversations file exists
    if os.path.exists(file_path):
        # Load conversations and return count
        with open(file_path, 'r') as file:
            data = json.load(file)
            return jsonify({"conversation_count": len(data)})

# Route for submitting conversation
@app.route('/submit/<int:conversation_number>', methods=['GET','POST'])
@app.route('/submit', methods=['POST'])
def submit(conversation_number = None):
    # Global variables for stored conversation and current conversation
    global stored_variable
    global current_conversation

    # List to store edited sentences
    edited_sentences = []

    # Check if a specific conversation is requested
    if conversation_number:
        # Load conversation and return stored conversation
        current_conversation = conversation_number
        response = load_conversation(current_conversation)
        conversation = response.get("messages")[-1]["stored_conversation"] if response.get("messages") else []
        return jsonify(conversation)

    try:
        # Get user input from request
        data = request.get_json()
        user_input = data.get('userInput', '')

        # Check if there are stored conversations
        if not stored_variable:
            # Split user input into sentences
            sentences = nltk.sent_tokenize(user_input)

            # Process sentences in batches of up to 3
            batch_size = 3
            for i in range(0, len(sentences), batch_size):
                batch = sentences[i:i + batch_size]
                try:
                    # Make API call to Mixtral for ESL correction task
                    response = requests.post(
                        MIXTRAL_URL,
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': f'Basic {base64.b64encode(f"{MIXTRAL_USERNAME}:{MIXTRAL_PASSWORD}".encode()).decode()}'
                        },
                        json={
                            'prompt': '<s>[INST]ESL Correction Task: You will receive: 1. A paragraph of English text, potentially containing grammar or spelling mistakes. The model is expected to output: 1. A corrected version of the paragraph, starting with the format Correction:. 2. An accompanying explanation for each correction, explained in simple terms, assuming the user has limited knowledge of English grammar. The explanations should use examples to clarify concepts. This section will start with the format Explanation:. Use <br> to create new lines after each sentence. These are the sentences you need to fix: {}[/INST]</s>'.format('<br>'.join(batch)),
                            'n_predict': 600,
                        }
                    )

                    response.raise_for_status()

                    mixtral_output = response.json()
                    # Process Mixtral response and store information
                    process_mixtral_response(user_input, mixtral_output['content'])
                    edited_sentences.append(mixtral_output['content'])
                except requests.exceptions.RequestException as api_error:
                    logging.error(f"Mixtral API error: {api_error}")
                    edited_sentences.append([f"Error processing: {s}." for s in batch])

            # Save conversation to local storage
            save_conversation(user_input, edited_sentences, current_conversation)
            # Return suggestions and edited text as JSON
            response_data = {
                'edited_text': edited_sentences,
            }

            return jsonify(response_data)
        else:
            try:
                # Make API call to Mixtral for ESL Q&A task
                response = requests.post(
                    MIXTRAL_URL,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Basic {base64.b64encode(f"{MIXTRAL_USERNAME}:{MIXTRAL_PASSWORD}".encode()).decode()}'
                    },
                    json={
                        'prompt': '<s>[INST]ESL Q&A Task: You will receive: \n1. A paragraph of English text, potentially containing grammar or spelling mistakes. \n2. A corrected version of the English text. \n3. A question about the correction. \nThe model is expected to output: \n1. An answer to the question using the corrected text and the original text, along with new examples that can better explain what the user is asking about. Make sure the examples and explanations are in layman terms and easy to understand for someone who does not know anything about English grammar. \nUse <br> to create new lines after each sentence. Here is the original sentence: {0}, here is the corrected text: {1}, and the question: {2}.[/INST]</s>'.format(stored_variable[1], stored_variable[0], user_input),
                        'n_predict': 600,
                    }
                )
                response.raise_for_status()

                mixtral_output = response.json()
                # Append Mixtral response to edited sentences
                edited_sentences.append(mixtral_output['content'])
            except requests.exceptions.RequestException as api_error:
                logging.error(f"Mixtral API error: {api_error}")
                edited_sentences.append([f"Error processing: {s}." for s in batch])
            # Save conversation to local storage
            save_conversation(user_input, edited_sentences, current_conversation)
            # Return suggestions and edited text as JSON
            response_data = {
                'edited_text': edited_sentences
            }

            return jsonify(response_data)

    except Exception as e:
        logging.error(f"Error processing user input: {e}")
        return jsonify({'error': 'An error occurred.'}), 500

# Function to process Mixtral response
def process_mixtral_response(user_input, mixtral_response):
    # Global variable for storing conversation
    global stored_variable
    try:
        # Tokenize sentences in Mixtral response
        sentences = nltk.sent_tokenize(mixtral_response)
        max_similarity = 0
        closest_sentence = ""

        # Find most similar sentence to user input
        for sentence in sentences:
            similarity = fuzz.token_set_ratio(user_input, sentence)
            if similarity > max_similarity and user_input != sentence:
                max_similarity = similarity
                closest_sentence = sentence

        # Extract explanation from Mixtral response
        explanation = mixtral_response.replace(closest_sentence, '').replace('Explanation:', '').strip()
        
        # Store closest sentence, user input, and explanation
        stored_variable = (closest_sentence.strip(), user_input.strip(), 'Explanation: ' + explanation.strip())
    except Exception as e:
        logging.error(f"Error processing Mixtral response: {e}")

# Function to save conversation to local storage
def save_conversation(user_input, edited_sentences, conversation_number):
    # Global variable for stored conversation
    global stored_variable
    try:
        # Convert edited sentences to string
        edited_sentences = '\n'.join(edited_sentences)
        file_path = 'conversations/conversations.json'
        conversation_data = {'user_input': user_input, 'edited_sentences': edited_sentences, 'stored_conversation': []}

        # Load existing conversations or create new array if file doesn't exist
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                existing_conversations = json.load(file)
        else:
            existing_conversations = []
        # Find conversation with specified number or create new one if not found
        conversation = next((conv for conv in existing_conversations if conv.get('conversation_number') == conversation_number), None)
        if conversation is None:
            conversation = {'conversation_number': conversation_number, 'messages': []}

        # Append new message to conversation
        stored_conversation = conversation.get("messages")[-1]["stored_conversation"] if conversation.get("messages") else []
        stored_conversation.append(user_input)
        stored_conversation.append(edited_sentences)
        conversation['messages'].append({'user_input': user_input, 'edited_sentences': edited_sentences, 'stored_conversation': stored_conversation})
        
        # Append updated conversation to list of conversations
        if conversation_number in [conv.get('conversation_number') for conv in existing_conversations]:
            existing_conversations = [conv for conv in existing_conversations if conv.get('conversation_number') != conversation_number]
        existing_conversations.append(conversation)

        # Save updated conversations to file
        with open(file_path, 'w') as file:
            json.dump(existing_conversations, file)

    except Exception as e:
        logging.error(f"Error saving conversation: {e}")

# Function to load conversation from local storage
def load_conversation(conversation_number):
    # Global variable for stored conversation
    global stored_variable
    try:
        file_path = 'conversations/conversations.json'
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
                for conversation in data:
                    if conversation.get('conversation_number') == conversation_number:
                        messages = conversation.get('messages')
                        stored_variable = messages[-1]['stored_conversation'] if messages else []
                        return conversation
            with open(file_path, 'w') as file:
                data.append({"conversation_number": conversation_number, "messages": []})
                json.dump(data, file)
                for conversation in data:
                    if conversation.get('conversation_number') == conversation_number:
                        messages = conversation.get('messages')
                        stored_variable = messages[-1]['stored_conversation'] if messages else []
                        return conversation

    except Exception as e:
        logging.error(f"Error loading conversation {conversation_number}: {e}")
    return {}

# Main function
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)





