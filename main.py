from flask import Flask, request, jsonify, render_template
from gpt_utils import ask_gpt
import os

app = Flask(__name__)

# Root route – serves the chatbot + intake form page
@app.route('/')
def homepage():
    return render_template("home.html")

# Form page route
@app.route('/form')
def form_page():
    return render_template("form.html")

# Route for appointment availability (static for now)
@app.route('/api/availability', methods=['GET'])
def get_availability():
    availability = [
        {"date": "2025-08-08", "time": "09:00 AM"},
        {"date": "2025-08-08", "time": "11:00 AM"},
        {"date": "2025-08-09", "time": "02:00 PM"}
    ]
    return jsonify({"available_slots": availability})

# GPT-powered chatbot intake logic
@app.route('/api/intake', methods=['POST'])
def intake_questions():
    data = request.json
    response = {}

    if 'urgency' not in data:
        prompt = "Ask the patient how urgent this medical issue is."
        response['question'] = ask_gpt(prompt)
    elif 'imaging' not in data:
        prompt = "Ask if the patient already has imaging like an MRI or CT scan."
        response['question'] = ask_gpt(prompt)
    elif 'location' not in data:
        prompt = "Ask the patient where they are located."
        response['question'] = ask_gpt(prompt)
    else:
        response['message'] = "Thank you — your request has been received. A coordinator will contact you shortly."

    return jsonify(response)

# (Optional) handle form submission (e.g., save to file, send email)
@app.route('/submit-form', methods=['POST'])
def submit_form():
    # You can extract form fields like this:
    email = request.form.get("contact")
    phone = request.form.get("phone")
    age = request.form.get("age_21_plus")
    condition = request.form.get("condition")
    appointment_type = request.form.get("appointment_type")
    other_info = request.form.get("other_info")

    # Do something with the data (log, save, route, etc.)
    print("📥 Form submitted:", email, phone, condition, appointment_type)

    return "✅ Form submitted successfully!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
