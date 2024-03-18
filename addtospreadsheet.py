import gspread
import schedule
import time
from gamedata import getGameData

def addtospreadsheet():
    SPREADSHEET_ID = "1rpIjIBM70klZ4ZgLjZ2V4IqL4BKlYPN9Grp5L6VkPmE"
    
    Sheet_credential = gspread.service_account("credentials.json")
    
    # Open Spreadsheet by URL
    # spreadsheet = Sheet_credential.open_by_url('paste your sheet url')
    
    # Open Spreadsheet by key
    spreadsheet = Sheet_credential.open_by_key(SPREADSHEET_ID)
    worksheet = spreadsheet.worksheet("PythonTest")
    max_length = len(worksheet.col_values(1)) + 1
    # print(getGameData())
    for index, row in enumerate(getGameData()):
        tempRow = [row['date'],row['teams'],row['bet'],row['odds'],row['dawg'],row['result'],row['WL']]
        for idx, item in enumerate(tempRow, start=1):
            worksheet.update_cell(max_length + index, idx, item)
        print(tempRow)
    
schedule.every().day.at("22:05").do(addtospreadsheet)

while True:
        schedule.run_pending()
        time.sleep(1)