from datetime import datetime, timedelta

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

def classify_hepatitis_type(text):
    # Convert text to lowercase for normalization
    text = text.lower()

    # Check for keyword patterns for each type
    if "kronik hepatit b" in text or "hbv dna" in text or "entekavir" in text:
        return "Kronik Hepatit B"

    if "karaciğer sirozu" in text or "fibrozis" in text or "hbv dna (+)" in text:
        return "Hepatit B Karaciğer Sirozu"

    if "karaciğer transplantasyonu" in text:
        return "Karaciğer Transplantasyonu"

    if "hepatit d" in text or "delta ajanlı" in text or "anti hdv" in text:
        return "Kronik Hepatit D"

    if "hepatit c" in text or "hcv rna" in text or "sofosbuvir" in text:
        return "Kronik Hepatit C"

    if "akut hepatit c" in text or "pegile interferon" in text or "ribavirin" in text:
        return "Akut Hepatit C"

    # Default case for non-specific conditions
    return "Unknown"


def load_hepatit_guide():
    with open('json/hepatit_tedavisi.json', 'r', encoding='utf-8') as file:
        return json.load(file)



def extract_relevant_guide_section(classified_type, guide_data):
    # Map the classified type to the corresponding section in the guide
    if classified_type == "Kronik Hepatit B":
        return {"kronik_hepatit_b": guide_data.get("hepatit_tedavisi", {}).get("kronik_hepatit_b", {})}
    elif classified_type == "Hepatit B Karaciğer Sirozu":
        return {"hepatit_b_karaciger_sirozu": guide_data.get("hepatit_tedavisi", {}).get("hepatit_b_karaciger_sirozu", {})}
    elif classified_type == "Karaciğer Transplantasyonu":
        return {"karaciger_transplantasyonu": guide_data.get("hepatit_tedavisi", {}).get("karaciger_transplantasyonu", {})}
    elif classified_type == "Kronik Hepatit D":
        return {"kronik_hepatit_d": guide_data.get("hepatit_tedavisi", {}).get("kronik_hepatit_d", {})}
    elif classified_type == "Kronik Hepatit C":
        return {"kronik_hepatit_c": guide_data.get("hepatit_tedavisi", {}).get("kronik_hepatit_c", {})}
    elif classified_type == "Akut Hepatit C":
        return {"akut_hepatit_c": guide_data.get("hepatit_tedavisi", {}).get("akut_hepatit_c", {})}

    # If unknown, return an empty dictionary
    return {}



def include_always_relevant_sections(guide_data):
    # Always include "karaciğer biyopsisi" and "immunsupresif ilaç tedavisi"
    additional_sections = {
        "karaciger_biyopsisi": guide_data.get("hepatit_tedavisi", {}).get("karaciger_biyopsisi", {}),
        "immunsupresif_ilac_tedavisi": guide_data.get("hepatit_tedavisi", {}).get("immunsupresif_ilac_tedavisi", {}),
        "genel_bilgiler": guide_data.get("hepatit_tedavisi", {}).get("genel_bilgiler", {})
    }
    return additional_sections


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
       - **Rapor**: Raporun tanısı ve klinik değerlerini kontrol edin. Yönergelerde belirtilen HBV DNA seviyesi, histolojik aktivite indeksi, fibrozis evresi, ve diğer biyokimyasal kriterlerle karşılaştırarak tedavi başlangıcının ve devamının uygun olup olmadığını belirleyin.
       - **İlişki ve Koşullar**: Yönergelerde yer alan ilişkileri dikkate alın (örn. "veya" ve "ve" operatörleri). Örneğin, fibrozis ≥2 veya histolojik aktivite indeksi ≥6 kriterlerinden biri sağlanmıyorsa tedaviye uygunluk onaylanamaz.

    2. **Uzmanlık Alanı**:
       - **Rapor**: Raporu düzenleyen doktorun uzmanlık alanını kontrol edin. Yönergelere göre tedavi raporunun hangi uzmanlık alanları tarafından düzenlenmesi gerektiğini kontrol edin.

    3. **Tedavi ve İlaç Bilgileri**:
       - **Rapor**: Tedaviye başlanan ilaçları ve dozajları yönergede belirtilen koşullarla karşılaştırın. Tedavi başlangıcı ve devamı için belirtilen HBV DNA eşik değerlerini, devam tedavisinde olası ilaç değişiklikleri ve eklemeleriyle kıyaslayarak tedavi uygunluğunu değerlendirin.

    4. **Sonuç ve Değerlendirme**:
       - Raporun genel yönergelere uygun olup olmadığını analiz edin. Raporun tedavi başlangıcı ve devamı kriterlerine uyup uymadığını belirleyin ve bu durumu açıklayın.

    Sonuç olarak, raporun yönergelere uygunluğunu belirleyin ve gerekçeleriyle birlikte raporun geçerli olup olmadığını belirtin. Eğer rapor ile yönerge uyum göstermiyorsa, özellikle hangi sayısal değerlerin neden uyumsuz olduğunu açıklayın. Cevap net ve anlaşılır olsun, özellikle "ve" ve "veya" gibi koşullara dikkat ederek tüm adımları atlamadan değerlendirin.
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
        validation_result = response.choices[0].message['content'].strip()
        return validation_result
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

        # Classify the extracted text into the correct hepatitis type
        classified_type = classify_hepatitis_type(extracted_text)

        # Extract the relevant guide section based on the classified type
        relevant_section = extract_relevant_guide_section(classified_type, hepatit_guide)

        # Always include specific sections in the query
        additional_sections = include_always_relevant_sections(hepatit_guide)
        relevant_section.update(additional_sections)

        # Log the guide data being sent to OpenAI
        print("Guide Data Being Sent to OpenAI:")
        #print(json.dumps(relevant_section, indent=4, ensure_ascii=False))

        # Validate the report using OpenAI
        validation_message = validate_with_openai(extracted_text, relevant_section)

        # Return the validation result
        return jsonify({
            "is_valid": "compliant" in validation_message.lower(),  # Simple check to see if OpenAI says it's compliant
            "message": validation_message,
            "relevant":relevant_section,
            "extracted": extracted_text
        })

    except Exception as e:
        import traceback
        error_message = traceback.format_exc()
        print(error_message)
        return jsonify({"error": "An error occurred during validation", "details": str(e), "relevant":hepatit_guide}), 500


