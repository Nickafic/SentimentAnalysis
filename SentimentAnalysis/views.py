from flask import Flask, render_template, request, redirect, url_for, session, Blueprint, jsonify
import requests, json, boto3

views = Blueprint('views', __name__)
dynamodb = boto3.resource('dynamodb')
senttable = dynamodb.Table('sentiment')
EXTENSIONS = {'txt', 'csv'}


@views.route('/')
def home():
    if not session.get('logged_in'):
         return redirect("/login")
    return render_template('main.html', USERNAME=session["username"], sentiment=None)

SENTIMENT_API_URL = "https://bbtflv6yqf.execute-api.us-east-1.amazonaws.com/Initial/sentimental-analysis"

@views.route('/account')
def account():
    if not session.get('logged_in'):
        return redirect("/login")
    return render_template('account.html')

# Route to get sentiment history for a specific page
@views.route('/get_sentiment_history', methods=['GET'])
def get_sentiment_history():
    response = senttable.get_item(Key={'username': session['username']})
    item = response.get('Item')
    sentiments_list = item['sentiments']

    page = int(request.args.get('page', 1))
    items_per_page = 10  # Adjust as needed
    start_index = (page-1) * 10
    end_index = page * 10 - 1


    page_entries = sentiments_list[start_index:end_index]
    has_more_pages = end_index < len(sentiments_list)

    response_data = {
        "entries": page_entries,
        "page": page,
        "hasMorePages": has_more_pages,
    }

    return jsonify(response_data)


@views.route('/analyzeText', methods=['POST'])
def analyzeText():
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

        response = senttable.get_item(Key={'username': session['username']})
        item = response.get('Item')
        if item and 'sentiments' in item:
            sentiments_list = item['sentiments']

            if len(sentiments_list) > 50:
                # Remove the last pair in the list
                sentiments_list.pop()

            # Add the new sentiment-text pair to the front of the list
            new_pair = {'sentiment': last_word, 'text': text}
            sentiments_list.insert(0, new_pair)

            # Update the item in the table
            senttable.update_item(
                Key={'username': session['username']},
                UpdateExpression='SET sentiments = :s',
                ExpressionAttributeValues={':s': sentiments_list}
            )

        # Process and display the last word of the sentiment label
        return render_template('main.html', USERNAME=session["username"], sentiment=last_word, input_text=text)
    else:
        return render_template('main.html', USERNAME=session["username"], sentiment="Failed to analyze sentiment", input_text=text)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in EXTENSIONS

@views.route('/analyzeFile', methods=['POST'])
def analyzeFile():
        
        if 'inputFile' not in request.files:
            return render_template('main.html', USERNAME=session["username"], sentiment="File Failed To Upload")
            
            """ Process File"""

        return redirect("/login", USERNAME=session["username"], sentiment="WIP")

            

        

        


