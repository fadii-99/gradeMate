import cv2
import numpy as np
import easyocr

def preprocess_image(image):
    """Preprocess image to improve OCR accuracy."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5,5), 0)  # Reduce noise
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # Convert to binary
    return binary

def extract_text(file_obj):
    """Extract text from a file-like object (Django InMemoryUploadedFile) using OCR."""
    # If the input is a file-like object, convert it to an OpenCV image:
    if hasattr(file_obj, "read"):
        image = convert_to_cv2_image(file_obj)
    else:
        image = file_obj

    # Preprocess the image
    processed_img = preprocess_image(image)
    
    # Initialize OCR reader
    reader = easyocr.Reader(['en'])
    results = reader.readtext(processed_img, detail=1)  # Returns list of [bbox, text, confidence]

    # Sort results based on Y-coordinate (to maintain line order)
    results.sort(key=lambda x: x[0][0][1])
    extracted_lines = []
    current_line = []
    prev_y = -10

    for bbox, text, _ in results:
        y = bbox[0][1]
        if abs(y - prev_y) > 10:  # New line detected if significant vertical gap
            if current_line:
                extracted_lines.append(" ".join(current_line))
                current_line = []
        current_line.append(text)
        prev_y = y

    if current_line:
        extracted_lines.append(" ".join(current_line))

    return extracted_lines

def convert_to_cv2_image(file_obj):
    file_bytes = np.asarray(bytearray(file_obj.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    file_obj.seek(0)  # Reset the file pointer for future use
    return image


def correct_cpp_code(lines):
    """Apply common C++ corrections."""
    corrections = {
        "includde": "include", "includ": "include", 
        "<iostream <": "<iostream>", 
        "mainC)": "main()", 
        "Lint": "int", "int 0 =5>": "int a = 5;",
        "int b=10;": "int b = 10;", "bI0Z": "b=10;",
        "Sum_": "sum", "Ctb)": "a + b;",
        "stc ef_": "std::", "Sum <Sum 2 cout @and bis": 'std::cout << "Sum of a and b is " << sum;',
        "return_": "return", "0 ;": "0;"
    }

    corrected_lines = []
    for line in lines:
        for wrong, correct in corrections.items():
            line = line.replace(wrong, correct)
        corrected_lines.append(line)

    return corrected_lines

