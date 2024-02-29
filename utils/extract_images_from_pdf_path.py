import fitz  # PyMuPDF
import os
import io
from PIL import Image
import numpy as np

MIN_Y = 400  # Minimum width of "hero" images
MIN_X = 400  # Minimum height of "hero" images

'''
-----------------------------------------------------------
This function is used to determine if an image is mostly white or not.
-----------------------------------------------------------
Parameters:
    image: PIL.Image
Returns:
    bool: True if the image is mostly white, False otherwise
-----------------------------------------------------------
'''
def is_mostly_white(image):
    # Convert the image to grayscale
    grayscale_image = image.convert('L')
    
    # Convert the grayscale image to a NumPy array
    image_array = np.array(grayscale_image)
    
    # Calculate the percentage of white pixels (close to 255)
    white_pixel_percentage = (image_array >= 240).sum() / image_array.size * 100
    
    # You can adjust the threshold as needed; this example uses 95% as a threshold
    return white_pixel_percentage >= 95

'''
-----------------------------------------------------------
This function is used to extract images from a PDF file.
-----------------------------------------------------------
Parameters:
    pdf_path: str
    image_folder: str
Returns:
    None
-----------------------------------------------------------
'''
def extract_images_from_pdf(pdf_path, image_folder="output_images"):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    # Create the output folder if it doesn't exist
    os.makedirs(f'{image_folder}/images', exist_ok=True)

    # Hold the cached images so we don't save dupes
    cached_images = set()

    # Iterate through the pages of the PDF
    i = 0
    for page_number in range(pdf_document.page_count):
        page = pdf_document.load_page(page_number)

        # Get the XObjects (image objects) on the page
        xobjects = page.get_images(full=True)
        
        for img_index, xobject in enumerate(xobjects):
            image = pdf_document.extract_image(xobject[0])
            image_bytes = image["image"]

            # Filter images in the PDF and save the relevant ones
            if not (image['width'] >= MIN_X and image['height'] >= MIN_Y):
                continue
            # do not allow duplicates
            if str(image_bytes) in cached_images:
                continue
            # do not allow all white/black images
            if is_mostly_white(Image.open(io.BytesIO(image_bytes))):
                continue
            cached_images.add(str(image_bytes))
            i += 1
            
            # Save the image to a file
            image_filename = f"{image_folder}/page_{page_number}_img_{img_index}.png"
            with open(image_filename, "wb") as f:
                f.write(image_bytes)

            
    if i == 0:
        # delete the empty folder
        pass
        #os.rmdir(image_folder)

    # Close the PDF document
    pdf_document.close()


if __name__ == "__main__":
    # Specify the PDF file path and the folder where you want to save the extracted images
    pdf_file_path = "PDFs/property2.pdf"
    output_image_folder = "output_images"

    # Extract images from the PDF
    extract_images_from_pdf(pdf_file_path, output_image_folder)
