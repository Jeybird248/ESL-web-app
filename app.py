from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
# from transformers import AutoTokenizer, T5ForConditionalGeneration
from nltk import sent_tokenize
import nltk 
import requests
import base64

MIXTRAL_URL = 'https://mixtral.k8s-gosha.atlas.illinois.edu/completion'
MIXTRAL_USERNAME = 'atlasaiteam'
MIXTRAL_PASSWORD = 'jx@U2WS8BGSqwu'

# tokenizer = AutoTokenizer.from_pretrained("grammarly/coedit-large")
# model = T5ForConditionalGeneration.from_pretrained("grammarly/coedit-large")
nltk.download('punkt')

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/grammar')
def grammar():
    return render_template('grammar.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json()
        user_input = data.get('userInput', '')

        # Split user input into sentences
        sentences = sent_tokenize(user_input)

        edited_sentences = []

        # Process sentences in batches of up to 3
        batch_size = 3
        for i in range(0, len(sentences), batch_size):
            batch = sentences[i:i+batch_size]
            try:
                # Make API call to Mixtral
                response = requests.post(
                    MIXTRAL_URL,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': 'Basic YXRsYXNhaXRlYW06anhAVTJXUzhCR1Nxd3U='
                    },
                    json={
                        'prompt': '<s>[INST]ESL Correction Task: You will receive: 1. A paragraph of English text, potentially containing grammar or spelling mistakes. The model is expected to output: 1. A corrected version of the paragraph. 2. An accompanying explanation for each correction, explained in simple terms, assuming the user has limited knowledge of English grammar. The explanations should use examples to clarify concepts. Use <br> to create new lines after each sentence. These are the sentences you need to fix: {}[/INST]</s>'.format('<br>'.join(batch)),
                        'n_predict': 600,
                    }
                )

                response.raise_for_status()

                mixtral_output = response.json()
                print(mixtral_output)
                edited_sentences.append(mixtral_output['content'])
            except requests.exceptions.RequestException as api_error:
                print(f"Mixtral API error: {api_error}")
                edited_sentences.extend([f"Error processing: {s}. [Correction: Your corrected sentence here. Explanation: Provide a simple explanation.]" for s in batch])
        # Return suggestions and edited text as JSON
        response_data = {
            'edited_text': edited_sentences
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"Error processing user input: {e}")
        return jsonify({'error': 'An error occurred'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)




