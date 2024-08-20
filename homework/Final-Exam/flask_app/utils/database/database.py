import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import hashlib
import os
import cryptography
from datetime import date
from cryptography.fernet import Fernet
from math import pow


class database:

    def __init__(self, purge=False):

        # Grab information from the configuration file
        self.database = 'db'
        self.host = '127.0.0.1'
        self.user = 'master'
        self.port = 3306
        self.password = 'master'
        self.tables = ['institutions', 'positions', 'experiences', 'skills', 'feedback', 'users', 'victors',
                       'words', 'decks', 'cards']

        # NEW IN HW 3-----------------------------------------------------------------
        self.encryption = {'oneway': {'salt': b'averysaltysailortookalongwalkoffashortbridge',
                                      'n': int(pow(2, 5)),
                                      'r': 9,
                                      'p': 1
                                      },
                           'reversible': {'key': '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='}
                           }
        # -----------------------------------------------------------------------------

    def query(self, query="SELECT * FROM users", parameters=None):

        cnx = mysql.connector.connect(host=self.host,
                                      user=self.user,
                                      password=self.password,
                                      port=self.port,
                                      database=self.database,
                                      use_unicode=True,
                                      charset='utf8'
                                      )

        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def createTables(self, purge=False, data_path='flask_app/database/'):
        if purge == True:
            tables_drop = ["skills", "experiences", "positions", "institutions", "feedback", 'victors']
            for drop in tables_drop:
                drop_query = "DROP TABLE IF EXISTS " + drop
                self.query(drop_query)

        # creates the tables
        def executeFileScripts(filename):
            raw_file = open(filename)
            sql_file = raw_file.read()
            sql_file.strip()
            self.query(sql_file)
            raw_file.close()

        sql_tables = ['institutions.sql', 'feedback.sql', 'positions.sql', 'experiences.sql', 'skills.sql', 'users.sql',
                      "words.sql", "victors.sql", "decks.sql", "cards.sql"]

        # goes through each table and creates it
        for table in sql_tables:
            correct_path = data_path + 'create_tables/' + table
            executeFileScripts(correct_path)

        tables_csv = ['institutions', 'positions', 'experiences', 'skills', 'decks']
        # iterates through tables with csv data
        for x in tables_csv:
            csv_file = data_path + 'initial_data/' + x + '.csv'
            file = open(csv_file)
            reader = csv.reader(file)
            header = []
            # gets the header information
            header = next(reader)
            # pops the unique id number we dont need it
            header.pop(0)

            # iterate through the rows in the csv and inserts that information
            for row in reader:
                # pops the value that would have went with the unique id number
                row.pop(0)
                self.insertRows(x, header, row)

    def insertRows(self, table='table', columns=['x', 'y'], parameters=[['v11', 'v12'], ['v21', 'v22']]):

        insert_statement = "INSERT INTO " + table + "("
        counter = 0
        # essentially creates the insert statement by collecting the column names and appending
        # them onto a string
        for column in columns:
            counter += 1
            insert_statement += column
            if counter < len(columns):
                insert_statement += ", "
        insert_statement += ") VALUES ("
        counter = 0
        values = "("
        # does the same thing as the column but adds default variable strings
        for parameter in parameters:
            counter += 1
            insert_statement += "%s"
            values += parameter
            if counter < len(parameters):
                insert_statement += ", "
                values += ","
        insert_statement += ")"
        values += ")"
        self.query(insert_statement, parameters)

    def getResumeData(self):
        # Pulls data from the database to genereate data like this:

        # retrieve all the tables
        instituion_select = self.query("SELECT * FROM institutions")
        position_select = self.query("SELECT * FROM positions")
        experience_select = self.query("SELECT * FROM experiences")
        skill_select = self.query("SELECT * FROM skills")
        # end of table retrieval
        resume_data_dict = dict()
        inst_counter = 1
        for inst_row in instituion_select:
            # get inside the institutions dict
            resume_data_dict[inst_counter] = dict()
            individual_dict = resume_data_dict[inst_counter]

            # collect the information on the institutions
            individual_dict['address'] = inst_row['address']
            individual_dict['city'] = inst_row['city']
            individual_dict['state'] = inst_row['state']
            individual_dict['type'] = inst_row['type']
            individual_dict['zip'] = inst_row['zip']
            individual_dict['department'] = inst_row['department']
            individual_dict['name'] = inst_row['name']
            # create the dict for positions
            individual_dict['positions'] = dict()
            position_counter = 1
            # go into the position table and find which positions correlate with this institution
            for pos_row in position_select:
                # if the institution id matches then the position was at this institution
                if inst_row['inst_id'] == pos_row['inst_id']:

                    # set up the position dict
                    positions_dict = individual_dict['positions']
                    positions_dict[position_counter] = dict()
                    specific_pos_dict = positions_dict[position_counter]
                    # get the information for the position
                    specific_pos_dict['end_date'] = pos_row['end_date']
                    specific_pos_dict['responsibilities'] = pos_row['responsibilities']
                    specific_pos_dict['start_date'] = pos_row['start_date']
                    specific_pos_dict['title'] = pos_row['title']
                    experience_counter = 1
                    # create the dictionary for the experiences at the position
                    specific_pos_dict['experiences'] = dict()
                    # enter the experience table and find which experiences correlate with this position
                    for exp_row in experience_select:
                        # if the position ids match then the experience was for this position
                        if pos_row['position_id'] == exp_row['position_id']:

                            #  set up the experience dictionary nesting
                            experience_dict = specific_pos_dict['experiences']
                            experience_dict[experience_counter] = dict()
                            specific_exp_dict = experience_dict[experience_counter]
                            # retrieve the information for the experience
                            specific_exp_dict['description'] = exp_row['description']
                            specific_exp_dict['end_date'] = exp_row['end_date']
                            specific_exp_dict['hyperlink'] = exp_row['hyperlink']
                            specific_exp_dict['name'] = exp_row['name']
                            # retrieve the skills information
                            specific_exp_dict['skills'] = dict()
                            skills_counter = 1
                            # enter the skills table and find which skills correlate with this experience
                            for skill_row in skill_select:
                                # if the experience id's are the same then the skill is for this experience
                                if exp_row['experience_id'] == skill_row['experience_id']:
                                    # set up skill dictionary nesting
                                    skills_dict = specific_exp_dict['skills']
                                    skills_dict[skills_counter] = dict()
                                    specific_skill_dict = skills_dict[skills_counter]
                                    # retrieve skill information
                                    specific_skill_dict['name'] = skill_row['name']
                                    specific_skill_dict['skill_level'] = skill_row['skill_level']
                                    skills_counter += 1
                            # end of skill dictionary creation
                            specific_exp_dict['start_date'] = exp_row['start_date']
                            experience_counter += 1
                    # end of experience dictionary creation
                    position_counter += 1
            # end of position dictionary creation
            inst_counter += 1
        # end of resume dictionary creation

        return resume_data_dict

    #######################################################################################
    # AUTHENTICATION RELATED
    #######################################################################################
    #  checks if the email is in the user database
    def checkEmail(self, email='me@email.com'):
        # retrieve user data table
        availableEmail = True
        # grab the user database information
        user_select = self.query("SELECT * FROM users")
        # iterate through the users
        for row in user_select:
            # if any email in the user select equals the inputted email, then it is already in use
            if row["email"] == email:
                # return false if the email is found in the database already
                availableEmail = False
        if availableEmail == False:
            return 0
        else:
            return 1

    # creates the user
    def createUser(self, email='me@email.com', password='password', role='user'):
        # checks if the email is already in the database
        available = self.checkEmail(email)
        # if the email is not in the database then insert the new user information
        if available == 1:
            self.insertRows('users', ['role', 'email', 'password'], [role, email, self.onewayEncrypt(password)])
            return {'Success': 1}
        # else return with no success
        else:
            return {'Success': 0}

    # checks that there is a email with the associated password in the database
    def authenticate(self, email='me@email.com', password='password'):
        # first checks if the email is in the database
        available = self.checkEmail(email)
        #  0 means that the email is already in the database
        if available == 0:
            # grab the user information
            user_select = self.query("SELECT * FROM users")
            # iterate through the users and try to match the email with the inputted email
            for row in user_select:

                if row["email"] == email:
                    # when the user with the same email is found as the inputted email, check and make sure the users password matches as well
                    if row["password"] == self.onewayEncrypt(password):
                        # return success 1 if password and email match
                        return {'Success': 1}
        # if available is not 0, then the email does not exist in the database
        else:
            # this means the account has been taken
            return {"Account": 1, "Success": 0}
        # if the function has not returned a success yet, then it must have failed
        return {'Success': 0}

    # function that checks if a date is already in the word database
    def checkDate(self, current_date):
        date_used = False
        # grab the user database information
        word_select = self.query("SELECT * FROM words")
        # iterate through the users
        for row in word_select:
            # if any email in the user select equals the inputted email, then it is already in use
            if row["date"] == current_date:
                # return false if the email is found in the database already
                date_used = True

        if date_used == True:
            return 1
        else:
            return 0

    # function that stores a new word with its correlating date
    def storeNewWord(self, date, word):
        # insert the new word
        self.insertRows('words', ['date', 'word'], [date, word])
        return 1

    def getWord(self, date):
        # grab the user database information
        word_select = self.query("SELECT * FROM words")
        # iterate through the users
        for row in word_select:
            # find the row that has the same date and return that word
            if row["date"] == date:
                return row["word"]
        return 0

    # function that stores the winners information
    def storeNewVictor(self, username, date, time):
        # insert the the new winner
        self.insertRows('victors', ['username', 'date', 'time'], [username, date, time])
        return 1

    # handles retriving the top 5 users in terms of time taken to win
    def retrieveTop(self, date):
        winner_select = self.query("SELECT * FROM victors")
        count = 1
        leaders_dict = {}

        winner_select = sorted(winner_select, key=lambda i: int(i['time']))

        for row in winner_select:

            # only store winners that won on todays wordle
            if row['date'] == date:
                # only take the top 5
                if count <= 5:
                    leaders_dict[count] = row['username'], row['time']
                    count += 1
        return leaders_dict

    def onewayEncrypt(self, string):
        encrypted_string = hashlib.scrypt(string.encode('utf-8'),
                                          salt=self.encryption['oneway']['salt'],
                                          n=self.encryption['oneway']['n'],
                                          r=self.encryption['oneway']['r'],
                                          p=self.encryption['oneway']['p']
                                          ).hex()
        return encrypted_string

    def reversibleEncrypt(self, type, message):
        fernet = Fernet(self.encryption['reversible']['key'])

        if type == 'encrypt':
            message = fernet.encrypt(message.encode())
        elif type == 'decrypt':
            message = fernet.decrypt(message).decode()

        return message

    # #########################################################################################
    ##################### Flash Cards Functions ###############################################
    ###########################################################################################
    def retrievedecks(self,user):
        decks = self.query("SELECT * FROM decks")
        users_decks = []
        for deck in decks:
            if deck['user_id'] == user:
                users_decks.append(deck)
        return users_decks

    def retrieveusers(self, current_user):
        users = self.query("SELECT * FROM users")
        for user in users:
            if user['email'] == current_user:
                return user['user_id']

        return None

    def retrieveCards(self, deck_id):

        cnx = mysql.connector.connect(host=self.host,
                                      user=self.user,
                                      password=self.password,
                                      port=self.port,
                                      database=self.database,
                                      use_unicode=True,
                                      charset='utf8'
                                      )
        cur = cnx.cursor(dictionary=True)
        cur.execute("""SELECT * FROM cards WHERE deck_id = '%s'""" % (int(deck_id)))
        cards = cur.fetchall()
        return cards

    def createdeck(self, user, name, language_1, language_2, accessibility):
        user_select = self.query("SELECT * FROM users")
        # iterate through the users and try to match the email with the inputted email
        user_id = 0
        for row in user_select:

            if row["email"] == user:
                user_id = row["user_id"]

        languages = language_1 + ", " + language_2
        self.insertRows('decks', ['user_id', 'name', 'languages', 'access', ],
                        [str(user_id), name, languages, accessibility])
        return {'Success': 1}

    def addcard(self, user, name, front, back, deck_id):

        self.insertRows('cards', ['deck_id', 'front', 'back', 'last_seen'],
                        [str(deck_id), str(front), str(back), ""])

        return {'Success': 1}

    def deleteCard(self, card_id):
        cnx = mysql.connector.connect(host=self.host,
                                      user=self.user,
                                      password=self.password,
                                      port=self.port,
                                      database=self.database,
                                      use_unicode=True,
                                      charset='utf8'
                                      )

        cur = cnx.cursor(dictionary=True)
        cur.execute("""DELETE FROM cards WHERE cards_id = '%s'""" % (int(card_id)))
        cnx.commit()

        cur.close()
        cnx.close()
        return {'Success': 1}
