import sqlite3
import atexit

DB_NAME = 'ar_db'


# Data Transfer Objects:
class user(object):
    def __init__(self, id, first_name, last_name, phone, email, joined_at, club_id):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.joined_at = joined_at
        self.club_id = club_id


class membership(object):
    def __init__(self, id, user_id, start_date, end_date, membership_type):
        self.id = id
        self.user_id = user_id
        self.start_date = start_date
        self.end_date = end_date
        self.membership_type = membership_type


# Data Access Object:
class Dao(object):
    def __init__(self, dto_type):
        self._dto_type = dto_type
        # dto_type is a class, its __name__ field contains a string representing the name of the class.
        # assume table name is the same ass class name f.e: class: user table: users
        self._table_name = dto_type.__name__ + 's'

    def insert(self, dto_instance):
        ins_dict = vars(dto_instance)

        column_names = ','.join(ins_dict.keys())
        params = tuple(ins_dict.values())

        query = 'INSERT INTO {}.{} ({}) VALUES ({})'.format(DB_NAME, self._table_name, column_names, params)
        print(query)


# SQL query that returns the emails that already exist in the DB
def getDuplicateEmailsFromDB(emails):
    query = 'SELECT * FROM {}.users WHERE email in {}'.format(DB_NAME, tuple(emails))
    print(query)
    # with a real query we wold return True if the number of results form the query > 0, False otherwise
    return 0


# Repository
class Repository:
    def __init__(self):
        self.user = Dao(user)
        self.membership = Dao(membership)


# singleton
repo = Repository()
