import os.path
from gamedata import getGameData
import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "1rpIjIBM70klZ4ZgLjZ2V4IqL4BKlYPN9Grp5L6VkPmE"
RANGE_NAME = "PythonTest!A2:H"


def main():
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    # service = build("sheets", "v4", credentials=creds)

    url = "https://sheets.googleapis.com/v4/spreadsheets/" + SPREADSHEET_ID + ":batchUpdate"
    requestsJson = {"requests":[
        {
        "insertDimension": {
            "range": {
            "sheetId": SPREADSHEET_ID,
            "dimension": "ROWS",
            "startIndex": 0,
            "endIndex": 1
            },
            "inheritFromBefore": True
        }
        },
    ]}

    resp = requests.post(url, json=requestsJson)
    print(resp)

    # Call the Sheets API
    # sheet = service.spreadsheets()
    # result = (
    #     sheet.values()
    #     .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
    #     .execute()
    # )
    # values = result.get("values", [])

    # if not values:
    #   print("No data found.")
    #   return

    # print("Date, Teams, Bet, Odds, DAWG?, Result, W/L, Profit:")
    # for row in values:
    #   # Print columns A and E, which correspond to indices 0 and 4.
    #   print(f"{row[0]}, {row[1]}, {row[2]}, {row[3]}, {row[4]}, {row[5]}, {row[6]}, {row[7]}")
    # print(getGameData())
  except HttpError as err:
    print(err)


if __name__ == "__main__":
  main()