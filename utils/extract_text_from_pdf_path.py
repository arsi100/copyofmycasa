import fitz 
import sys

'''
-----------------------------------------------------------
This function is used to extract text from a PDF file.
-----------------------------------------------------------
Parameters:
    pdf_path: str
Returns:
    extracted_text: str
-----------------------------------------------------------
'''
def extract_text_from_pdf(pdf_path):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    # Initialize a variable to store the extracted text
    extracted_text = []

    # Iterate through the pages of the PDF
    for page_number in range(pdf_document.page_count):
        page = pdf_document.load_page(page_number)

        # Extract text from the page
        page_text = page.get_text()
        extracted_text.append(page_text)

    # Close the PDF document
    pdf_document.close()

    return extracted_text

if __name__ == "__main__":

    # Specify the PDF file path
    try:
        path = sys.argv[1]
    except:
        path = "PDFs/property2.pdf"

    # Extract text from the PDF
    extracted_text = extract_text_from_pdf(path)

    # Combine the text from all pages into a single string
    all_text = "\n".join(extracted_text)

    # Print or process the extracted text as needed
    print(all_text)