def parikalsitol_karar_al(pth_duzeyi, alt_artisi_var_mi, albumin_duzey, fosfor_duzey, hasta_tipi, tedavi_formu, doktor_tipi, ilk_rapor_mu, lab_result_date):
    # Step 1: Check if lab results are within the last 3 months
    if lab_result_date < datetime.now() - timedelta(days=90):
        return "Lab sonuçları 3 aydan daha eski, tedavi raporu geçerli değil."

    # Step 2: Check if it's a follow-up report
    if not ilk_rapor_mu:
        # Step 3: Check for treatment termination conditions
        if pth_duzeyi < 150 or albumin_duzey > 10.5 or fosfor_duzey > 6:
            return "Parikalsitol tedavisi sonlandırılmalıdır."
        # Step 4: If no termination condition is met, proceed with follow-up checks
        return "Takip raporlarında tedavi koşulları kontrol edilmelidir."
    if pth_duzeyi < 150 or albumin_duzey > 10.5 or fosfor_duzey > 6:
        return "Parikalsitol tedavisi sonlandırılmalıdır."
    # Step 5: Initial report checks (if it's the first report)
    if not (albumin_duzey < 10.2 and fosfor_duzey < 5.5):
        return "Parikalsitol tedavisi başlatılamaz. Serum kalsiyum veya fosfor düzeyleri uygun değil."

    # Step 6: PTH Level-Based Decisions with Doctor and Patient Type Conditions
    if pth_duzeyi > 600 or (pth_duzeyi > 300 and alt_artisi_var_mi):
        # Additional checks based on patient type and doctor specialization
        if hasta_tipi == "hemodiyaliz" and tedavi_formu == "parenteral":
            if doktor_tipi in ["nefroloji", "iç_hastalıkları", "çocuk_sagligi", "diyaliz_sertifikali"]:
                return "Hemodiyaliz hastaları için parenteral Parikalsitol reçete edilebilir."
            else:
                return "Tedaviyi reçete eden doktor yetkili değil."
        elif hasta_tipi == "periton_diyalizi" and tedavi_formu == "oral":
            if doktor_tipi == "nefroloji":
                return "Periton diyalizi hastaları için oral Parikalsitol reçete edilebilir."
            else:
                return "Tedaviyi reçete eden doktor yetkili değil."
        else:
            return "Tedavi koşulları sağlanıyor ancak hasta tipi veya tedavi formu uygun değil."
    else:
        return "Parikalsitol tedavisi başlatılamaz. PTH koşulları sağlanmamış."

    # If none of the above conditions are met, default to this:
    return "Tedaviye devam edilebilir; uygun rapor ve test sonuçları gerekmektedir."
