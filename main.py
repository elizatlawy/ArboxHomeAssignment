import argparse
import sys
from uuid import uuid4
import pandas as pd
import presistence
import dataHeaders


# assume that we have all the necessary headers but their name may change in different exel sheets
def setHeaders(dataFrameHeaders):
    dataHeaders.FIRST_NAME = dataFrameHeaders[0]
    dataHeaders.LAST_NAME = dataFrameHeaders[1]
    dataHeaders.EMAIL = dataFrameHeaders[2]
    dataHeaders.PHONE = dataFrameHeaders[3]
    dataHeaders.MEMBERSHIP_START_DATE = dataFrameHeaders[4]
    dataHeaders.MEMBERSHIP_END_DATE = dataFrameHeaders[5]
    dataHeaders.MEMBERSHIP_NAME = dataFrameHeaders[6]


# This is only an example for a Unique ID generator since I do not know how the
# user id and table id's work in the actual DB.
def generateUniqueID():
    return str(uuid4())


def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("dataPath", help="Path to the Data Excel Sheet to insert into the Database")
    parser.add_argument("clubId", help="Id of the new club club.", type=int)
    return parser.parse_args()


def openExelSheet(path, sheet=0):
    try:
        xlSheet = pd.read_excel(path, sheet)
        return xlSheet
    except Exception as e:
        print("Error while opening Excel Sheet file: " + str(e))


def isUniqueEmails(emailsList):
    return len(emailsList) == len(emailsList.unique())


def processData(args):
    dataFrame = openExelSheet(args.dataPath)
    dataFrameHeaders = dataFrame.columns.values
    if len(dataFrameHeaders) < 5:
        sys.exit("Exel Sheet is missing one of the necessary headers: first_name, last_name, phone, email,"
                 "membership_start_date membership_end_date or membership_name")
    setHeaders(dataFrameHeaders)
    if not isUniqueEmails(dataFrame[dataHeaders.EMAIL]):
        sys.exit("The data file contains duplicate emails fields, please delete the duplication and try again")
    else:
        insertDataToDB(dataFrame, args.clubId)


def insertDataToDB(dataFrame, clubId):
    for index, row in dataFrame.iterrows():
        usersId = generateUniqueID()
        insertUserToDB(row, usersId, clubId)
        insertMembershipToDB(row, usersId)


def insertUserToDB(row, usersId, clubId):
    userToInsert = presistence.user(usersId,
                                    row[dataHeaders.FIRST_NAME],
                                    row[dataHeaders.LAST_NAME],
                                    row[dataHeaders.PHONE],
                                    row[dataHeaders.EMAIL],
                                    row[dataHeaders.MEMBERSHIP_START_DATE].strftime("%d/%m/%y"),
                                    clubId)
    presistence.repo.user.insert(userToInsert)


def insertMembershipToDB(row, usersId):
    membershipToInsert = presistence.membership(generateUniqueID(),
                                                usersId,
                                                row[dataHeaders.MEMBERSHIP_START_DATE].strftime("%d/%m/%y"),
                                                row[dataHeaders.MEMBERSHIP_END_DATE].strftime("%d/%m/%y"),
                                                row[dataHeaders.MEMBERSHIP_NAME])
    presistence.repo.membership.insert(membershipToInsert)


if __name__ == '__main__':
    processData(parseArgs())
