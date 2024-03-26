import json

def getTeamData(jsonList, teamName):
    teamData = [team for team in jsonList if team['Team'] == teamName]
    return teamData[0]

def chooseWinner(team1, team2):
    team1Score = 0
    team2Score = 0

    adjEMfactor = 4
    adjOfactor = 10
    adjDfactor = 10
    adjTfactor = 6
    adjSOSEMfactor = 4

    if float(team1['AdjEM']) > float(team2['AdjEM']):
        team1Score += adjEMfactor
    elif float(team1['AdjEM']) < float(team2['AdjEM']):
        team2Score += adjEMfactor
    
    if float(team1['AdjO']) > float(team2['AdjO']):
        team1Score += adjOfactor
    elif float(team1['AdjO']) < float(team2['AdjO']):
        team2Score += adjOfactor

    if float(team1['AdjD']) > float(team2['AdjD']):
        team1Score += adjDfactor
    elif float(team1['AdjD']) < float(team2['AdjD']):
        team2Score += adjDfactor

    if float(team1['AdjT']) < float(team2['AdjT']):
        team1Score += adjTfactor
    elif float(team1['AdjT']) > float(team2['AdjT']):
        team2Score += adjTfactor

    if float(team1['SOSAdjEM']) > float(team2['SOSAdjEM']):
        team1Score += adjSOSEMfactor
    elif float(team1['SOSAdjEM']) < float(team2['SOSAdjEM']):
        team2Score += adjSOSEMfactor

    if team1Score > team2Score:
        return team1['Team']
    else:
        return team2['Team']

def makeBracket():
    with open('kenpom.json') as team_file:
        dataString = team_file.read()

    teamData = json.loads(dataString)

    r64 = [
            'Connecticut','Stetson',
            'Florida Atlantic','Northwestern',
            'San Diego St.','UAB',
            'Auburn','Yale',
            'BYU','Duquesne',
            'Illinois','Morehead St.',
            'Washington St.','Drake',
            'Iowa St.','South Dakota St.',
            'North Carolina','Wagner',
            'Mississippi St.','Michigan St.',
            'Saint Marys','Grand Canyon',
            'Alabama','Charleston',
            'Clemson','New Mexico',
            'Baylor','Colgate',
            'Dayton','Nevada',
            'Arizona','Long Beach St.',
            'Houston','Longwood',
            'Nebraska','Texas A&M',
            'Wisconsin','James Madison',
            'Vermont','Duke',
            'Texas Tech','N.C. State',
            'Kentucky','Oakland',
            'Florida','Colorado',
            'Marquette','Western Kentucky',
            'Purdue','Grambling St.',
            'Utah St.','TCU',
            'Gonzaga','McNeese St.',
            'Kansas','Samford',
            'South Carolina','Oregon',
            'Creighton','Akron',
            'Texas','Colorado St.',
            'Tennessee','Saint Peters',
          ]
    r32 = []
    r16 = []
    r8 = []
    r4 = []
    r2 = []
    # Round of 64
    for x in range(0, 64, 2):
        team1 = getTeamData(teamData, r64[x])
        team2 = getTeamData(teamData, r64[x+1])
        r32.append(chooseWinner(team1,team2))
    # Round of 32
    for x in range(0, 32, 2):
        team1 = getTeamData(teamData, r32[x])
        team2 = getTeamData(teamData, r32[x+1])
        r16.append(chooseWinner(team1,team2))
    # Sweet 16
    for x in range(0, 16, 2):
        team1 = getTeamData(teamData, r16[x])
        team2 = getTeamData(teamData, r16[x+1])
        r8.append(chooseWinner(team1,team2))
    # Elite 8
    for x in range(0, 8, 2):
        team1 = getTeamData(teamData, r8[x])
        team2 = getTeamData(teamData, r8[x+1])
        r4.append(chooseWinner(team1,team2))
    # Final 4
    for x in range(0, 4, 2):
        team1 = getTeamData(teamData, r4[x])
        team2 = getTeamData(teamData, r4[x+1])
        r2.append(chooseWinner(team1,team2))
    # Championship
    team1 = getTeamData(teamData, r2[0])
    team2 = getTeamData(teamData, r2[1])
    champion = chooseWinner(team1,team2)

    print("-------------------------------------------------")
    print("Round of 64")
    print(r64)
    print("-------------------------------------------------")
    print("Round of 32")
    print(r32)
    print("-------------------------------------------------")
    print("Sweet 16")
    print(r16)
    print("-------------------------------------------------")
    print("Elite 8")
    print(r8)
    print("-------------------------------------------------")
    print("Final 4")
    print(r4)
    print("-------------------------------------------------")
    print("Championship")
    print(r2)
    print("-------------------------------------------------")
    print("Champion:")
    print(champion)
makeBracket()