from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
from flask import Blueprint
import requests
import json

views = Blueprint('views', __name__)

@views.route('/')
def home():
    if not session.get('logged_in'):
         return redirect("/login");z
    return render_template('main.html', USERNAME=session["username"]);

SENTIMENT_API_URL = "https://bbtflv6yqf.execute-api.us-east-1.amazonaws.com/Initial/sentimental-analysis"

@views.route('/analyze', methods=['POST'])
def analyze():
    # if not session.get('logged_in'):
    #     return redirect(url_for('login'))

    text = request.form['text']

    # Call the sentiment analysis API using a GET request
    response = requests.get(SENTIMENT_API_URL, params={'query': text})

    if response.status_code == 200:
        response_text = response.text  # Get the response as a string

        # Extract the last word of the sentiment label as the default value
        sentiment_words = response_text.split(':')[-1].strip().split()
        last_word = sentiment_words[-1].rstrip('"')

        # Process and display the last word of the sentiment label
        return render_template('output.html', sentiment=last_word)
    else:
        return render_template('output.html', sentiment="Failed to analyze sentiment")
