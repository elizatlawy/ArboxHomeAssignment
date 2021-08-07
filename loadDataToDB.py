import argparse
import sys
from uuid import uuid4
import pandas as pd
import presistence as pr
import dataHeaders


# This is only an example for a Unique ID generator since I do not know how the
# user id and table id's generated in the actual DB.
def generateUniqueID():
    return str(uuid4())


def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("dataPath", help="Path to the Data Excel Sheet to insert into the Database")
    parser.add_argument("clubId", help="Id of the new club.", type=int)
    return parser.parse_args()


def readExelSheet(path, sheet=0):
    try:
        xlSheet = pd.read_excel(path, sheet)
        return xlSheet
    except Exception as e:
        print("Error while opening Excel Sheet file: " + str(e))


# check if the exel file have the necessary headers in order to input the data to the DB
def checkHeaders(dataFrameHeaders):
    if len(dataFrameHeaders) < 5:
        sys.exit("Exel Sheet is missing one of the necessary headers: first_name, last_name, phone, email,"
                 "membership_start_date membership_end_date or membership_name")


# assume that we have all the necessary headers in the same order but their name may change in different exel sheets
def setHeaders(dataFrameHeaders):
    dataHeaders.FIRST_NAME = dataFrameHeaders[0]
    dataHeaders.LAST_NAME = dataFrameHeaders[1]
    dataHeaders.EMAIL = dataFrameHeaders[2]
    dataHeaders.PHONE = dataFrameHeaders[3]
    dataHeaders.MEMBERSHIP_START_DATE = dataFrameHeaders[4]
    dataHeaders.MEMBERSHIP_END_DATE = dataFrameHeaders[5]
    dataHeaders.MEMBERSHIP_NAME = dataFrameHeaders[6]


# check if there are duplicate emails in the provided exel sheet
def checkDuplicateEmailsInData(emails):
    dupEmails = set(emails[emails.duplicated(keep=False)].tolist())
    if dupEmails:
        sys.exit("Duplicate emails are not allowed.\nThe exel sheet contains the following duplicate emails: \n" + str(
            dupEmails) +
                 "\nPlease delete the duplications and try ""again")


# check if the emails in the provided exel sheet already exist in the DB
def checkDuplicateEmailsInDB(emails):
    duplicateEmailsFromDB = pr.getDuplicateEmailsFromDB(emails)
    if duplicateEmailsFromDB > 0:
        sys.exit("Duplicate emails are not allowed. \n The DB already contains the following emails from the exel "
                 "sheet:" + str(duplicateEmailsFromDB)
                 + " please delete the duplications and try again")


def insertDataToDB(dataFrame, clubId):
    for index, row in dataFrame.iterrows():
        usersId = generateUniqueID()
        insertUserToDB(row, usersId, clubId)
        insertMembershipToDB(row, usersId)


def insertUserToDB(row, usersId, clubId):
    userToInsert = pr.user(usersId,
                           row[dataHeaders.FIRST_NAME],
                           row[dataHeaders.LAST_NAME],
                           row[dataHeaders.PHONE],
                           row[dataHeaders.EMAIL],
                           row[dataHeaders.MEMBERSHIP_START_DATE].strftime("%d/%m/%y"),
                           clubId)
    pr.repo.user.insert(userToInsert)


def insertMembershipToDB(row, usersId):
    membershipToInsert = pr.membership(generateUniqueID(),
                                       usersId,
                                       row[dataHeaders.MEMBERSHIP_START_DATE].strftime("%d/%m/%y"),
                                       row[dataHeaders.MEMBERSHIP_END_DATE].strftime("%d/%m/%y"),
                                       row[dataHeaders.MEMBERSHIP_NAME])
    pr.repo.membership.insert(membershipToInsert)


# main function that handle the data process
def processData(args):
    dataFrame = readExelSheet(args.dataPath)
    dataFrameHeaders = dataFrame.columns.values
    checkHeaders(dataFrameHeaders)
    setHeaders(dataFrameHeaders)
    emails = dataFrame[dataHeaders.EMAIL]
    checkDuplicateEmailsInData(emails)
    checkDuplicateEmailsInDB(emails)
    insertDataToDB(dataFrame, args.clubId)


if __name__ == '__main__':
    processData(parseArgs())
