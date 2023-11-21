from flask import Flask, render_template, request, redirect, url_for, session, Blueprint, jsonify

from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

import csv, io, base64
import requests, json, boto3

views = Blueprint('views', __name__)
dynamodb = boto3.resource('dynamodb')
senttable = dynamodb.Table('sentiment')

#Constansts
VALID_EXTENSIONS = {'txt', 'csv'}
SENTIMENT_API_URL = "https://bbtflv6yqf.execute-api.us-east-1.amazonaws.com/Initial/sentimental-analysis"

@views.route('/')
def home():
    if not session.get('logged_in'):
         return redirect("/login")
    return render_template('main.html', USERNAME=session["username"], sentiment=None)


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

def finishFileProcess(identifiers, messages):
    JSONData = json.dumps(messages)
    B64Data = base64.b64encode( JSONData.encode() ).decode()
    APIPayload =  {
        'queryType' : 'multiple',
        'query' : B64Data
    }

    response = requests.get(SENTIMENT_API_URL, params=APIPayload)
    
    if response.status_code == 200:
        resJSONData = response.json()['body']
        resJSONData = resJSONData.split('\n', 1)[1]
        splitJSONData = resJSONData.split('\n')
        splitJSONData.pop()
        
        sentTable = []
        i = 0
        for splitString in splitJSONData:
            activeSplit = splitString.rsplit(',',1)
            nextEntry = {'index':i, 'indentifier':identifiers[i], 'query':activeSplit[0], 'result':activeSplit[1]}
            i = i+1
            sentTable.append(nextEntry)

        return render_template('main.html', USERNAME=session["username"], sentimentTable=sentTable )

    else:
        print("Failed. CODE: ", response.status_code) 
        return

@views.route('/analyzeFile', methods=['POST'])
def analyzeFile():
    try: 
        #ERROR Checks
        if 'inputFile' not in request.files:
            return render_template('main.html', USERNAME=session["username"], ERRORMESSAGE="File Failed To Upload")
        activeFile = request.files['inputFile']
        activeFileName = secure_filename(activeFile.filename)
        #EXISTENCE CHECK
        if activeFileName == '':
            return render_template('main.html', USERNAME=session["username"], ERRORMESSAGE="File Has No Name")
        #EXTENSION CHECK
        fileExtention = activeFileName.rsplit('.', 1)[1].lower()
        if( not ( ('.' in activeFileName) and (fileExtention in VALID_EXTENSIONS) ) ):
            return render_template('main.html', USERNAME=session["username"], ERRORMESSAGE="File Extension is not allowed")
        
        ##VARS
        messages = []
        identifiers = []
        fileContent = activeFile.read().decode('utf-8')
        
        if(fileExtention == 'txt'): #TXT
            lines = fileContent.split('\r\n')
            for line in lines:
                
                if not line.strip():
                    continue  # Skip empty lines

                activeSplits = line.split(',',1)
                if len(activeSplits) != 2:
                    msg = "txt is not formatted correctly. Missing ',' for '" + line + "'"
                    return render_template('main.html', USERNAME=session["username"], ERRORMESSAGE=msg )
                
                identifiers.append(activeSplits[0])

                if activeSplits[1].count('"') != 2:
                    msg = "txt is not formatted correctly. Missing '\"' for '" + line + "'"
                    return render_template('main.html', USERNAME=session["username"], ERRORMESSAGE=msg )

                messages.append(activeSplits[1].strip('"'))

        #END IF
        elif (fileExtention == 'csv'): #CSV
            csvRecords = []
            for row in csv.reader(io.StringIO(fileContent)):
                for word in row:
                    if not word:
                        return render_template('main.html', USERNAME=session["username"], ERRORMESSAGE="CSV formatting issue. Missing a value")
                csvRecords.append(row)
            
            if( len(csvRecords) < 1 ):
                return render_template('main.html', USERNAME=session["username"], ERRORMESSAGE="CSV formatting issue. File is empty")

            if( len(csvRecords[0]) > 2 ):
                return render_template('main.html', USERNAME=session["username"], ERRORMESSAGE="CSV formatting issue. Only use two columns")

            for rec in csvRecords:
                identifier = rec[0]
                message = rec[1]
                messages.append(message)
                identifiers.append(identifier)
        #ENDIF

        else: ##FAILED STATE SHOULD BE UNREACHABLE
            return render_template('main.html', USERNAME=session["username"], ERRORMESSAGE="File UPLOADED file type not valid. Unknow Error Occurred")
        
        if( len(messages) < 1 or len(identifiers) < 1):
            return render_template('main.html', USERNAME=session["username"], ERRORMESSAGE="File was empty")

        return finishFileProcess(identifiers, messages)
    
    except RequestEntityTooLarge:
        #abort(413, 'File size exceeds the allowed limit')
        #MAX FILE SIZE CHECK
        return render_template('main.html', USERNAME=session["username"], ERRORMESSAGE="File size exceeds the allowed limit")



        


