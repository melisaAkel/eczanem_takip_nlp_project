# 💊 Pharmacy Inventory & Prescription Validation System
Welcome to the Pharmacy Inventory & NLP Prescription System! This project is designed to streamline pharmacy operations by integrating efficient inventory management with advanced prescription validation using NLP techniques.

## 🚀 Project Overview
This system helps pharmacies manage their stock while ensuring that prescribed medications align with predefined medical guidelines. The key features include:

### 📦 Inventory Management: Add, update, search, and filter medicines with ease.
### 🔍 Barcode Scanning: Quickly search for medicines using barcodes via the integrated ZXing library.
### 📊 Stock Management: Filter, paginate, and manage stock efficiently through a user-friendly interface.
### 🔗 Supplier Integration: Dynamically select suppliers using a dropdown integrated with an API.
### 🤖 NLP Prescription Validation: Process Turkish text using NLP and decision trees to validate prescriptions automatically.
### 🔬 Decision Support System: The backend analyzes medical data and guidelines to provide insights and recommendations.
### ⚙️ Technologies Used
**Backend**: Flask, Python, MySQL
**Frontend**: HTML, Bootstrap, JavaScript
**NLP**: spaCy, custom decision tree logic
**Additional Libraries**: ZXing for barcode scanning, Flask-CORS, pandas, opencv-python
## 📂 Project Structure
**app/**: Contains the main application code.
**templates/**: Frontend HTML files.
**static/**: CSS, JS, and images.
**routes/**: Backend routes for stock management, sales, and prescription validation.
**nlp/**: Custom NLP logic for extracting and validating prescription information.
## 📂 Project Structure

- **app/**: Contains the main application code.
- **templates/**: Frontend HTML files.
- **static/**: CSS, JS, and images.
- **routes/**: Backend routes for stock management, sales, and prescription validation.
- **nlp/**: Custom NLP logic for extracting and validating prescription information.

## 🛠️ Key Features

### Inventory Management:

- Add, delete, and update stock.
- Real-time filtering and searching with pagination.

### NLP Prescription Validation:

- Automatically analyze prescription text.
- Ensure compliance with medical guidelines using decision trees.

### Barcode Scanning:

- Quickly find medicines with barcode scanning using the ZXing library.

### Dynamic Supplier Selection:

- Integrate supplier data from an API for seamless stock management.

### User Interface:

- Clean and intuitive design with Bootstrap.
- Responsive layout for efficient use on various devices.

## 🚀 Getting Started

Clone the repository:

```bash
git clone https://github.com/your-username/pharmacy-inventory-nlp.git
Install the dependencies:

bash
Kodu kopyala
pip install -r requirements.txt
Run the application:

bash
Kodu kopyala
python app.py
🧪 Testing
Use the sample data provided in the /data folder for testing stock and prescription validation. The system supports real-time testing of prescription validation via the /nlp endpoint.

📜 License
This project is licensed under the MIT License.
