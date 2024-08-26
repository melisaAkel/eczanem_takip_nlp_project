from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session
import spacy
from spacy.matcher import Matcher

# Create the blueprint
nlp_bp = Blueprint('nlp', __name__)

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Define custom patterns for entity extraction
patterns = [
    {"label": "DIALYSATE_CALCIUM",
     "pattern": [{"LOWER": "diyalizat"}, {"LOWER": "kalsiyum"}, {"LIKE_NUM": True}, {"TEXT": ".", "OP": "?"}, {"LIKE_NUM": True, "OP": "?"}, {"LOWER": "mmol"}, {"LOWER": "/"}, {"TEXT": "L"}]},
    {"label": "ALBUMIN",
     "pattern": [{"LOWER": "albümin"}, {"IS_PUNCT": True, "OP": "?"}, {"LIKE_NUM": True}, {"TEXT": ".", "OP": "?"}, {"LIKE_NUM": True, "OP": "?"}, {"LOWER": "g"}, {"LOWER": "/"}, {"TEXT": "L"}]},
    {"label": "PTH",
     "pattern": [{"LOWER": "pth"}, {"IS_PUNCT": True, "OP": "?"}, {"LIKE_NUM": True}, {"TEXT": ".", "OP": "?"}, {"LIKE_NUM": True, "OP": "?"}, {"LOWER": "µg"}, {"LOWER": "/"}, {"TEXT": "L"}]},
    {"label": "PHOSPHORUS",
     "pattern": [{"LOWER": "fosfor"}, {"IS_PUNCT": True, "OP": "?"}, {"LIKE_NUM": True}, {"TEXT": ".", "OP": "?"}, {"LIKE_NUM": True, "OP": "?"}, {"LOWER": "mg"}, {"LOWER": "/"}, {"LOWER": "dl"}]},
    {"label": "CALCIUM",
     "pattern": [{"LOWER": "kalsiyum"}, {"IS_PUNCT": True, "OP": "?"}, {"LIKE_NUM": True}, {"TEXT": ".", "OP": "?"}, {"LIKE_NUM": True, "OP": "?"}, {"LOWER": "mg"}, {"LOWER": "/"}, {"LOWER": "dl"}]},
    {"label": "DIAGNOSIS",
     "pattern": [{"LOWER": "tanı"}, {"LOWER": "kronik"}, {"LOWER": "böbrek"}, {"LOWER": "yetmezliği"}, {"LOWER": "tanımlanmamış", "OP":"?"}]},
    {"label": "MEDICATION",
     "pattern": [{"LOWER": "parikalsitol"}, {"LOWER": "parenteral"}, {"LOWER": "haftada"}, {"IS_DIGIT": True}, {"LOWER": "x"}, {"IS_DIGIT": True}, {"LOWER": "µg"}]}
]

# Add the patterns to the matcher
matcher = Matcher(nlp.vocab)
for pattern in patterns:
    matcher.add(pattern["label"], [pattern["pattern"]])


@nlp_bp.route('/nlp', methods=['POST'])
def extract_entities():
    # Retrieve the extracted text from the session
    text = session.get('extracted_text', '')

    # Process the text with spaCy
    doc = nlp(text)

    # Apply the matcher
    matches = matcher(doc)
    extracted_entities = {}

    # Extract matched entities
    for match_id, start, end in matches:
        entity_label = nlp.vocab.strings[match_id]  # Get the entity label
        entity_text = doc[start:end].text
        extracted_entities[entity_label] = entity_text

    # Save the extracted entities back into the session
    session['extracted_entities'] = extracted_entities

    return jsonify({"entities": extracted_entities, "text": text})




@nlp_bp.route('/nlp_check', methods=['POST'])
def nlp_check():
    # Retrieve the extracted entities from the session
    extracted_entities = session.get('extracted_entities', {})

    # Extract the relevant entities for decision-making
    pth_duzeyi = float(extracted_entities.get('PTH', '0').split()[0])
    albumin_duzey = float(extracted_entities.get('ALBUMIN', '0').split()[0])
    fosfor_duzey = float(extracted_entities.get('PHOSPHORUS', '0').split()[0])
    calcium_duzey = float(extracted_entities.get('CALCIUM', '0').split()[0])
    hasta_tipi = "hemodiyaliz"  # Assuming patient type based on context
    tedavi_formu = "parenteral"  # Assuming treatment form based on context
    doktor_tipi = "nefroloji"  # Assuming doctor specialization based on context
    ilk_rapor_mu = True  # Default assumption (could be determined by additional logic)
    lab_result_date = datetime.now()  # Simulating lab result date, replace with actual logic

    # Use extracted entities in the decision-making function
    decision = parikalsitol_karar_al(
        pth_duzeyi=pth_duzeyi,
        alt_artisi_var_mi=True,  # This can be dynamically determined
        albumin_duzey=albumin_duzey,
        fosfor_duzey=fosfor_duzey,
        hasta_tipi=hasta_tipi,
        tedavi_formu=tedavi_formu,
        doktor_tipi=doktor_tipi,
        ilk_rapor_mu=ilk_rapor_mu,
        lab_result_date=lab_result_date
    )

    return jsonify({"decision": decision, "extracted": extracted_entities})


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
