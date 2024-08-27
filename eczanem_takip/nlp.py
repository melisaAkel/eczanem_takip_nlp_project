from datetime import datetime, timedelta
import re
from flask import Blueprint, request, jsonify, session
import spacy
from spacy.matcher import Matcher

# Create the blueprint
nlp_bp = Blueprint('nlp', __name__)

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

patterns = [
    {"label": "DIALYSATE_CALCIUM",
     "pattern": [
         {"TEXT": {"REGEX": r"(?i)^diyalizat$"}},
         {"TEXT": {"REGEX": r"(?i)^kalsiyum(un(un)?)?$"}},
         {"TEXT": {"REGEX": r"^\d+(\.\d+)?$"}},
         {"TEXT": ".", "OP": "?"},
         {"TEXT": {"REGEX": r"^\d+$"}, "OP": "?"},
         {"IS_SPACE": True, "OP": "?"},
         {"LOWER": "mmol"},
         {"LOWER": "/"},
         {"LOWER": {"IN": ["l", "it"]}}
     ]},
    {"label": "ALBUMIN",
     "pattern": [
         {"LOWER": {"IN": ["albumin", "albümin"]}},
         {"IS_PUNCT": True, "OP": "?"},
         {"TEXT": {"REGEX": r"^\d+(\.\d+)?(mg|µg|g|dl)?$"}},  # Captures numbers with or without attached units
     ]},
    {"label": "PTH",
     "pattern": [
         {"LOWER": "pth"},
         {"IS_PUNCT": True, "OP": "?"},
         {"TEXT": {"REGEX": r"^\d+(\.\d+)?(µg|ug)?$"}},  # Captures numbers with or without attached units
     ]},
    {"label": "PHOSPHORUS",
     "pattern": [
         {"LOWER": {"IN": ["fosfor", "p"]}},
         {"IS_PUNCT": True, "OP": "?"},
         {"TEXT": {"REGEX": r"^\d+(\.\d+)?(mg|µg|g|dl)?$"}},  # Captures numbers with or without attached units
     ]},
    {"label": "CALCIUM",
     "pattern": [
         {"LOWER": {"IN": ["kalsiyum", "ca"]}},
         {"IS_PUNCT": True, "OP": "?"},
         {"TEXT": {"REGEX": r"^\d+(\.\d+)?(mg|µg|g|dl)?$"}},  # Captures numbers with or without attached units
     ]},
    {"label": "DIAGNOSIS",
     "pattern": [
         {"LOWER": "tanı"},
         {"IS_PUNCT": True, "OP": "?"},
         {"LOWER": "kronik"},
         {"LOWER": "böbrek"},
         {"LOWER": "yetmezliği"}
     ]},
    {"label": "MEDICATION",
     "pattern": [
         {"LOWER": "parikalsitol"}
     ]},
    {"label": "LAB_RESULT_DATE",
     "pattern": [
         {"LOWER": {"IN": ["albumin", "pth", "ca", "p"]}},  # Matches entity labels
         {"TEXT": "-", "OP": "?"},  # Matches optional dash
         {"LOWER": "tarih"},  # Matches "Tarih"
         {"TEXT": ":", "OP": "?"},  # Matches optional colon after "Tarih"
         {"TEXT": {"REGEX": r"\b\d{2}[./-]\d{2}[./-]\d{4}\b"}},  # Matches the date (dd.mm.yyyy)
         {"LOWER": {"IN": ["sonuc", "sonuç"]}},  # Matches "Sonuc" or "Sonuç"
         {"TEXT": {"IN": ["-", "—"]}, "OP": "?"},  # Matches optional dash
         {"IS_SPACE": True, "OP": "?"},  # Handles any spaces
         {"TEXT": {"REGEX": r"^\d+(\.\d+)?$"}},  # Captures numeric results like "3.8" or "967"
         {"TEXT": ",", "OP": "?"},  # Matches optional comma
     ]},
    {"label": "DOCTOR",
     "pattern": [
         {"TEXT":{"IN":["iç", "İç"]} },
         {"LOWER": "hastalıkları"}
     ]},
    {"label": "DOCTOR",
     "pattern": [
         {"LOWER": "diyaliz"},
         {"IS_PUNCT": True, "OP": "?"},
         {"LOWER": "sertifikalı"}
     ]},
    {"label": "DATE",
     "pattern": [
         {"TEXT": {"REGEX": r"\b\d{2}[./-]\d{2}[./-]\d{4}\b"}}
     ]},
    {"label": "DOCTOR",
     "pattern": [
         {"LOWER": "çocuk"},
         {"IS_PUNCT": True, "OP": "?"},
         {"LOWER": "sağlığı"}
     ]},
    {"label": "DOCTOR",
     "pattern": [
         {"LOWER": "nefroloji"}
     ]},
    {"label": "MEDICATION_FORM",
     "pattern": [
         {"LOWER": "oral"}
     ]},
    {"label": "MEDICATION_FORM",
     "pattern": [
         {"LOWER": "parenteral"}
     ]},
    {"label": "TYPE",
     "pattern": [
         {"LOWER": "periton"},
         {"IS_PUNCT": True, "OP": "?"},
         {"LOWER": "diyalizi"}
     ]},
    {"label": "TYPE",
     "pattern": [
         {"LOWER": "hemodiyaliz"}
     ]},
    # Handling repeated measurements in one sentence
    {"label": "LAB_RESULT",
     "pattern": [
         {"LOWER": {"IN": ["albümin", "albumin", "pth", "fosfor", "kalsiyum", "ca", "p"]}},
         {"IS_PUNCT": True, "OP": "?"},
         {"TEXT": ":"},
         {"TEXT": {"REGEX": r"^\d+(\.\d+)?(mg|µg|g|dl)?$"}},  # Captures numbers with or without attached units
         {"TEXT": ".", "OP": "?"},
         {"TEXT": {"REGEX": r"^\d+$"}, "OP": "?"},  # Optional second numeric part
         {"IS_SPACE": True, "OP": "?"},  # Handles optional spaces
         {"IS_PUNCT": True, "OP": "?"},
         {"TEXT": "-", "OP": "?"},
         {"TEXT": {"REGEX": r"\b\d{2}[./-]\d{2}[./-]\d{4}\b"}, "OP": "?"}
     ]},
]

