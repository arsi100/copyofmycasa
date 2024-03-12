from utils.extract_info_from_pdf import extract_info_from_pdf
from utils.query_llm import ask_question, generate_rag__chain
from werkzeug.utils import secure_filename
from flask import Flask, request
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()
OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')
UPLOAD_FOLDER = 'temp_uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/query', methods=['POST'])
def query():
    """
    FLASK API endpoint to query the LLM model
    @ return: response from the LLM model
    """

    # todo, needs also take a chat id to load the history from the db
    # also should be cacheing the rag_chain 
    query = request.form['query']

    if query == '':
        return 'No query provided', 400
   
    rag_chain = generate_rag__chain()
    msg = ask_question(query, rag_chain, chat_history=[])

    return msg 

@app.route('/extract', methods=['POST'])
def extract():
    '''
    FLASK API endpoint to extract information and upload chunked data to mongodb 
    @ params: request object with a PDF file see README for more details
    @ return: response from the LLM model
    '''
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}

    if 'pdf_file' not in request.files:
        return 'No file provided', 400

    pdf_file = request.files['pdf_file']

    if pdf_file.filename == '' or not allowed_file(pdf_file.filename):
        return 'Invalid file', 400

    filename = secure_filename(pdf_file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    pdf_file.save(filepath)

    extract_info_from_pdf(filepath)

    return 'File uploaded and processed successfully'


if __name__ == '__main__':
    app.run(debug=True)
