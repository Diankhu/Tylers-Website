import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import datetime
class database:

    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'

    def query(self, query = "SELECT CURDATE()", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
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
            print(row)
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def about(self, nested=False):
        query = """select concat(col.table_schema, '.', col.table_name) as 'table',
                          col.column_name                               as column_name,
                          col.column_key                                as is_key,
                          col.column_comment                            as column_comment,
                          kcu.referenced_column_name                    as fk_column_name,
                          kcu.referenced_table_name                     as fk_table_name
                    from information_schema.columns col
                    join information_schema.tables tab on col.table_schema = tab.table_schema and col.table_name = tab.table_name
                    left join information_schema.key_column_usage kcu on col.table_schema = kcu.table_schema
                                                                     and col.table_name = kcu.table_name
                                                                     and col.column_name = kcu.column_name
                                                                     and kcu.referenced_table_schema is not null
                    where col.table_schema not in('information_schema','sys', 'mysql', 'performance_schema')
                                              and tab.table_type = 'BASE TABLE'
                    order by col.table_schema, col.table_name, col.ordinal_position;"""
        results = self.query(query)
        if nested == False:
            return results

        table_info = {}
        for row in results:
            table_info[row['table']] = {} if table_info.get(row['table']) is None else table_info[row['table']]
            table_info[row['table']][row['column_name']] = {} if table_info.get(row['table']).get(row['column_name']) is None else table_info[row['table']][row['column_name']]
            table_info[row['table']][row['column_name']]['column_comment']     = row['column_comment']
            table_info[row['table']][row['column_name']]['fk_column_name']     = row['fk_column_name']
            table_info[row['table']][row['column_name']]['fk_table_name']      = row['fk_table_name']
            table_info[row['table']][row['column_name']]['is_key']             = row['is_key']
            table_info[row['table']][row['column_name']]['table']              = row['table']
        return table_info



    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        if purge == True:
            tables_drop = ["skills","experiences","positions","institutions","feedback"]
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

        sql_tables = ['institutions.sql','feedback.sql','positions.sql','experiences.sql','skills.sql']

        # goes through each table and creates it
        for table in sql_tables:
            correct_path = data_path + 'create_tables/' + table
            executeFileScripts(correct_path)

        tables_csv = ['institutions','positions','experiences','skills']
        # iterates through tables with csv data
        for x in tables_csv:
            csv_file = data_path + 'initial_data/' + x +'.csv'
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
                self.insertRows(x,header,row)


    def insertRows(self, table='table', columns=['x','y'], parameters=[['v11','v12'],['v21','v22']]):

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
        self.query(insert_statement,parameters)


    def getResumeData(self):
        # Pulls data from the database to genereate data like this:

        # retrieve all the tables
        instituion_select= self.query("SELECT * FROM institutions")
        position_select= self.query("SELECT * FROM positions")
        experience_select= self.query("SELECT * FROM experiences")
        skill_select= self.query("SELECT * FROM skills")
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

        print(resume_data_dict)
        return resume_data_dict
