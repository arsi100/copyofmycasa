import os
import sys
from flask import Flask, request
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from utils.extract_info_from_pdf import extract_info_from_pdf
from utils.query_db import find_similar_documents
from utils.extract_info_from_pdf import upload_chunked_pdf_data

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

    #$extract_info_from_pdf(filepath)
    upload_chunked_pdf_data(filepath)

    return 'File uploaded and processed successfully'


if __name__ == '__main__':
    app.run(debug=True)
