import PyPDF2
import pytesseract
from PIL import Image, ImageEnhance
import pdf2image
import re

# Common unwanted patterns (you can customize these)
UNWANTED_PATTERNS = [
    r'Scanner by .+',  # Matches phrases like "Scanner by XYZ"
    r'\d+\s*/\s*\d+',  # Matches page numbers like "1 / 9"
]

# Function to remove unwanted text (scanner marks, page numbers, etc.)
def clean_text(text):
    for pattern in UNWANTED_PATTERNS:
        text = re.sub(pattern, '', text)
    return text.strip()

# Function to preprocess image for better OCR
def preprocess_image(image):
    # Convert image to grayscale
    image = image.convert('L')

    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)

    # Apply thresholding to make text clearer
    image = image.point(lambda p: p > 128 and 255)  # Binary threshold

    return image

# Function to perform OCR on an image without saving
def ocr_image(image):
    # Preprocess the image
    preprocessed_image = preprocess_image(image)

    # Perform OCR on the preprocessed image
    text = pytesseract.image_to_string(preprocessed_image)

    return text

# Function to check if "Scanner by" text exists in the extracted page text
def contains_scanner_text(page_text):
    scanner_pattern = r"Scanner by"
    return bool(re.search(scanner_pattern, page_text))

# Extract text from mixed PDFs (both text and scanned images)
def extract_text_from_mixed_pdf(pdf_path):
    text = ""

    # Open the PDF
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(reader.pages)

        for page_number in range(num_pages):
            page = reader.pages[page_number]
            page_text = page.extract_text()

            if page_text and not contains_scanner_text(page_text):
                # If there is regular text and no "Scanner by", extract it normally
                page_text = clean_text(page_text)
                text += page_text
            elif page_text and contains_scanner_text(page_text):
                # If "Scanner by" is found, use OCR by converting PDF page to an image
                images = pdf2image.convert_from_path(pdf_path, first_page=page_number + 1, last_page=page_number + 1)

                # Perform OCR on each image (representing one page)
                for image in images:
                    ocr_text = ocr_image(image)  # OCR without saving
                    ocr_text = clean_text(ocr_text)  # Clean unwanted patterns
                    text += ocr_text
            else:
                # If no text is found at all, treat the page as a fully scanned page
                images = pdf2image.convert_from_path(pdf_path, first_page=page_number + 1, last_page=page_number + 1)

                # Perform OCR on each image (representing one page)
                for image in images:
                    ocr_text = ocr_image(image)  # OCR without saving
                    ocr_text = clean_text(ocr_text)  # Clean unwanted patterns
                    text += ocr_text

    return text
