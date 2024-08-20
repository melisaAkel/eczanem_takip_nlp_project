from flask import Blueprint, request, jsonify, render_template
from flask_mysqldb import MySQL
import pytesseract
import cv2
from PIL import Image
import numpy as np


image_bp = Blueprint('image', __name__)

@image_bp.route('/process_image', methods=['POST'])
def process_image():
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        # Read the image
        image = Image.open(file.stream)
        image = np.array(image)

        # Convert the image to grayscale for better OCR results
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Perform OCR
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(gray, config=custom_config, lang='tur')

        # Extract the relevant sections
        tanı_part = extract_section(text, "Tanı")
        açıklamalar_part = extract_section(text, "Açıklamalar")
        doktor_bilgileri_part = extract_section(text, "Doktor Bilgileri")
        rapor_madde_bilgileri_part = extract_section(text, "Rapor Etkin Madde")

        return jsonify({
            "Tanı": tanı_part,
            "Açıklamalar": açıklamalar_part,
            "Doktor Bilgileri": doktor_bilgileri_part,
            "Rapor Etkin Madde Bilgileri": rapor_madde_bilgileri_part
        })

    except Exception as e:
        # Log the full traceback to get more context
        import traceback
        error_message = traceback.format_exc()
        print(error_message)  # This will appear in your Docker logs
        return jsonify({"error": "An error occurred during processing", "details": str(e)}), 500

def extract_section(text, keyword):
    lines = text.split('\n')
    section = []
    capture = False
    for line in lines:
        if keyword.lower() in line.lower():
            capture = True
        if capture:
            section.append(line)
            # Assuming a blank line ends the section
            if line.strip() == '':
                break
    return '\n'.join(section).strip()