# Add the patterns to the matcher
matcher = Matcher(nlp.vocab)
for pattern in patterns:
    matcher.add(pattern["label"], [pattern["pattern"]])

@nlp_bp.route('/nlp', methods=['POST'])
def extract_entities():
    # Retrieve the extracted text from the session
    text = session.get('extracted_text', '')
    text = add_space_between_number_and_text(text)

    # Process the text with spaCy
    doc = nlp(text)

    # Apply the matcher
    matches = matcher(doc)
    extracted_entities = {}

    # Extract matched entities
    for match_id, start, end in matches:
        entity_label = nlp.vocab.strings[match_id]  # Get the entity label
        span = doc[start:end]  # Create a span for the matched entity

        # Store the matched entities as a list to handle multiple occurrences
        if entity_label in extracted_entities:
            extracted_entities[entity_label].append(span.text)
        else:
            extracted_entities[entity_label] = [span.text]

    # Save the extracted entities back into the session
    session['extracted_entities'] = extracted_entities

    return jsonify({"entities": extracted_entities, "text": text})


def add_space_between_number_and_text(text):
    # Add a space between numbers and letters where there isn't one already
    updated_text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)  # Add space after a number if followed by a letter
    updated_text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', updated_text)  # Add space before a number if preceded by a letter

    # Add a space after a colon if followed directly by a number or letter
    updated_text = re.sub(r'(:)(\S)', r'\1 \2', updated_text)

    # Add a space after a number if followed by a comma and another character
    updated_text = re.sub(r'(\d),(\S)', r'\1 , \2', updated_text)

    # Add a space before a comma if it directly follows a number
    updated_text = re.sub(r'(\d)(,)', r'\1 \2', updated_text)

    return updated_text

