from flask import Blueprint, request, jsonify, session
from PIL import Image
import pytesseract
import cv2
import numpy as np
import json
import re
import openai

image_bp = Blueprint('image', __name__)

# Configure your OpenAI API key

def load_hepatit_guide():
    with open('json/hepatit_tedavisi.jsonl', 'r', encoding='utf-8') as file:
        return json.load(file)



def validate_with_openai(extracted_data, guide_data):
    # Use OpenAI to enhance validation logic or assist in understanding the extracted data
    prompt = f"""
    Verilen tıbbi raporun yönergelere uygunluğunu analiz edin. Aşağıdaki verileri kullanarak, raporda yer alan tanı, klinik değerler, uzmanlık alanı ve tedavi bilgilerini yönergelerle karşılaştırarak raporun uygun olup olmadığını belirleyin ve sonucu belirtin.

    ### Çıkarılan Rapor:
    {json.dumps(extracted_data, ensure_ascii=False)}

    ### Yönergeler:
    {json.dumps(guide_data, ensure_ascii=False)}

    ### Analiz ve Sonuç

    Lütfen aşağıdaki adımları izleyerek analiz yapın:

    1. **Tanı ve Klinik Değerler**:
       - **Rapor**: Raporun tanısı ve klinik değerlerini kontrol edin. Yönergelerde belirtilen HBV DNA seviyesi, histolojik aktivite indeksi ve diğer biyokimyasal kriterlerle karşılaştırarak tedavi başlangıcının ve devamının uygun olup olmadığını belirleyin. Özellikle tarihler arasında bir tutarlılık olup olmadığını ve tedavi sürecinde değişen değerleri dikkate alın.

    2. **Uzmanlık Alanı**:
       - **Rapor**: Raporu düzenleyen doktorun uzmanlık alanını kontrol edin. Yönergelere göre tedavi raporunun hangi uzmanlık alanları tarafından düzenlenmesi gerektiğini kontrol edin.

    3. **Tedavi ve İlaç Bilgileri**:
       - **Rapor**: Tedaviye başlanan ilaçları ve dozajları yönergede belirtilen koşullarla karşılaştırın. Tedavi başlangıcı ve devamı için belirtilen HBV DNA eşik değerlerini, devam tedavisinde olası ilaç değişiklikleri ve eklemeleriyle kıyaslayarak tedavi uygunluğunu değerlendirin.

    4. **Sonuç ve Değerlendirme**:
       - Raporun genel yönergelere uygun olup olmadığını analiz edin. Raporun tedavi başlangıcı ve devamı kriterlerine uyup uymadığını belirleyin ve bu durumu açıklayın.

    Sonuç olarak, raporun yönergelere uygunluğunu belirleyin ve gerekçeleriyle birlikte raporun geçerli olup olmadığını belirtin.
    Eğer raporla yönerge uymuyorsa bunun sayısal bir değeri varsa belirtiniz neden olmadığı. Cevap hızlı göz gezdirirken anlaşılır olması için daha odaklı ve direkt olabilir. Maddeleri atlamadan.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # The OpenAI model you're using
            messages=[
                {"role": "system", "content": "You are an expert assistant helping to validate medical reports."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.5,
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error during OpenAI validation: {str(e)}"


@image_bp.route('/set_extracted_text', methods=['POST'])
def set_extracted_text():
    try:
        # Get the extracted text from the request body
        extracted_text = request.json.get('extracted_text')

        if not extracted_text:
            return jsonify({"error": "No extracted text provided"}), 400

        # Store the extracted text in the session
        session['extracted_text'] = extracted_text

        # Return a success response
        return jsonify({"message": "Extracted text has been updated successfully.", "extracted_text": extracted_text})

    except Exception as e:
        import traceback
        error_message = traceback.format_exc()
        print(error_message)
        return jsonify({"error": "An error occurred while setting the extracted text", "details": str(e)}), 500


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

        # Run OCR on the entire image
        text = pytesseract.image_to_string(gray, config=r'--oem 3 --psm 6', lang='tur')

        # Store the extracted text in the session
        session['extracted_text'] = text

        # Extract and return the text
        return jsonify({
            "ExtractedText": text
        })

    except Exception as e:
        import traceback
        error_message = traceback.format_exc()
        print(error_message)
        return jsonify({"error": "An error occurred during processing", "details": str(e)}), 500

@image_bp.route('/validate_report', methods=['POST'])
def validate_report():
    try:
        # Load the JSON guide
        hepatit_guide = load_hepatit_guide()

        # Retrieve the extracted text from the session
        extracted_text = session.get('extracted_text', '')

        if not extracted_text:
            return jsonify({"error": "No extracted text found. Please process the image first."}), 400


        # Validate the report using OpenAI
        openai_validation = validate_with_openai(extracted_text, hepatit_guide)

        # Return the validation result
        return jsonify({
            "is_valid": "compliant" in openai_validation.lower(),  # Simple check to see if OpenAI says it's compliant
            "message": openai_validation
        })

    except Exception as e:
        import traceback
        error_message = traceback.format_exc()
        print(error_message)
        return jsonify({"error": "An error occurred during validation", "details": str(e)}), 500
