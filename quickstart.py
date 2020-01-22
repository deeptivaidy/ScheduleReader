from __future__ import print_function
import click
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1zVHrMiVbWPRKUMoYsAYwuvuNT3AGtAmu1P6Gyj7aa6Q"
SAMPLE_RANGE_NAME = "Fall  18!A1:E"


@click.command()
@click.option(
    "--link",
    "-l",
    default="https://docs.google.com/spreadsheets/d/1zVHrMiVbWPRKUMoYsAYwuvuNT3AGtAmu1P6Gyj7aa6Q/edit#gid=423768437",
    help="Link to google sheet",
)
def main(link):
    arr_link = link.split("/")
    # Check if link is valid spreadsheet URL
    if (
        len(arr_link) >= 7
        and arr_link[2] == "docs.google.com"
        and arr_link[3] == "spreadsheets"
    ):
        # print(link)
        SAMPLE_SPREADSHEET_ID = arr_link[5]

    else:
        # print(arr_link)
        raise ValueError("Link must be a valid Google Sheets URL")

    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
        .execute()
    )
    values = result.get("values", [])

    if not values:
        print("No data found.")
    else:
        # convert values into dataframe
        df = pd.DataFrame(values)

        # replace all non trailing blank values created by Google Sheets API
        # with null values
        df_replace = df.replace([""], [None])

        # convert back to list
        processed_dataset = df_replace.values.tolist()
        # print('Name, Major:')
        for row in processed_dataset:
            # Print columns A and E, which correspond to indices 0 and 4.
            print(row)
            # print('%s, %s' % (row[0], row[2]))


if __name__ == "__main__":
    main()
