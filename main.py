import requests
import time
import json
from datetime import datetime


class ApiHandler:
    def __init__(self, api_url, auth_token):
        self.api_url = api_url
        self.auth_token = auth_token
        self.matchDayTeams = []
        self.current_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.headers = {
            "X-Auth-Token": auth_token
        }

    def get_data(self, type):
        try:
            api = self.api_url + type
            response = requests.get(api, headers=self.headers)

            if response.status_code == 200:
                # API call was successful
                data = response.json()
                return data
            else:
                # Handle error cases
                print(f"Error: {response.status_code}")
                print(response.text)
                return None

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def main(self):
        #TODO 
        #ADD TODAYS MATCH DAYS
        competitions = self.extract_competitions()

        for competition in competitions:
            print("Calculating bets for: ", competition['name'])
            matches = self.getTodaysMatches(competition)
            self.proccessTodaysMatches(matches)
            break;
        
        return competitions
    
    def proccessTodaysMatches(self, data): #DOESNT ACTUALLY PROCCESS TODAY, IT PROCESSES FOR THE WHOLE ROUND, 
                                           #MAKE IT GET ONLY TODAYS MATCHES, OR JUST PRINT ALL BETS FOR WHOLE ROUND
        #call proccessHeadToHead somewhere here
        for matches in data["matches"]:
            homeTeamId = matches["homeTeam"]["id"]
            awayTeamId = matches["awayTeam"]["id"]
            hometeamName = matches["homeTeam"]["name"]
            awayteamName = matches["awayTeam"]["name"]
            #TODO
            #SAVE THE 5 MATCHES AND 10 MATCHES, AND USE THAT TO PASS TO THE FUNCTIONS SO THE API ISNT CALLED EVERY TIME, HAVE TO ALSO MODIFY THE OTHER FUNCTIONS
            lastFiveMatchesHome = self.getRecentMatches(homeTeamId, 5)
            lastTenMatchesHome = self.getRecentMatches(homeTeamId, 10)
            lastFiveMatchesAway = self.getRecentMatches(awayTeamId, 5)
            lastTenMatchesAway = self.getRecentMatches(awayTeamId, 10)

            underGoals = [1.5, 2.5, 3.5, 4.5]
            
            print("Calculating bets for: ", hometeamName, " vs ", awayteamName)
            print("Under goals:")
            for goals in underGoals:
                print("-----------------Calculating under goals: ", goals, "-----------------")
                self.calculateAndPrintUnderGoals(homeTeamId, hometeamName, lastFiveMatchesHome, goals, 5)
                self.calculateAndPrintUnderGoals(homeTeamId, awayteamName, lastTenMatchesHome, goals, 10)
                self.calculateAndPrintUnderGoals(awayTeamId, hometeamName, lastFiveMatchesAway, goals, 5)
                self.calculateAndPrintUnderGoals(awayTeamId, awayteamName, lastTenMatchesAway, goals, 10)
            print("-----------------Calculating average goals-----------------")
            print(hometeamName," averaged ", self.averageGoals(homeTeamId, lastFiveMatchesHome), " in the last 5 matches")
            print(awayteamName," averaged ", self.averageGoals(awayTeamId, lastFiveMatchesAway), " in the last 5 matches")
            print(hometeamName," averaged ", self.averageGoals(homeTeamId, lastTenMatchesHome), " in the last 10 matches")
            print(awayteamName," averaged ", self.averageGoals(awayTeamId, lastTenMatchesAway), " in the last 10 matches")
        



            break
            #self.proccessHeadToHead(homeTeamId, awayTeamId)
        
        return None
    
    def proccessHeadToHead(self, homeTeamId, awayTeamId):
        return None
    
    def processData(self, teamId):
        return None
    
    def calculateAndPrintUnderGoals(self, teamId, teamName, matches, underGoals, numberOfMatches): 
        underGoalsCount, percentageUnderGoals = self.underGoals(matches, underGoals)
        print(f"LAST {numberOfMatches} MATCHES - The percentage of matches that {teamName} scored under ", underGoals, " goals is: ", percentageUnderGoals, f" - {underGoalsCount}/{numberOfMatches} GAMES")
        underGoalsCount, percentageUnderGoals = self.underGoalsForTeam(matches, teamId, underGoals)
        print(f"LAST {numberOfMatches} MATCHES - The percentage of matches that {teamName} played were under ", underGoals, " goals is: ", percentageUnderGoals, f" - {underGoalsCount}/{numberOfMatches} GAMES")
        return None
    

    def averageGoals(self, teamId, matches):
        sum = 0
        counter = 0
        if matches:
            for match in matches:
                if match["homeTeam"]["id"] == teamId:
                    homeTeamGoals = match["score"]["fullTime"]["home"]
                    sum += homeTeamGoals
                    counter += 1
                        
                elif match["awayTeam"]["id"] == teamId:
                    awayTeamGoals = match["score"]["fullTime"]["away"]
                    sum += awayTeamGoals
                    counter += 1

        return sum / counter

    #make the exact same function as below to calculate under goals, but calculate the goals for only one team
    def underGoalsForTeam(self, matches, teamId, underGoals):
        under_goals_count = 0
        total_matches = len(matches)

        for match in matches:
            if match["homeTeam"]["id"] == teamId:
                home_goals = match["score"]["fullTime"]["home"]
                if home_goals < underGoals:
                    under_goals_count += 1
                            
            elif match["awayTeam"]["id"] == teamId:
                away_goals = match["score"]["fullTime"]["away"]
                if away_goals < underGoals:
                    under_goals_count += 1
        
        percentage_under_goals = (under_goals_count / total_matches) * 100

        return under_goals_count, percentage_under_goals
    
    def underGoals(self, matches, underGoals):
        under_goals_count = 0
        total_matches = len(matches)

        for match in matches:
            home_goals = match["score"]["fullTime"]["home"]
            away_goals = match["score"]["fullTime"]["away"]
            
            if home_goals + away_goals < underGoals:
                under_goals_count += 1

        percentage_under_goals = (under_goals_count / total_matches) * 100

        return under_goals_count, percentage_under_goals



    def getRecentMatches(self, teamId, numberOfMatches): 
        team = self.getAllMatchesOfTeam(teamId)
        return team[-numberOfMatches:]

    def getTodaysMatches(self, competition):
        print("Retrieving todays matches for:", competition['name'])
        matches = self.get_data(f"competitions/{competition['id']}/matches/?matchday={competition['matchday']}")
        return matches
    
    def getCompetitionsTeams(self, competitions):
        teams_dict = {}
        for competition in competitions:
            teams = self.process_competitions(competition['id'])
            teams_dict[competition['name']] = teams
            break
            time.sleep(10)
    
        return teams_dict
    
    """def getAllMatchesOfTeam(self, team):
        for key, value in team.items():
            print("Teams in:", key)
            for team in value:
                data = self.get_data(f"teams/{team['id']}/matches/")
                json_data = json.dumps(data)
                target_date = "2023-11-13T21:30:00Z"  # The date you want to filter by
                matches = data["matches"]
                filtered_matches = [match for match in matches if match["utcDate"] < target_date]
                break
        return filtered_matches
    """
    def getAllMatchesOfTeam(self, teamId):
        data = self.get_data(f"teams/{teamId}/matches/")
        json_data = json.dumps(data)
        target_date = "2023-11-13T21:30:00Z"  # The date you want to filter by
        matches = data["matches"]
        filtered_matches = [match for match in matches if match["utcDate"] < target_date]
        return filtered_matches


    def process_competitions(self, id):
        data = self.get_data(f"competitions/{id}/teams")
        teams = []

        for team in data["teams"]:
            team_id = team["id"]
            team_name = team["name"]
            team_info = {"id": team_id, "name": team_name}
            teams.append(team_info)

        return teams


    def extract_competitions(self):
        data = self.get_data("competitions")
        competitions = []

        for competition in data["competitions"]:
            competition_info = {
                "id": competition["id"],
                "name": competition["name"],
                "matchday": competition["currentSeason"]["currentMatchday"]
            }
            competitions.append(competition_info)

        return competitions
    



# Example usage
api_url = "https://api.football-data.org/v4/"
auth_token = "b28f448742d8405a87c94dbdd9637081"

api_handler = ApiHandler(api_url, auth_token)

api_data = api_handler.main()


