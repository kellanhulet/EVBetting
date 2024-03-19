from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime, date
import csv


def space_split(a):
    if a.count(" ") == 1:
        return a.split(" ")[0]
    return " ".join(a.split(" ", 2)[:2])

def get_bet_type(bet):
    if "UNDER" in bet.upper():
        return "Under"
    elif "OVER" in bet.upper():
        return "Over"
    else:
        betParsed = bet.split()
        try:
            float(betParsed[-1])
            return "Spread"
        except ValueError:
            return "ML"
    
def filter_json_objects(json_list, date):
    filtered_objects = []

    for obj in json_list:
        try:
            # Assuming the date key in JSON object is named "date"
            date_str = obj["date"]
            obj_date = datetime.strptime(date_str,'%A, %B %d, %Y').date()

            if obj_date <= date:
                filtered_objects.append(obj)
        except KeyError:
            print("Invalid JSON object: 'date' key not found.")

    return filtered_objects

# Get the games and results of today's bets
def getGameData():
    # Open the best picks page on the Rithmm website for NCAAM basketball
    # Could move all URLs to constants.py or another file
    url = "https://www.rithmm.com/best-bets/ai-college-basketball-picks-ncaab?13550908_page=24"
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # Get todays date. Script will only consider games from today
    # currentDate = date.today()
    currentDate = datetime.strptime('01-25-2024','%m-%d-%Y').date()

    betList = soup.find("div", class_="blogs-collection-list w-dyn-items")

    gsRows = []
    gameKeys = []

    for row in betList.find_all("div", class_="w-dyn-item"):
        gsRow = {}

        # First p tag contains the date in the following format: WEEKDAY, MONTH DD, YYYY
        cells = row.find_all("p")
        gsDate = cells[0].get_text() # Date

        date_obj = datetime.strptime(gsDate,'%A, %B %d, %Y').date()
        # Only consider today's games
        if currentDate == date_obj:
            gsRow["date"] = gsDate

            # Title for each section is the two teams playing
            # There doesn't seem to be a format of home team first or second. Also not alphabetical. Seems random but could be based off a hidden id or data piece not exposed.
            title = row.find("h5", class_="featured-blog-heading-2 best-bets")
            gsTeams = title.get_text()  # Teams
            gsHomeTeam = gsTeams.split(" vs",1)[0].split(" (",1)[0].lstrip()
            gameKeys.insert(len(gameKeys),gsHomeTeam)
            gsRow["teams"] = gsTeams

            # Button color is different for DAWG bets
            dawgBet = row.find("div", class_="category-contain-2 free-picks").get("style")
            gsDawg = "Yes" if "#30a6eb" in dawgBet else "No"
            gsRow["dawg"] = gsDawg

            # Rithmm put an NBA game in the NCAAM basketball category. Very cool, thank you Rithmm!
            if not "NCAAB" in cells[1].get_text():
                continue
            
            # Second p tag contains league, teams, and the bet. Parse the bet from the text.
            # All bets are either Over/Under totals or moneylines
            # Have not seen any spreads yet (for free picks)
            gameText1 = cells[1].get_text().split(": ",1)[1]
            if " - " in gameText1:
                gsBet = gameText1.split(" - ",1)[1].lstrip() 
            elif "+" in gameText1 and not "." in gameText1:
                gsBet = gameText1.split(" +",1)[0].lstrip()
            elif " -" in gameText1 or "+" in gameText1:
                if "OVER" in gameText1.upper() or "UNDER" in gameText1.upper():
                    gsBet = gameText1.split(" -",1)[1].lstrip()
                else:
                    index_of_parenthesis = gameText1.find("(")
                    gsBet = gameText1[:index_of_parenthesis].lstrip()  
            gsRow["bet"] = gsBet
            gsRow["betType"] = get_bet_type(gsBet)

            gsOdds = "-110"
            if gsRow["betType"] == "ML":
                tempInd = gameText1.index("+") + 1
                gsOdds = gameText1[tempInd:tempInd+3]
            gsRow["odds"] = gsOdds

            # All data pertaining to Rithmm is pulled, add to larger list
            gsRows.insert(len(gsRows), gsRow)

    # At this point, could export to a Discord bot or another method of nofitications. All data needed to place the bet has been obtained.
    # Most major sportsbook's lines match similarly to the odds displayed on Rithmm
    # Can take the bet without worrying about if the line has moved (most are around -110 for totals and +140 - +250 for ML)

    # scoresUrl = "https://www.espn.com/mens-college-basketball/scoreboard/_/seasontype/2/group/50"
    scoresUrl = "https://www.espn.com/mens-college-basketball/scoreboard/_/date/20240125/seasontype/2/group/50"
    pageESPN = urlopen(scoresUrl)
    htmlESPN = pageESPN.read().decode("utf-8")
    soupESPN = BeautifulSoup(htmlESPN, "html.parser")

    scoresESPNHTML = soupESPN.find("section", class_="Card gameModules")

    # Gets HTML list of NCAAM basketball games for the day. Filtered for all Division 1 games
    for game in scoresESPNHTML.find_all("section", class_="Scoreboard bg-clr-white flex flex-auto justify-between"):
        # Gets the wrapper HTML for the two teams
        gameDetails = game.find("ul", class_="ScoreboardScoreCell__Competitors")
        
        # Gets the HTML tags for the home and away teams for the given game
        homeTeamStats = gameDetails.find("li", class_="ScoreboardScoreCell__Item--home")
        awayTeamStats = gameDetails.find("li", class_="ScoreboardScoreCell__Item--away")
        
        # Gets the name of the home team and away team. Naming convention seems to match well between Rithmm and ESPN (ie, UConn not University of Conneticut, Iowa State not Iowa St. or ISU)
        homeTeamName = homeTeamStats.find("div", class_="ScoreCell__TeamName").get_text()
        awayTeamName = awayTeamStats.find("div", class_="ScoreCell__TeamName").get_text()

        # If either team is apart of the games listed by Rithmm, run the following code to determine the outcome. Otherwise, skip
        if gameKeys.count(homeTeamName) > 0 or gameKeys.count(awayTeamName) > 0:
            # Gets the index of the occurance from the gameKeys list. This index should match the index of the data in gsRows
            index = gameKeys.index(homeTeamName) if gameKeys.count(homeTeamName) > 0 else gameKeys.index(awayTeamName)

            # Get the score of both teams
            homeTeamScore = homeTeamStats.find("div", class_="ScoreCell__Score").get_text()
            awayTeamScore = awayTeamStats.find("div", class_="ScoreCell__Score").get_text()
            
            gsRow = gsRows[index]
            homeScore = int(homeTeamScore)
            awayScore = int(awayTeamScore)

            # Determine which type the bet was, and if the bet won or not. Record whether the bet won or lost as well as the result
            if gsRow["betType"] == "Under":
                lineNumber = gsRow["bet"].split(" ",1)[1]
                if homeScore + awayScore < float(lineNumber):
                    gsRows[index]["WL"] = "W"
                else:
                    gsRows[index]["WL"] = "L"
                gsRows[index]["result"] = homeScore + awayScore
            elif gsRow["betType"] == "Over":
                lineNumber = gsRow["bet"].split(" ",1)[1]
                if homeScore + awayScore > float(lineNumber):
                    gsRows[index]["WL"] = "W"
                else:
                    gsRows[index]["WL"] = "L"
                gsRows[index]["result"] = homeScore + awayScore
            elif gsRow["betType"] == "ML":
                if homeTeamName == gsRow["bet"] and homeScore > awayScore:
                    gsRows[index]["WL"] = "W"
                    gsRows[index]["result"] = homeTeamName
                elif awayTeamName == gsRow["bet"] and awayScore > homeScore:
                    gsRows[index]["WL"] = "W"
                    gsRows[index]["result"] = awayTeamName
                else:
                    gsRows[index]["WL"] = "L"
                    gsRows[index]["result"] = homeTeamName if homeScore > awayScore else awayTeamName
            elif gsRow["betType"] == "Spread":
                        betParsed = gsRow["bet"].split()
                        team = " ".join(betParsed[:-1])
                        spreadNum = float(betParsed[-1])
                        if homeTeamName == team:
                            if homeScore + spreadNum > awayScore:
                                gsRow["WL"] = "W"
                            else:
                                gsRow["WL"] = "L"
                            gsRow["result"] = homeScore - awayScore
                        elif awayTeamName == team:
                            if awayScore + spreadNum > homeScore:
                                gsRow["WL"] = "W"
                            else:
                                gsRow["WL"] = "L"
                            gsRow["result"] = awayScore - homeScore
    # Return the created JSON object
    print(gsRows)
    return gsRows

