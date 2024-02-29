import os
import sys
from flask import Flask, request
from werkzeug.utils import secure_filename
from openai import OpenAI
from dotenv import load_dotenv
from utils import *
from utils.extract_images_from_pdf_path import extract_images_from_pdf
from utils.extract_text_from_pdf_path import extract_text_from_pdf
from utils.connect_to_db import get_database, get_collection
from utils.str_to_json import str_to_json
from utils.hash_pdf import hash_pdf
from utils.query_db import get_embedding
from utils.query_db import find_similar_documents

app = Flask(__name__)

load_dotenv()
OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')

'''
-----------------------------------------------------------
Extract real estate info into a JSON object from a PDF file
Endpoint: /extract
Method: POST
Parameters: pdf_file (file) as string

Endpoint: /query
Method: POST
Parameters: query (string)

Example:
# Replace '/path/to/your/file.pdf' with the server path to the PDF file
# eventually this is going to be a file uploaded by the user or something
curl -X POST -F "pdf_file=@/path/to/your/file.pdf" http://127.0.0.1:5000/extract
-----------------------------------------------------------
'''
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}

@app.route('/query', methods=['POST'])
def query():
  query = request.form['query']

  if query == '':
    return 'No query provided', 400
   
  find_similar_documents(query)

  return 'Query received and processed successfully'

   

@app.route('/extract', methods=['POST'])
def extract():
    if 'pdf_file' not in request.files:
        return 'No file provided', 400

    pdf_file = request.files['pdf_file']

    if pdf_file.filename == '' or not allowed_file(pdf_file.filename):
        return 'Invalid file', 400

    filename = secure_filename(pdf_file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    pdf_file.save(filepath)

    extract_from_pdf(filepath)

    return 'File uploaded and processed successfully'


def extract_from_pdf(path: str, add_to_db: bool = True, verbose: bool = True) -> None:


    pdf_file_path = path

    if (verbose):
       print('Extracting images from PDF...')
    extract_images_from_pdf(pdf_file_path, f"output/{pdf_file_path}")

    if (verbose):
      print('Extracting text from PDF...')

    text = extract_text_from_pdf(pdf_file_path)

    # Remove special chars
    data = list()
    for sec in text:
        data.append(sec.rstrip('\n\r'))
    query_data = ' '.join(data)

    if (verbose):
       print('Querying LLM...')
    # Query the LLM remotely using openAI
    # note: eventually we can call this locally
    generate_code_schema = {
      "type": "object",
      "properties": {
        "description": {
          "type": "string",
          "description": "English description of the real estate property"
        },
        "price": {
          "type": "array",
          "items": {
            "type": "object",
            "properties" : {
                "price": {
                    "type": "string",
                    "description": "price of the property"
                }, 
                "footage": {
                    "type": "string",
                    "description": "square footage of the property"
                },
                "bedrooms": {
                    "type": "string",
                    "description": "number of bedrooms"
                }
            }
          },
          "description": "json containing number of bedrooms, square footage, and price"
        },
        "amenities": {
          "type": "array",
          "items": {
              "type": "string"
          },
          "description": "list of amenities"
        },
        "location": {
          "type": "string",
          "description": "string of the location of the property"
        }
      },
      "required": ["description", "price", "amenities", "location"],
    }
  
    client = OpenAI(api_key=OPEN_AI_KEY)
    response = client.chat.completions.create(
      model="gpt-3.5-turbo",
       messages=[
          {
            "role": "system",
            "content": "You are a real estate assistant. You will be given a large chunk of text from a PDFs and will be required to find various pieces of information.\n\nIf you don’t know the answer to a question return a N/A in that field.\n\nYou are an assistant that only responds in JSON. Do not write normal text.\n\n[no prose][Output only valid JSON]\n\nReturn responses as a valid JSON object with four keys:\nThe first key is the property description, a string, which must contain all natural language and is a general description about the facts of the listing.\nthe second key is units, and each unit should have the price field, square footage, and number of bedrooms. The third key is amenities, a list of strings, of each amenity. The fourth key is location, a string, representing the location of the property. \n\nThe JSON response must be single line strings. Use the \\n newline character within the string to indicate new lines"
          },
          {
            "role": "user",
            "content": query_data
          },
      ],
      temperature=1,
      max_tokens=2048,
      functions=[ 
          {   # this custom schema forces JSON output and allows us to specify the fields we want
              "name": "generate_code",
              "description": "generates real estate fields in JSON format. used by code assistants",
              "parameters": generate_code_schema
          }
      ],
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )

    if (verbose):
       print('Response received from LLM...')
       print(response.choices[0].message.function_call.arguments)
    
    # write the reponse to a file with the same name as the pdf
    if (verbose):
      print('Writing json to file...')
    with open(f"{pdf_file_path[:-4]}_extracted.json", "w") as f:
        f.write(str(response.choices[0].message.function_call.arguments))

    if (verbose):
      print('Calculating hash...')
    # Calculate hash of pdf
    text_hash = hash_pdf(query_data)

    if (add_to_db):
      # check if hash already exists in database
      if (verbose):
        print('Checking database for duplicates...')
      property_db = get_database()
      property_collection = get_collection(property_db, 'properties_embed')

      if (property_collection.find_one({"property_hash" : text_hash})):
        if (verbose):
          print('Duplicate found, skipping...')
        add_to_db = False

      if (verbose):
        print('Adding data to database...')
      # Add to database
      json_response = str_to_json(str(response.choices[0].message.function_call.arguments))
      property_collection = get_collection(property_db, 'properties_embed')
      image_collection = get_collection(property_db, 'images')
      embedding = get_embedding(str(json_response['description'] + json_response['location']) + str(json_response['amenities']) + str(json_response['price']) + str(json_response['price']))
      
      property_collection.insert_one({
        "property_hash" : text_hash,
        "description" : json_response['description'],
        "price" : json_response['price'],
        "amenities" : json_response['amenities'],
        "location" : json_response['location'],
        "embedding" : embedding
      })

      # loop through directory and add images to database
      # store images in array and add all at once to avoid multiple db calls
      if (verbose):
        print('Adding images to database...')
      for filename in os.listdir(f"output/{pdf_file_path}"):
        if filename.endswith(".png"):
          with open(f"output/{pdf_file_path}/{filename}", "rb") as image_file:
            encoded_string = image_file.read()
            image_collection.insert_one({
              "property_hash" : text_hash,
              "image" : encoded_string
            })


if __name__ == '__main__':
    app.run(debug=True)
