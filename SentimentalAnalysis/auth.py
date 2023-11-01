from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
import requests

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/logout')
def logout():
    return redirect(url_for('auth.login'))

@auth.route('/signup')
def signup():
    return "<p>signup</p>"