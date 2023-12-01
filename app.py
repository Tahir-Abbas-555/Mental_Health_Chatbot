import uuid
import json
import os
from flask import Flask,request,jsonify
import pprint
import google.generativeai as palm
import random
from flask_cors import CORS
from gloabl_ver import questions
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("BARD_API_KEY")
if not api_key:
    raise ValueError("OpenAI API key not found. Make sure it's set in the .env file.")

folder_path = "Flask_sessions"



palm.configure(api_key=api_key)

file_path = 'stored_data.json'

QNA = {}

app = Flask (__name__)

CORS(app, origins='*')

@app.route('/generate_session', methods=['GET'])
def generate_session():
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    session_id = str(uuid.uuid4())
    filename = f"{folder_path}/{session_id}.json"
    # Data to be written to the JSON file (null values)
    data = []
    # Write the data to the JSON file
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    return jsonify(session_id)

@app.route('/generate_questions/<session_id>', methods=["GET"])
def generate_questions(session_id):
    number_of_questions = 10
    ask_question = random.sample(questions,number_of_questions)
    return jsonify(ask_question)

@app.route("/store_qa/<session_id>", methods=["POST"])
def store_qa(session_id):
    
    try:
        if request.form:
            data = request.form.get
        else:
            # If not, assume JSON data
            data = request.get_json()
        # Check if the file exists
        if os.path.exists(f"{folder_path}/{session_id}.json"):
            # If the file exists, load existing data
            with open(f"{folder_path}/{session_id}.json", 'r') as file:
                existing_data = json.load(file)
            
            # Append the new data to the existing data
            existing_data.append(data)
        else:
            # If the file doesn't exist, create a new list with the incoming data
            response = {'status': 'error', 'message': 'Invalid session ID'}
            return jsonify(response)

        # Write the combined data back to the file
        with open(f"{folder_path}/{session_id}.json", 'w') as file:
            json.dump(existing_data, file)

        response = existing_data
    except Exception as e:
        response = {'status': 'error', 'message': str(e)}

    return jsonify(response)
    
@app.route("/predict",methods=["POST"])
def predict():

    if request.form:
        data = request.form.get
    else:
        # If not, assume JSON data
        data = request.get_json()
    print(data)
    prompt = f""" 
        you are an expert mental health analyzer who can predict the setiment("positive","negative","neutral") of person using question and answer.
        predict the mental health using this data:{data}.
        just tell us the setiment of person using question and answer.
        """
    completion = palm.generate_text(
        model="models/text-bison-001",
        prompt=prompt,
        temperature=0.4,
    )
    if (completion.result).lower() == "positive":
        print({"link":"https://www.youtube.com/watch?v=ZbZSe6N_BXs","sentiment":completion.result})
        return {"link":"https://www.youtube.com/watch?v=ZbZSe6N_BXs","sentiment":completion.result}
    elif (completion.result).lower() == "negative":
        print({"link":"https://www.youtube.com/watch?v=8AHCfZTRGiI","sentiment":completion.result})
        return {"link":"https://www.youtube.com/watch?v=8AHCfZTRGiI","sentiment":completion.result}
    elif (completion.result).lower() == "neutral":
        print({"link":"https://www.youtube.com/watch?v=8AHCfZTRGiI","sentiment":completion.result})
        return {"link":"https://www.youtube.com/watch?v=qYnA9wWFHLI","sentiment":completion.result}
    return jsonify(completion.result)
    
if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=4000)