from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
import requests, boto3, bcrypt

from boto3.dynamodb.types import TypeDeserializer 

auth = Blueprint('auth', __name__)
dynamodb = boto3.resource('dynamodb')
usertable = dynamodb.Table('userdata')
senttable = dynamodb.Table('sentiment')

"""
Login Processing
"""
#Added 'Post' method to allowable methods.
@auth.route('/login', methods=['POST', 'GET'])
def login():

    #If request is post process form data.
    if request.method == "POST":
        ##Store form data
        username = request.form['username']
        password = request.form['password']

        response = usertable.get_item(Key={'username': username})
        if 'Item' in response:
            stored_hashed_password = response['Item']['password']
            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                session['username'] = username
                session['logged_in'] = True
                #redirect to Main page with user's name on top of main page.
                
                return redirect(url_for('views.home'))
            else:
                return render_template('login.html', error='Incorrect username or password. Please try again.')
        else:
            return render_template('login.html', error='User does not exist. Please sign up first.')
    else:
        if( (session.get('logged_in') != None) & (session.get('logged_in') == True)): #if logged in session redirect to home
            return redirect(url_for('views.home'))
        else:
        #DEFAULT PATH: head to login page.
            return render_template('login.html', error=None)

@auth.route('/logout')
def logout():
    ## ON LOGOUT REMOVE SESSION DATA
    session["logged_in"] = False
    session["username"] = ""

    return redirect(url_for('auth.login'))

"""
    DEBUG GO BACK. NOT FINAL
"""
@auth.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        email = request.form['email'].lower()
        questionOne = request.form['securityQuestion1']
        answerOne = request.form['answer1']
        questionTwo = request.form['securityQuestion2']
        answerTwo = request.form['answer2']
        
        response = usertable.query(
            KeyConditionExpression='username = :username',
            ExpressionAttributeValues={':username': username}
        )
        if len(response['Items']) == 0:
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt) #Case Sensitive
            security_answer1 = bcrypt.hashpw(answerOne.lower().encode('utf-8'), salt) #ans is lowercased
            security_answer2 = bcrypt.hashpw(answerTwo.lower().encode('utf-8'), salt) #ans is lowercased
            usertable.put_item(
                Item={
                    'username': username,
                    'email': email, # email is lowercased
                    'password': hashed_password.decode('utf-8'),
                    'securityQuestions': {
                        questionOne: security_answer1.decode('utf-8'),
                        questionTwo: security_answer2.decode('utf-8')
                    }
                    }
            )
            senttable.put_item(
                Item={
                    'username': username,
                    'sentiments': []
                }
            )
            return render_template('login.html')
        else:
            return render_template('signup.html', username=False)
    else:
        return render_template('signup.html', username=True)

@auth.route('/recovery', methods=['POST', 'GET'])
def accountRecover():
    if request.method == "POST":

        uName = request.form['uname']
        eMail = request.form['email'].lower()
        SeqQuestions = []
        try:
            response = usertable.get_item(Key={'username':uName})
            print(response)

            if "Item" in response:

                if( not (eMail == response['Item']['email'])):
                    return render_template('accountRecovery.html', ERRORMESSAGE="Account NOT Found")
                
                SecurityDictKeys = response['Item']['securityQuestions'].keys()
                for key in SecurityDictKeys:
                    SeqQuestions.append(key)
                return render_template('accountRecoverySeq.html', UNAME=uName, EMAIL=eMail, Q=SeqQuestions)

            else:
                return render_template('accountRecovery.html', ERRORMESSAGE="Account NOT Found")
        except:
            return render_template('accountRecovery.html', ERRORMESSAGE="No Server Responce")
    else:
        return render_template('accountRecovery.html')

@auth.route('/recoverySeq', methods=['POST'])
def accountRecoverSeq():
    ##If Security Q's Are answered correctly allow password reset
    ans = []
    ans.append( request.form['answer1'].lower() )
    ans.append( request.form['answer2'].lower() )
    uName = request.form['uname']
    eMail = request.form['email']
    pword = request.form['password']
    pwordconf = request.form['passwordconf']

    try:
        #GET user info
        response = usertable.get_item(Key={'username': uName})
        #Handle response
        if 'Item' in  response: 
            if( not (eMail == response['Item']['email'])):
                    return render_template('accountRecovery.html', ERRORMESSAGE="Server Error. Account NOT Found.")
            #Parse Res
            sQuestionsObject = response.get('Item', {}).get('securityQuestions',{})
            sQKeysList = []
            sQList = []
            for key, value, in sQuestionsObject.items():
                sQKeysList.append(key)
                sQList.append(value)
            #Conf New Pass Match
            if(pword != pwordconf):
                return render_template('accountRecoverySeq.html', UNAME=uName, EMAIL=eMail, Q=sQKeysList, ERRORMESSAGE="Passwords do NOT match.")

            #Check Sec Questions
            if( bcrypt.checkpw(ans[0].encode('utf-8'), sQList[0].encode('utf-8')) and bcrypt.checkpw(ans[1].encode('utf-8'), sQList[1].encode('utf-8'))  ):
                #PASSED QUESTIONS
    
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(pword.encode('utf-8'), salt) 

                response = usertable.update_item(
                    Key={
                        'username': uName
                    },
                    UpdateExpression="SET password = :password",
                    ExpressionAttributeValues={
                        ':password': hashed_password.decode('utf-8')
                    },
                    ReturnValues="UPDATED_NEW"
                )

                print("UpdateItem succeeded:", response)

                return render_template('accountRecoverySuccess.html')
            
            return render_template('accountRecoverySeq.html', UNAME=uName, EMAIL=eMail, Q=sQKeysList, ERRORMESSAGE="Failed Secutiy Questions")

        else: # Should be Unreachable
            return render_template('accountRecovery.html', ERRORMESSAGE="Server Error. No Account.")
    except ConnectionError:
        return render_template('accountRecovery.html', ERRORMESSAGE="Connection Error. No Response.")