from flask import Flask, request, jsonify, render_template

import csv
from datetime import datetime
import os
import re

app = Flask(__name__)

user_context = {}
user_logs = {}

# create headers for csv file
if not os.path.exists("patient_log.csv"):
    with open("patient_log.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "User_id", "Division", "NY/CT/NJ", "Email", "Phone"])


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

# Hard code for AI BOT
@app.route('/api/intake', methods=['POST'])
def rule_based_chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Message is required"}), 400
    user_message = data["message"].strip().lower()
    user_id = request.remote_addr  # Simple unique ID per user (can improve later)

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    # Default fallback
    reply = "I'm not sure how to respond to that. Please select one of the provided options."

    # Greeting
    if user_message.lower().strip() in ["hello", "start"]:
        reply = """Hello, welcome to Columbia Neurosurgery’s AI assistant. How may I help you today?"""

    # Scheduling Flow
    elif user_message.lower().strip() in ["schedule appointment"]:
        reply = """I can take care of that for you. First, what is your issue?"""

    elif user_message.lower().strip() in ["tumor", "stroke", "spine", "pediatric", "other"]:
        user_context.setdefault(user_id, {})["reason"] = user_message.lower().strip()
        reply = """Thank you for the information. Are you located in the tristate area (NY, NJ, or CT)?  """

    elif user_message.lower().strip() in ["yes"]:
        user_context.setdefault(user_id, {})["location"] = user_message.capitalize()
        reply = "Thank you. How would you like us to contact you?"

    elif user_message.lower().strip() in ["no"]:
        user_context.setdefault(user_id, {})["location"] = user_message.capitalize()
        reply = "Thank you. How would you like us to contact you?"

    # log email or phone
    elif user_message.lower().strip() in ["email"]:
        reply = """Please provide your email."""

    elif user_message.lower().strip() in ["phone"]:
        reply = """Please provide your phone."""

    elif user_message.lower().strip() in ["both"]:
        reply = """Please provide your email and phone number."""

    elif "@" in user_message or re.fullmatch(r"\d{7,15}", user_message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if user_id not in user_logs:
            user_logs[user_id] = {}

        if "@" in user_message and re.search(r"\d{7,15}", user_message):
            user_logs[user_id]["email"] = user_message
            user_logs[user_id]["phone"] = user_message
        elif "@" in user_message:
            user_logs[user_id]["email"] = user_message
        else:
            user_logs[user_id]["phone"] = user_message

        user_logs[user_id]["timestamp"] = timestamp

        # 🔁 Get other context values (if they exist)
        reason = user_context.get(user_id, {}).get("reason", "")
        location = user_context.get(user_id, {}).get("location", "")
        email = user_logs[user_id].get("email", "")
        phone = user_logs[user_id].get("phone", "")

        # 📝 Append to CSV file
        with open("patient_log.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                timestamp,               # Timestamp
                user_id,                 # User_id
                reason,                  # Division
                location,                # NY/CT/NJ
                email,                   # Email
                phone                    # Phone
                ])

        print("📥 Logged to patient_log.csv:", [timestamp, user_id, reason, location, email, phone])

        reply = "We appreciate your interest in Columbia Neurosurgery. A member of our team will contact you shortly. Have a great day!"


    # Imaging Flow
    elif user_message.lower().strip() in ["imaging"]:
        reply = """I need some more information before I can assist you. Do you: """

    elif user_message.lower().strip() in ["have imaging"]:
        reply = """Thank you for the information. Are you located in the tristate area (NY, NJ, or CT)?"""

    elif user_message.lower().strip() in ["need imaging"]:
        reply = """Since we prefer imaging before an appointment, let's connect you with an imaging service. Are you located in the tristate area (NY, NJ, or CT)?"""

    elif user_message.lower().strip() in ["yes, i do"]:
        reply = """Below are options for scheduling imaging prior to your appointment with Columbia Neurosurgery:

    1) CUIMC/Neurological Institute MRI Center  
    📍 710 W 168th St, New York, NY 10032  
    📞 (212) 326-8518

    2) ColumbiaDoctors/NewYork-Presbyterian Imaging – Hudson Yards  
    📍 504 W 35th St, New York, NY 10001  
    📞 (212) 746-6000

    3) ColumbiaDoctors/NewYork-Presbyterian Imaging – Scarsdale  
    📍 703 White Plains Rd, Scarsdale, NY 10583  
    📞 (212) 326-8518"""

    elif user_message == "2" or ("no, i" in user_message.lower()):
        reply = "Please provide your email and/or phone and a member of our team will contact you shortly."

    # Doctors Flow
    elif user_message in ["find doctors"]:
        reply = """Thank you for your interest in our providers. Is there a specialty you would like to learn more about?"""

    elif user_message in ["spine surgeons"]:
        reply = 'For more information click <a href="https://www.neurosurgery.columbia.edu/patient-care/specialties/spine-disorders">here.</a>'

    elif user_message in ["tumor surgeons"]:
        reply = 'For more information click <a href="https://www.neurosurgery.columbia.edu/about-us/our-divisions/neuro-oncology" target="_blank">here.</a>'

    elif user_message in ["pain surgeons"]:
        reply = 'For more information click <a href="https://www.neurosurgery.columbia.edu/about-us/our-divisions/functional" target="_blank">here./a>'

    elif user_message in ["pediatric surgeons"]:
        reply = 'For more information click <a href="https://www.neurosurgery.columbia.edu/about-us/our-divisions/pediatric" target="_blank">here.</a>'

    elif user_message in ["general"]:
        reply = 'For more information click <a href="https://www.neurosurgery.columbia.edu/patient-care/specialties" target="_blank">here.</a>'

    # Other inquiries
    elif user_message == "4" or ("inquires" in user_message):
        reply = "Thank you for your interest. Please provide your email and/or phone number and a member of our team will contact you shortly."

    return jsonify({
        "userMessage": { "content": user_message, "sender": "user" },
        "assistantMessage": { "content": reply, "sender": "ai" }
    })

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
