from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
import requests

auth = Blueprint('auth', __name__)

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

        ## Account Validation Will Be Added HERE
        # MOCK ALLOWS ALL LOGINS
        if(True):
            session['username'] = username
            session['logged_in'] = True
        
        #redirect to Main page with user's name on top of main page.
        return redirect(url_for('views.home'))
    else:
        if( (session.get('logged_in') != None) & (session.get('logged_in') == True)): #if logged in session redirect to home
            return redirect(url_for('views.home'))
        else:
        #DEFAULT PATH: head to login page.
            return render_template('login.html')

@auth.route('/logout')
def logout():
    ## ON LOGOUT REMOVE SESSION DATA
    session["logged_in"] = False
    session["username"] = ""

    return redirect(url_for('auth.login'))

"""
    DEBUG GO BACK. NOT FINAL
"""
@auth.route('/signup')
def signup():
    return "<p>signup</p><form method='GET', action='/login'><input type='submit' value='GO BACK'></form>"

@auth.route('/recovery')
def accountRecover():
    return "<p>recovery</p><form method='GET', action='/login'><input type='submit' value='GO BACK'></form>"