from flask import current_app as app
from flask import render_template, redirect, request, session, url_for, copy_current_request_context
from .utils.database.database import database
from werkzeug.datastructures import ImmutableMultiDict
from pprint import pprint
import json
import random
import functools
import requests
from datetime import date

# https://rapidapi.com/dpventures/api/wordsapi/ used for random word and word verification
db = database()
random_word_url = "https://wordsapiv1.p.rapidapi.com/words/"

querystring = {"random": "true"}

random_word_headers = {
    "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com",
    "X-RapidAPI-Key": "cee9233acbmsh036a78316b0472ep189799jsn990fab598f95"
}
# used for word validation

word_validate_headers = {
    "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com",
    "X-RapidAPI-Key": "cee9233acbmsh036a78316b0472ep189799jsn990fab598f95"
}


#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)

    return secure_function


def getUser():
    return session['email'] if 'email' in session else 'Unknown'


# login route
@app.route('/login')
def login():
    return render_template('login.html', user=getUser())


# account creation page route
@app.route("/createaccount")
def createaccount():
    return render_template('createaccount.html', user=getUser())


@app.route('/logout')
def logout():
    session.pop('email', default=None)
    return redirect('/')


# handles the creation of the accounts
@app.route('/processcreation', methods=["POST", "GET"])
def processcreation():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))

    return json.dumps(db.createUser(form_fields['email'], form_fields['password'], 'guest'))


# handles the logins for an account
@app.route('/processlogin', methods=["POST", "GET"])
def processlogin():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))

    # check the authorization status
    authorized = db.authenticate(form_fields['email'], form_fields['password'])
    # if the authentication was sucessful, store the email in the session
    if authorized["Success"] == 1:
        session['email'] = form_fields['email']
    return json.dumps(authorized)


#######################################################################################
# OTHER
#######################################################################################
@app.route('/')
def root():
    return redirect('/home')


@app.route('/home')
def home():
    return render_template('home.html', user=getUser())


@app.route('/projects')
def projects():
    return render_template('projects.html', user=getUser())


@app.route('/piano')
def piano():
    return render_template('piano.html', user=getUser())


@app.route('/resume')
def resume():
    resume_data = db.getResumeData()

    return render_template('resume.html', resume_data=resume_data, user=getUser())


#######################################################################################
# # Games related routes
#######################################################################################
@app.route("/Games")
def games():
    return render_template('games_main.html')


#######################################################################################
# # End of Game related routes
#######################################################################################
#######################################################################################
# # flashcard related routes
#######################################################################################
def getUserId():
    user_id = db.retrieveusers(getUser())
    return user_id


@app.route("/Flashcard")
@login_required
def flash():
    # removes any stored deck_id
    if "deck_id" in session:
        session.pop('deck_id', default=None)

    user_id = getUserId()
    decks = db.retrievedecks(user_id)
    counts = dict()
    for x in decks:
        cards = db.retrieveCards(x["deck_id"])

        counts[x["deck_id"]] = len(cards)

    return render_template('flash.html', user=getUser(), decks=decks, deck_counts=counts)


@app.route("/Study")
@login_required
def study():
    user_id = getUserId()
    decks = db.retrievedecks(user_id)
    current_deck = 0
    for i in decks:
        if i["deck_id"] == session["deck_id"]:
            current_deck = i

    return render_template('study.html', user=getUser(), current_deck=current_deck)


@app.route("/NewDeck", methods=["POST", "GET"])
@login_required
def newdeck():
    return render_template('newdeck.html', user=getUser())


# grabs the correct deck information and brings the user inside the deck to view the words, add more words,
# and start a study session
@app.route("/Deck", methods=["POST", "GET"])
def deck():
    user_id = getUserId()
    decks = db.retrievedecks(user_id)
    current_deck = 0
    for i in decks:
        if i["deck_id"] == session["deck_id"]:
            current_deck = i
    cards = db.retrieveCards(session["deck_id"])

    count = len(cards)

    return render_template('innerdeck.html', user=getUser(), current_deck=current_deck, cards=cards, count=count)


@app.route("/retrievecards", methods=["POST", "GET"])
def retrievecards():
    cards = db.retrieveCards(session["deck_id"])
    return json.dumps(cards)


@app.route("/processdeck", methods=["POST", "GET"])
def processdeck():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    db.createdeck(getUser(), form_fields["deck_name"], form_fields["language_1"], form_fields["language_2"],
                  form_fields["access"])
    return redirect('Flashcard')