@nlp_bp.route('/nlp_check', methods=['GET'])
def nlp_check():
    # Retrieve the extracted entities from the session
    extracted_entities = session.get('extracted_entities', {})

    # Function to extract numeric value from the text
    def extract_value(text, unit=None):
        if unit:
            value = text.split(unit)[0].strip()
        else:
            value = text
        try:
            return float(re.findall(r"[-+]?\d*\.\d+|\d+", value)[0])  # Extract numeric value
        except IndexError:
            return 0  # Return 0 if no numeric value is found

    # Extract the relevant entities for decision-making
    initial_pth_value = extract_value(extracted_entities.get('PTH', ['0'])[0])  # Extracting the initial PTH value
    lab_result_pth_values = [
        extract_value(result) for result in extracted_entities.get('LAB_RESULT_DATE', [])
        if 'PTH' in result
    ]

    # Ensure we have a valid lab result PTH value
    lab_result_pth_value = lab_result_pth_values[0] if lab_result_pth_values else 0

    # Calculate the threshold based on the initial PTH value
    pth_threshold = initial_pth_value * 5 / 4

    # Determine if there's an increase in PTH level (alt_artisi_var_mi)
    alt_artisi_var_mi = lab_result_pth_value <= pth_threshold

    # Other extracted values (these are placeholders; adjust based on your needs)
    albumin_duzey = extract_value(extracted_entities.get('ALBUMIN', ['0'])[0], "g/L")
    fosfor_duzey = extract_value(extracted_entities.get('PHOSPHORUS', ['0'])[0], "mg/dL")
    calcium_duzey = extract_value(extracted_entities.get('CALCIUM', ['0'])[0], "mg/dL")

    # Determine patient type and treatment form based on extracted entities
    def get_value_from_list(entity_list, target_value):
        for item in entity_list:
            if target_value.lower() in item.lower():
                return True
        return False

        # Determine patient type (hasta_tipi) and treatment form (tedavi_formu)

    hasta_tipi = 'hemodiyaliz' if get_value_from_list(extracted_entities.get('TYPE', []),
                                                      'hemodiyaliz') else 'periton_diyalizi'
    tedavi_formu = 'parenteral' if get_value_from_list(extracted_entities.get('MEDICATION_FORM', []),
                                                       'parenteral') else 'oral'
    doktor_tipi = extracted_entities.get('DOCTOR', [''])[0]  # Normalize doctor type

    # Simulate lab result date; replace with actual logic
    lab_result_date = datetime.now()

    # Assuming it's the first report (this can be dynamically determined)
    ilk_rapor_mu = True

    # Use extracted entities in the decision-making function
    decision = parikalsitol_karar_al(
        pth_duzeyi=initial_pth_value,
        alt_artisi_var_mi=alt_artisi_var_mi,
        albumin_duzey=albumin_duzey,
        fosfor_duzey=fosfor_duzey,
        hasta_tipi=hasta_tipi,
        tedavi_formu=tedavi_formu,
        doktor_tipi=doktor_tipi,
        ilk_rapor_mu=ilk_rapor_mu,
        lab_result_date=lab_result_date
    )
    print("")
    return jsonify({
        "decision": decision,
        "extracted": extracted_entities,
        "is_pth_within_threshold": alt_artisi_var_mi,
        "pth_threshold": pth_threshold,
        "lab_result_pth_value": lab_result_pth_value
    })

