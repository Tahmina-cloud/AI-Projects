# -*- coding: utf-8 -*-
"""
Created on Sat Feb 15 20:25:47 2025

@author: Tahmina
"""

import os
import sys
import threading
import requests
import google.generativeai as genai
from flask import Flask, request, jsonify
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox
)

# ---------------------- SETUP GOOGLE GEMINI API ----------------------
API_KEY = "AIzaSyA8hGwFJ1NJFhDRCbrwV9vJtw1E0CPAaII" # Set your Google Gemini API key in the environment
if not API_KEY:
    raise ValueError("Error: GEMINI_API_KEY is not set. Please set it in your environment variables.")

genai.configure(api_key=API_KEY)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
)

def query_gemini(prompt):
    """Queries Gemini API with the given prompt and returns the response."""
    try:
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# ---------------------- FLASK BACKEND ----------------------
app = Flask(__name__)

@app.route("/generate_outline", methods=["POST"])
def generate_outline():
    data = request.json
    topic = data.get("topic")
    if not topic:
        return jsonify({"error": "Topic is required"}), 400
    
    prompt = f"Generate a structured research outline on the topic: {topic}. Include sections: Introduction, Background, Methods, Results, Conclusion."
    outline = query_gemini(prompt)
    return jsonify({"outline": outline})

@app.route("/generate_section", methods=["POST"])
def generate_section():
    data = request.json
    topic = data.get("topic")
    section = data.get("section")
    
    if not topic or not section:
        return jsonify({"error": "Both topic and section are required"}), 400
    
    prompt = f"Write a detailed {section} section for a research paper on: {topic}."
    section_content = query_gemini(prompt)
    return jsonify({"section": section, "content": section_content})

def run_flask():
    """Runs Flask in a separate thread to prevent UI freezing."""
    app.run(debug=False, threaded=True, port=5000)

# ---------------------- PyQt5 UI ----------------------
class TextGeneratorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Topic Input
        self.label_topic = QLabel("Enter Topic:")
        self.input_topic = QLineEdit()
        layout.addWidget(self.label_topic)
        layout.addWidget(self.input_topic)

        # Section Input
        self.label_section = QLabel("Enter Section (Only for Section Generation):")
        self.input_section = QLineEdit()
        layout.addWidget(self.label_section)
        layout.addWidget(self.input_section)

        # API Selection Dropdown
        self.dropdown_api = QComboBox()
        self.dropdown_api.addItems(["Generate Outline", "Generate Section"])
        layout.addWidget(self.dropdown_api)

        # Generate Button
        self.btn_generate = QPushButton("Generate")
        self.btn_generate.clicked.connect(self.generate_text)
        layout.addWidget(self.btn_generate)

        # Output Display
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        self.setLayout(layout)
        self.setWindowTitle("Text Generator UI")
        self.setGeometry(200, 200, 500, 400)

    def generate_text(self):
        """Sends request to Flask API and displays response."""
        topic = self.input_topic.text().strip()
        section = self.input_section.text().strip()
        api_choice = self.dropdown_api.currentText()

        if not topic:
            self.output_text.setText("Error: Topic is required!")
            return

        url = "http://127.0.0.1:5000/generate_outline" if api_choice == "Generate Outline" else "http://127.0.0.1:5000/generate_section"
        payload = {"topic": topic}

        if api_choice == "Generate Section":
            if not section:
                self.output_text.setText("Error: Section is required for Section Generation!")
                return
            payload["section"] = section

        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                text_output = result.get("outline", result.get("content", "No response received"))
                self.output_text.setText(text_output)
            else:
                self.output_text.setText(f"Error: {response.json().get('error', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            self.output_text.setText(f"Error connecting to API: {e}")

# ---------------------- Main Execution ----------------------
if __name__ == "__main__":
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Start PyQt5 UI
    app = QApplication(sys.argv)
    window = TextGeneratorUI()
    window.show()
    sys.exit(app.exec_())