@app.route("/processwordadd", methods=["POST", "GET"])
def processwordadd():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))

    user_id = getUserId()
    decks = db.retrievedecks(user_id)
    current_deck = 0
    for i in decks:
        if i["deck_id"] == session["deck_id"]:
            current_deck = i

    db.addcard(getUser(), current_deck["name"], form_fields["front"], form_fields["back"], session["deck_id"])
    return redirect('Deck')


@app.route("/processdeckclick", methods=["POST", "GET"])
def processdeckclick():
    form_dict = request.form.to_dict()
    # store the selected deck id
    session["deck_id"] = int(form_dict["number"])
    return {'Success': 1}


# deletes the word from the dictionary
@app.route("/processworddelete", methods=["POST", "GET"])
def processworddelete():
    form_dict = request.form.to_dict()

    db.deleteCard(int(form_dict['number']))
    return {'Success': 1}


#######################################################################################
# # wordle related routes
#######################################################################################

@app.route('/wordle')
@login_required
def wordle():
    current_day = date.today().strftime("%m/%d/%Y")

    # when the user goes to the wordle web page, check if a word of the day has been selected
    used = db.checkDate(current_day)
    # if used is 0 then the current date was not found in the database
    if used == 0:
        # this makes sure that the random word is less than or equal to 10 characters
        while True:
            #  get the word of the day to store
            response = requests.request("GET", random_word_url, headers=random_word_headers, params=querystring)
            word_of_the_day = ""
            start = False
            # this finds the substring word in the response list so that we can grab the randomly generated word
            index = response.text.find("word")
            while (True):
                if response.text[index] == ",":
                    break
                if start == True and response.text[index] != '"':
                    word_of_the_day += response.text[index]
                if response.text[index] == ":":
                    start = True
                index += 1
            # limit the word size to 10 or less characters
            if len(word_of_the_day) <= 6 and len(word_of_the_day) >= 4 and word_of_the_day.isalpha() == True:
                db.storeNewWord(current_day, word_of_the_day)
                break
    # pass the length of the current word of the day to the wordle template for grid sizing and other functionality
    word_length = len(db.getWord(current_day))

    return render_template('wordle.html', user=getUser(), N=word_length)


