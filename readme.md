# Datacomm backend

This repository contains a Flask application which extracts real-estate data from PDF files.

## Setup

### 1. Create a Virtual Environment

```bash
# Create a virtual environment named 'venv'
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 2. Install the Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set the Environment Variables
    
```bash
OPEN_AI_KEY='your key'
DB_STRING='your mongodb connection string
```

### 4. Run the Flask Application

```bash
python main.py
```

### 5. Query the backend endpoints:

```bash
# Replace '/path/to/your/file.pdf' with the actual path to the PDF file
curl -X POST -F "pdf_file=@./PDFs/property4.pdf" "http://127.0.0.1:5000/extract"

curl -X POST -F "query=Do you have any properties in the JVC?" "http://127.0.0.1:5000/query"
```