# Get all posted free bets for NCAAM from Rithmm
# First recorded post appears to be on December 31, 2023
def getRithmmHistory():
    i = 1
    gsRows = []
    while True: 

        print(i)
        # Open the best picks page on the Rithmm website for NCAAM basketball
        # Could move all URLs to constants.py or another file
        url = "https://www.rithmm.com/best-bets/ai-college-basketball-picks-ncaab?13550908_page=" + str(i)
        page = urlopen(url)
        html = page.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")

        betList = soup.find("div", class_="blogs-collection-list w-dyn-items")

        gameKeys = []

        for row in betList.find_all("div", class_="w-dyn-item"):
            gsRow = {}

            # First p tag contains the date in the following format: WEEKDAY, MONTH DD, YYYY
            cells = row.find_all("p")
            gsDate = cells[0].get_text() # Date

            date_obj = datetime.strptime(gsDate,'%A, %B %d, %Y').date()
            
            gsRow["date"] = date_obj.strftime('%m/%d/%Y')

            # Title for each section is the two teams playing
            # There doesn't seem to be a format of home team first or second. Also not alphabetical. Seems random but could be based off a hidden id or data piece not exposed.
            title = row.find("h5", class_="featured-blog-heading-2 best-bets")
            gsTeams = title.get_text()  # Teams
            gsHomeTeam = gsTeams.split(" vs",1)[0].split(" (",1)[0].lstrip()
            gameKeys.insert(len(gameKeys),gsHomeTeam)
            gsRow["teams"] = gsTeams

            # Button color is different for DAWG bets
            dawgBet = row.find("div", class_="category-contain-2 free-picks").get("style")
            gsDawg = "Yes" if "#30a6eb" in dawgBet else "No"
            gsRow["dawg"] = gsDawg
            
            # Rithmm put an NBA game in the NCAAM basketball category. Very cool, thank you Rithmm!
            if not "NCAAB" in cells[1].get_text():
                continue
            # Second p tag contains league, teams, and the bet. Parse the bet from the text.
            # All bets are either Over/Under totals or moneylines
            # Have not seen any spreads yet (for free picks)
            gameText1 = cells[1].get_text().split(": ",1)[1]
            if " - " in gameText1:
                gsBet = gameText1.split(" - ",1)[1].lstrip() 
            elif "+" in gameText1 and not "." in gameText1:
                gsBet = gameText1.split(" +",1)[0].lstrip() 
            elif " -" in gameText1 or "+" in gameText1:
                if "OVER" in gameText1.upper() or "UNDER" in gameText1.upper():
                    gsBet = gameText1.split(" -",1)[1].lstrip()
                else:
                    index_of_parenthesis = gameText1.find("(")
                    gsBet = gameText1[:index_of_parenthesis].lstrip()  
            gsRow["bet"] = gsBet
            gsRow["betType"] = get_bet_type(gsBet)

            gsOdds = "-110"
            if gsRow["betType"] == "ML":
                tempInd = gameText1.index("+") + 1
                gsOdds = gameText1[tempInd:tempInd+3]
            gsRow["odds"] = gsOdds

            # scoresUrl = "https://www.espn.com/mens-college-basketball/scoreboard/_/seasontype/2/group/50"
            scoresUrl = "https://www.espn.com/mens-college-basketball/scoreboard/_/date/" + date_obj.strftime('%Y%m%d') + "/seasontype/2/group/50"
            pageESPN = urlopen(scoresUrl)
            htmlESPN = pageESPN.read().decode("utf-8")
            soupESPN = BeautifulSoup(htmlESPN, "html.parser")
            scoresESPNHTML = soupESPN.find("section", class_="Card gameModules")
            # Gets HTML list of NCAAM basketball games for the day. Filtered for all Division 1 games
            for game in scoresESPNHTML.find_all("section", class_="Scoreboard bg-clr-white flex flex-auto justify-between"):
                # If the game is not finished, skip
                if not game.find("div", class_="ScoreCell__Time").get_text() == "FINAL":
                    continue

                # Gets the wrapper HTML for the two teams
                gameDetails = game.find("ul", class_="ScoreboardScoreCell__Competitors")

                # Gets the HTML tags for the home and away teams for the given game
                homeTeamStats = gameDetails.find("li", class_="ScoreboardScoreCell__Item--home")
                awayTeamStats = gameDetails.find("li", class_="ScoreboardScoreCell__Item--away")
           
                # Gets the name of the home team and away team. Naming convention seems to match well between Rithmm and ESPN (ie, UConn not University of Conneticut, Iowa State not Iowa St. or ISU)
                homeTeamName = homeTeamStats.find("div", class_="ScoreCell__TeamName").get_text()
                awayTeamName = awayTeamStats.find("div", class_="ScoreCell__TeamName").get_text()

                # If either team is apart of the games listed by Rithmm, run the following code to determine the outcome. Otherwise, skip
                if gameKeys.count(homeTeamName) > 0 or gameKeys.count(awayTeamName) > 0:
                    # Get the score of both teams
                    homeTeamScore = homeTeamStats.find("div", class_="ScoreCell__Score").get_text()
                    awayTeamScore = awayTeamStats.find("div", class_="ScoreCell__Score").get_text()
                    
                    homeScore = int(homeTeamScore)
                    awayScore = int(awayTeamScore)

                    # Determine which type the bet was, and if the bet won or not. Record whether the bet won or lost as well as the result
                    if gsRow["betType"] == "Under":
                        lineNumber = gsRow["bet"].split(" ",1)[1]
                        if homeScore + awayScore < float(lineNumber):
                            gsRow["WL"] = "W"
                        else:
                            gsRow["WL"] = "L"
                        gsRow["result"] = homeScore + awayScore
                    elif gsRow["betType"] == "Over":
                        lineNumber = gsRow["bet"].split(" ",1)[1]
                        if homeScore + awayScore > float(lineNumber):
                            gsRow["WL"] = "W"
                        else:
                            gsRow["WL"] = "L"
                        gsRow["result"] = homeScore + awayScore
                    elif gsRow["betType"] == "ML":
                        if homeTeamName == gsRow["bet"] and homeScore > awayScore:
                            gsRow["WL"] = "W"
                            gsRow["result"] = homeTeamName
                        elif awayTeamName == gsRow["bet"] and awayScore > homeScore:
                            gsRow["WL"] = "W"
                            gsRow["result"] = awayTeamName
                        else:
                            gsRow["WL"] = "L"
                            gsRow["result"] = homeTeamName if homeScore > awayScore else awayTeamName
                    elif gsRow["betType"] == "Spread":
                        betParsed = gsRow["bet"].split()
                        team = " ".join(betParsed[:-1])
                        spreadNum = float(betParsed[-1])
                        if homeTeamName == team:
                            if homeScore + spreadNum > awayScore:
                                gsRow["WL"] = "W"
                            else:
                                gsRow["WL"] = "L"
                            gsRow["result"] = homeScore - awayScore
                        elif awayTeamName == team:
                            if awayScore + spreadNum > homeScore:
                                gsRow["WL"] = "W"
                            else:
                                gsRow["WL"] = "L"
                            gsRow["result"] = awayScore - homeScore
            gsRows.insert(len(gsRows), gsRow)

        i += 1
        if i > 28:
            break
    # Return the created JSON object
    # print(gsRows)
    # return gsRows
    with open("output.csv","w",newline="") as f:  # python 2: open("output.csv","wb")
        title = "date,teams,dwag,bet,betType,HUMIDITY".split(",") # quick hack
        cw = csv.DictWriter(f,title,delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        cw.writeheader()
        cw.writerows(gsRows)   

getRithmmHistory()
# getGameData()