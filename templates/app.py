from ai_chatbot import ask_gpt
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import numpy as np
import pandas as pd
import pickle
import re
from chatbot import find_best_match  # Import the chatbot function

app = Flask(__name__)
app.secret_key = '2181'  # Replace with a real secret key in production

# Your existing Flask routes and functions here...

# Fixed chat route to properly use the chatbot function
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").lower()

    # Get response using the imported function from chatbot.py
    response = find_best_match(user_message)

    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True)

