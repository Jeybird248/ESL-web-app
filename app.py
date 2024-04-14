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

MIXTRAL_URL = 'https://mixtral.k8s-gosha.atlas.illinois.edu/completion'
MIXTRAL_USERNAME = 'atlasaiteam'
MIXTRAL_PASSWORD = 'jx@U2WS8BGSqwu'

nltk.download('punkt')
logging.basicConfig(filename='app.log', level=logging.INFO)
gn = GoogleNews(lang='en', country='US')
app = Flask(__name__)
CORS(app)

stored_variable = None
current_conversation = 1
article_text = None
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/grammar')
def grammar():
    return render_template('grammar.html')

@app.route('/article')
def article():
    return render_template('article.html')

@app.route('/fetch_article_text', methods=['POST'])
def fetch_article_text():
    global article_text
    try:
        s = gn.top_news()
        url = s['entries'][0].link
        article = Article(url, language='en')
        article.download()
        article.parse()
        article_text = article.text

        # Generate questions and answers using MIXTRAL or any other service
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
        

        if response.status_code != 200:
            raise Exception(f'MIXTRAL API request failed with status code {response.status_code}')
        
        # Parse MIXTRAL response and extract questions, answer choices, and correct answers
        mixtral_data = response.json()
        mixtral_data = mixtral_data.get('content', "")
        print("before cleaning:",  mixtral_data)
        print()
        json_start_index = mixtral_data.find('{')
        json_end_index = mixtral_data.find('}')
        mixtral_data = mixtral_data[json_start_index:json_end_index + 1]
        mixtral_data.replace("\\", "")
        mixtral_data.replace("\'", "\"")
        mixtral_data = json.loads(mixtral_data)
        print("after cleaning:",  mixtral_data)
        print()

        questions = mixtral_data.get('questions', [])
        answer_choices = mixtral_data.get('answer_choices', [])
        short_answers = mixtral_data.get('short_answer_questions', [])
        correct_answers = mixtral_data.get('correct_answers', [])
        print(questions, answer_choices, short_answers, correct_answers)

        # Return article text, questions, answer choices, and correct answers in JSON format
        return jsonify({
            'articleText': article_text,
            'questions': questions,
            'shortAnswer': short_answers,
            'answerChoices': answer_choices,
            'correctAnswers': correct_answers
        })

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@app.route('/incorrect_answers', methods=["POST"])
def query_incorrect():
    global article_text
    data = request.json
    questions = data.get('questions', [])
    correct_answers = data.get('correctAnswers', [])
    print(questions, correct_answers)
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
    if response.status_code != 200:
        raise Exception(f'MIXTRAL API request failed with status code {response.status_code}')
    
    mixtral_data = response.json()['content']
    print("before", mixtral_data)
    json_start_index = mixtral_data.find('{')
    json_end_index = mixtral_data.find('}')
    mixtral_data = mixtral_data[json_start_index:json_end_index + 1]
    mixtral_data.replace("\\", "")
    mixtral_data.replace("\'", "\"")
    print("after", mixtral_data)
    mixtral_data = json.loads(mixtral_data).get('answer_explanations', [])
    print("explanations", mixtral_data)
    return jsonify({
        'answer_explanations': mixtral_data
    })

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/conversation/count', methods=['GET'])
def get_conversation_count():
    file_path = 'conversations/conversations.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            return jsonify({"conversation_count": len(data)})

@app.route('/submit/<int:conversation_number>', methods=['GET','POST'])
@app.route('/submit', methods=['POST'])
def submit(conversation_number = None):
    global stored_variable
    global current_conversation

    edited_sentences = []
    if conversation_number:
        current_conversation = conversation_number
        response = load_conversation(current_conversation)
        conversation = response.get("messages")[-1]["stored_conversation"] if response.get("messages") else []
        return jsonify(conversation)
    try:
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
                    # Make API call to Mixtral
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
                    # Process the Mixtral response and store information
                    process_mixtral_response(user_input, mixtral_output['content'])
                    edited_sentences.append(mixtral_output['content'])
                except requests.exceptions.RequestException as api_error:
                    logging.error(f"Mixtral API error: {api_error}")
                    edited_sentences.append([f"Error processing: {s}." for s in batch])

            # Save the conversation to local storage
            save_conversation(user_input, edited_sentences, current_conversation)
            # Return suggestions and edited text as JSON
            response_data = {
                'edited_text': edited_sentences,
            }

            return jsonify(response_data)
        else:
            try:
                # Make API call to Mixtral
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
                # Process the Mixtral response and store information
                # process_mixtral_response(user_input, mixtral_output['content'])
                edited_sentences.append(mixtral_output['content'])
            except requests.exceptions.RequestException as api_error:
                logging.error(f"Mixtral API error: {api_error}")
                edited_sentences.append([f"Error processing: {s}." for s in batch])
            save_conversation(user_input, edited_sentences, current_conversation)
            # Return suggestions and edited text as JSON
            response_data = {
                'edited_text': edited_sentences
            }

            return jsonify(response_data)

    except Exception as e:
        logging.error(f"Error processing user input: {e}")
        return jsonify({'error': 'An error occurred.'}), 500

def process_mixtral_response(user_input, mixtral_response):
    global stored_variable
    try:
        sentences = nltk.sent_tokenize(mixtral_response)
        max_similarity = 0
        closest_sentence = ""

        for sentence in sentences:
            similarity = fuzz.token_set_ratio(user_input, sentence)
            if similarity > max_similarity and user_input != sentence:
                max_similarity = similarity
                closest_sentence = sentence

        explanation = mixtral_response.replace(closest_sentence, '').replace('Explanation:', '').strip()
        
        stored_variable = (closest_sentence.strip(), user_input.strip(), 'Explanation: ' + explanation.strip())
    except Exception as e:
        logging.error(f"Error processing Mixtral response: {e}")

def save_conversation(user_input, edited_sentences, conversation_number):
    global stored_variable
    try:
        edited_sentences = '\n'.join(edited_sentences)
        file_path = 'conversations/conversations.json'
        conversation_data = {'user_input': user_input, 'edited_sentences': edited_sentences, 'stored_conversation': []}

        # Load existing conversations or create a new array if the file doesn't exist
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                existing_conversations = json.load(file)
        else:
            existing_conversations = []
        # Find the conversation with the specified number or create a new one if not found
        conversation = next((conv for conv in existing_conversations if conv.get('conversation_number') == conversation_number), None)
        if conversation is None:
            conversation = {'conversation_number': conversation_number, 'messages': []}

        # Append new message to the conversation
        stored_converesation = conversation.get("messages")[-1]["stored_conversation"] if conversation.get("messages") else []
        stored_converesation.append(user_input)
        stored_converesation.append(edited_sentences)
        conversation['messages'].append({'user_input': user_input, 'edited_sentences': edited_sentences, 'stored_conversation': stored_converesation})
        
        # Append the updated conversation to the list of conversations
        if conversation_number in [conv.get('conversation_number') for conv in existing_conversations]:
            existing_conversations = [conv for conv in existing_conversations if conv.get('conversation_number') != conversation_number]
        existing_conversations.append(conversation)

        # Save the updated conversations to file
        with open(file_path, 'w') as file:
            json.dump(existing_conversations, file)

    except Exception as e:
        logging.error(f"Error saving conversation: {e}")

def load_conversation(conversation_number):
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)




