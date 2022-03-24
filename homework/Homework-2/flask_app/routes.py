# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from flask import current_app as app
from flask import render_template, redirect, request, session
from .utils.database.database  import database
from werkzeug.datastructures import ImmutableMultiDict
from pprint import pprint
import json
import random
db = database()

@app.route('/')
def root():
	return redirect('/home')

@app.route('/home')
def home():
	return render_template('home.html')

@app.route('/projects')
def projects():
	return render_template('projects.html')

@app.route('/piano')
def piano():
	return render_template('piano.html')

@app.route('/resume')
def resume():
	resume_data = db.getResumeData()
	pprint(resume_data)
	return render_template('resume.html', resume_data = resume_data)


@app.route('/processfeedback', methods = ['POST'])
def processfeedback():

	feedback = request.form
	header = ["name","email","comment"]
	data = []
	# gather the data from the form
	data.append(feedback['name'])
	data.append(feedback['email'])
	data.append(feedback['feedback_comment'])
	# insert it into the database table
	db.insertRows('feedback',header,data)
	feedback_select = "SELECT * FROM feedback"
	pprint(db.query(feedback_select))
	# grabs the information from the feedback table
	feedback_data = db.query(feedback_select)
	# this redirect prevents page refreshs from inserting the same post request more than one time
	return redirect('/refreshcheck')

# used to stop post from sending more than once when page is refreshed
@app.route('/refreshcheck')
def refreshcheck():
	# get the information and render it in the feedback html
	feedback_select = "SELECT * FROM feedback"
	feedback_data = db.query(feedback_select)
	return render_template('processfeedback.html',feedback_data = feedback_data)