# this handles the validation of a user submitted word. if the word is valid, it will compare it to the word of the day
# and return a dictionary that contains color codes for each index of the inputted word. This will show how similar the two are
@app.route('/wordvalidation', methods=["POST", "GET"])
def wordvalidation():
    # retrieve the inputted word
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    inputted_word = form_fields["word"]
    # adds the user inputted word into the word url, need this url for the word api request
    word_validate_url = "https://wordsapiv1.p.rapidapi.com/words/"
    word_validate_url += inputted_word

    # records the response from the word api request
    response = requests.request("GET", word_validate_url, headers=word_validate_headers)
    # if the response has word in it, then the word was found and is a viable submission
    index = response.text.find("success")

    real = ""
    start = False
    # see if the request returned with a success == false
    while (True):
        if response.text[index] == " " or response.text[index] == ",":
            break
        if start == True and response.text[index] != '"':
            real += response.text[index]
        if response.text[index] == ":":
            start = True
        index += 1

    # if it equals false, then the word does not exists
    if (real == "false"):
        return json.dumps({"Success": 0})
    # if it is not equal to false, then it is a real word, so check it against the correct word and return a dictionary of what indexes are correct
    # index = 0 is the character is not in the correct word at all
    # index = 1 is the character is in the word, but not in the correct spot
    # index = 2 is the character is in the word and in the correct spot
    else:
        char_dict = {}
        correct_word = db.getWord(date.today().strftime("%m/%d/%Y"))
        # this keeps count of each char found in the correct word
        char_count_dict = {}
        # find the counts of each character that is in the correct word, this helps with giving the grids the correct colors
        for x in correct_word:
            if x in char_count_dict:
                char_count_dict[x] += 1
            if x not in char_count_dict:
                char_count_dict[x] = 1

        # dictionary of lists that have the indexs that correlate to that character being used in the user word
        current_char_count = {}
        for i in range(len(correct_word)):
            # i use .lower() throughout this section because the inputted word is in all caps and the stored word is all undercase
            if inputted_word[i].lower() == correct_word[i]:

                char_dict[i] = 2
                # this shows that we have more characters in the inputted word than there is in the correct word
                if char_count_dict[inputted_word[i].lower()] - 1 < 0:
                    # pop the last index added to this specific character and add the index of this character to it
                    not_used = current_char_count[inputted_word[i].lower()].pop()
                    # change the number at the index of the popped index
                    char_dict[not_used] = 0
                    # insert the index at the front because exact matches hold priority
                    current_char_count[inputted_word[i].lower()].insert(0, i)
                else:
                    if inputted_word[i].lower() in current_char_count:
                        current_char_count[inputted_word[i].lower()].insert(0, i)
                    # if the character has not been seen yet, add it like normal
                    elif inputted_word[i].lower() not in current_char_count:
                        current_char_count[inputted_word[i].lower()] = list()
                        current_char_count[inputted_word[i].lower()].append(i)
                        char_count_dict[inputted_word[i].lower()] -= 1

            else:
                # check if the character is in the correct word at all
                is_in = False
                # iterate through the correct word and see if any of the characters equal the current character
                for x in correct_word:

                    if inputted_word[i].lower() == x:
                        # the character was found in it, only add if we have not found enough of these characters already
                        # if there is 2 S's in the correct word and we already have found 2 S's, treat the next S like it is
                        # not in the correct word at all and give it a color code of 0
                        if char_count_dict[inputted_word[i].lower()] - 1 >= 0:
                            if inputted_word[i].lower() in current_char_count:
                                current_char_count[inputted_word[i].lower()].append(i)
                            elif inputted_word[i].lower() not in current_char_count:
                                current_char_count[inputted_word[i].lower()] = list()
                                current_char_count[inputted_word[i].lower()].append(i)
                            char_count_dict[inputted_word[i].lower()] -= 1
                            is_in = True
                            char_dict[i] = 1
                    # append the index to end of list because not true matches have a first come first serve priority

                if is_in == False:
                    char_dict[i] = 0
        # add success key to show that the word was in fact found and then return the dictionary
        is_correct = True
        char_dict["Success"] = 1
        # iterates through the tiles to see if they are all the same
        for tile in char_dict:

            if tile != "Success":
                if char_dict[tile] == 1 or char_dict[tile] == 0:
                    is_correct = False
                    break
        if is_correct == True:
            char_dict["correct"] = 'True'
        else:
            char_dict["correct"] = 'False'
        # returns if the word is correct or not so we can know if they won or not
        return json.dumps(char_dict)


# process a users victory
@app.route('/processvictory', methods=["POST", "GET"])
def processvictory():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    # store the user information

    # only store the victor if the user was marked as a winner
    if form_fields['winner'] == 'True':
        db.storeNewVictor(session['email'], date.today().strftime("%m/%d/%Y"), form_fields['time'])

    return json.dumps({'Success': 1})


# retrieves the top 5 users of todays wordle and the correct word of the day
@app.route('/retrieverankings', methods=["POST", "GET"])
def retrieverankings():
    current_day = date.today().strftime("%m/%d/%Y")
    # append the correct word
    top = db.retrieveTop(current_day)
    top['word'] = db.getWord(current_day)

    return json.dumps(top)


#######################################################################################
# # feedback related routes
#######################################################################################
@app.route('/processfeedback', methods=['POST'])
def processfeedback():
    feedback = request.form
    header = ["name", "email", "comment"]
    data = []
    # gather the data from the form
    data.append(feedback['name'])
    data.append(feedback['email'])
    data.append(feedback['feedback_comment'])
    # insert it into the database table
    db.insertRows('feedback', header, data)
    feedback_select = "SELECT * FROM feedback"
    # grabs the information from the feedback table
    feedback_data = db.query(feedback_select)
    # this redirect prevents page refreshs from inserting the same post request more than one time
    return redirect('/feedback')


# used to stop post from sending more than once when page is refreshed
@app.route('/feedback')
def refreshcheck():
    # get the information and render it in the feedback html
    feedback_select = "SELECT * FROM feedback"
    feedback_data = db.query(feedback_select)
    return render_template('processfeedback.html', feedback_data=feedback_data, user=getUser())


@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)


@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r


#######################################################################################
# # Othello related routes
#######################################################################################

@app.route('/Othello', methods=["POST", "GET"])
def othello():
    return render_template('othello.html', grid_size=8)


@app.route("/processgamestart", methods=["POST", "GET"])
def processgamestart():
    session.pop('difficulty', default=None)
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    print(form_fields)
    session["difficulty"] = form_fields["difficulty"]
    return {'Success': 1}