def parikalsitol_karar_al(pth_duzeyi, alt_artisi_var_mi, albumin_duzey, fosfor_duzey, hasta_tipi, tedavi_formu, doktor_tipi, ilk_rapor_mu, lab_result_date):
    # Step 1: Check if lab results are within the last 3 months
    if lab_result_date < datetime.now() - timedelta(days=90):
        return f"Lab sonuçları 3 aydan daha eski, tedavi raporu geçerli değil. Lab tarihi: {lab_result_date.strftime('%d/%m/%Y')}"

    # Step 2: Check if it's a follow-up report
    if not ilk_rapor_mu:
        # Step 3: Check for treatment termination conditions
        if pth_duzeyi < 150 or albumin_duzey > 10.5 or fosfor_duzey > 6:
            return f"Parikalsitol tedavisi sonlandırılmalıdır. PTH: {pth_duzeyi}, Albümin: {albumin_duzey}, Fosfor: {fosfor_duzey}"
        # Step 4: If no termination condition is met, proceed with follow-up checks
        return f"Takip raporlarında tedavi koşulları kontrol edilmelidir. PTH: {pth_duzeyi}, Albümin: {albumin_duzey}, Fosfor: {fosfor_duzey}"

    # Step 5: Initial report checks (if it's the first report)
    if pth_duzeyi < 150 or albumin_duzey > 10.5 or fosfor_duzey > 6:
        return f"Parikalsitol tedavisi sonlandırılmalıdır. PTH: {pth_duzeyi}, Albümin: {albumin_duzey}, Fosfor: {fosfor_duzey}"
    if not (albumin_duzey < 10.2 and fosfor_duzey < 5.5):
        return f"Parikalsitol tedavisi başlatılamaz. Serum kalsiyum veya fosfor düzeyleri uygun değil. Albümin: {albumin_duzey}, Fosfor: {fosfor_duzey}"

    # Step 6: PTH Level-Based Decisions with Doctor and Patient Type Conditions
    if pth_duzeyi > 600 or (pth_duzeyi > 300 and alt_artisi_var_mi):
        # Additional checks based on patient type and doctor specialization
        if hasta_tipi == "hemodiyaliz" and tedavi_formu == "parenteral":
            if doktor_tipi.lower() in ["nefroloji", "iç hastalıkları", "çocuk sagligi", "diyaliz sertifikali"]:
                return f"1 Hemodiyaliz hastaları için parenteral Parikalsitol reçete edilebilir. PTH: {pth_duzeyi}, Albümin: {albumin_duzey}, Fosfor: {fosfor_duzey}, Doktor: {doktor_tipi}"
            elif doktor_tipi in ["İç hastalıkları", "İç Hastalıkları"]:
                return f"2 Hemodiyaliz hastaları için parenteral Parikalsitol reçete edilebilir. PTH: {pth_duzeyi}, Albümin: {albumin_duzey}, Fosfor: {fosfor_duzey}, Doktor: {doktor_tipi}"
            else:
                return f"3 Tedaviyi reçete eden doktor yetkili değil. Doktor: {doktor_tipi}, PTH: {pth_duzeyi}, Albümin: {albumin_duzey}, Fosfor: {fosfor_duzey}"
        elif hasta_tipi == "periton_diyalizi" and tedavi_formu == "oral":
            if doktor_tipi.lower() == "nefroloji":
                return f"4 Periton diyalizi hastaları için oral Parikalsitol reçete edilebilir. PTH: {pth_duzeyi}, Albümin: {albumin_duzey}, Fosfor: {fosfor_duzey}, Doktor: {doktor_tipi}"
            else:
                return f"5 Tedaviyi reçete eden doktor yetkili değil. Doktor: {doktor_tipi}, PTH: {pth_duzeyi}, Albümin: {albumin_duzey}, Fosfor: {fosfor_duzey}"
        else:
            return f"6 Tedavi koşulları sağlanıyor ancak hasta tipi veya tedavi formu uygun değil. Hasta Tipi: {hasta_tipi}, Tedavi Formu: {tedavi_formu}"
    else:
        return f"7 Parikalsitol tedavisi başlatılamaz. PTH {pth_duzeyi} koşulları sağlanmamış."

    # If none of the above conditions are met, default to this:
    return f"Tedaviye devam edilebilir; uygun rapor ve test sonuçları gerekmektedir. PTH: {pth_duzeyi}, Albümin: {albumin_duzey}, Fosfor: {fosfor_duzey}, Hasta Tipi: {hasta_tipi}, Tedavi Formu: {tedavi_formu}, Doktor: {doktor_tipi}"
