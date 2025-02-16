# -*- coding: utf-8 -*-
"""
Created on Sat Feb 15 21:31:32 2025

@author: tahmi
"""

from flask import Flask, request, jsonify
import requests
import PySimpleGUI as sg

app = Flask(__name__)

# Google Gemini API setup (replace 'YOUR_API_KEY' with your actual API key)
API_KEY = "AIzaSyA8hGwFJ1NJFhDRCbrwV9vJtw1E0CPAaII"
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateText"
import google.generativeai as genai

# Set up Gemini API key (replace with actual key)
genai.configure(api_key="AIzaSyA8hGwFJ1NJFhDRCbrwV9vJtw1E0CPAaII")  # Replace or use os.environ["GEMINI_API_KEY"]

# Model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Create the model
model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config,
)

def query_gemini(prompt):
    """ Sends a query to the Google Gemini API and returns the response. """
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(prompt)
    return response.text if response else "No response received"

def create_ui():
    """ Creates a PySimpleGUI-based UI for the study helper app. """
    sg.theme('LightBlue')
    
    layout = [
        [sg.Text('Enter text for processing:')],
        [sg.Multiline(size=(60, 10), key='-TEXT-')],
        [sg.Button('Summarize'), sg.Button('Generate Flashcards'), sg.Button('Create Quiz')],
        [sg.Text('Output:', size=(60, 1))],
        [sg.Multiline(size=(60, 10), key='-OUTPUT-', disabled=True)],
        [sg.Button('Exit')]
    ]
    
    window = sg.Window('AI Study Helper', layout)
    
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Exit':
            break
        
        text = values['-TEXT-'].strip()
        if not text:
            window['-OUTPUT-'].update("Please enter text before proceeding.")
            continue

        if event == 'Summarize':
            prompt = f"Summarize the following passage: {text}"
        elif event == 'Generate Flashcards':
            prompt = f"Generate key concept flashcards (question-answer pairs) from this text: {text}"
        elif event == 'Create Quiz':
            prompt = f"Create a short multiple-choice quiz from this passage: {text}"
        else:
            continue
        
        response = query_gemini(prompt)
        window['-OUTPUT-'].update(response)
    
    window.close()

if __name__ == '__main__':
    create_ui()
