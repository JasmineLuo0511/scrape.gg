# wrapper
import re
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class match:
    def __init__(self, match, username):
        self.match = match
        self.gamestats = match.find_elements_by_class_name("GameStats")[0]
        self.gamesetting = match.find_elements_by_class_name("GameSettingInfo")[0]
        self.playerstats = match.find_elements_by_class_name("Stats")[0]
        self.kda = match.find_elements_by_class_name('KDA')[0]
        self.username = username
        self.player_names = {}
    
    def game_player_names(self, is_win):
        if (len(self.player_names) > 0): # if already instantiated
            return self.player_names

        # not set yet
        teams = self.match.find_elements_by_class_name("FollowPlayers")[0].find_elements_by_class_name("Team")
        for team in teams:
            curr = {}
            is_self = False
            self_team = False # check which side player is on
            for summoner in team.find_elements_by_class_name("Summoner"):
                username = class_content_search(summoner, ["SummonerName", "Link"])
                champion = class_content_search(summoner, ["ChampionImage", "__sprite"])
                curr[username] = champion # all default to loser
                if (username == self.username):
                    is_self = True

            # set curr to either winner or loser
            if (is_self and is_win) or (not is_self and not is_win):
                winner = curr # own team won, is on right team
            elif (is_self and not is_win) or (not is_self and is_win):
                loser = curr 
        return {
            'winner': winner,
            'loser': loser
        }
                
    # stats before clicking downarrow
    def self_stats(self):
        # game stats information block
        queue_type = class_content(self.gamestats, "GameType")
        is_win = class_content(self.gamestats, "GameResult") == 'Victory'
        game_length = class_content(self.gamestats, "GameLength")
        game_time = class_content_search(self.gamestats, ["TimeStamp", "_timeago"])

        # game setting information block
        champion_played_wrapper = self.gamesetting.find_elements_by_class_name("ChampionName")[0]
        champion_played = a_textcontent(champion_played_wrapper)
        # +runes

        # game stats information block
        level = class_content(self.playerstats, "Level")
        cs_wrapper = class_content_search(self.playerstats, ["CS", "tip"])
        cs_per_min = cs_wrapper[cs_wrapper.find("(")+1:cs_wrapper.find(")")]
        cs_raw = cs_wrapper.replace('(' + cs_per_min + ')', '')

        pkill = class_content(self.playerstats, "CKRate")

        try:
            mmr_wrapper = self.playerstats.find_elements_by_class_name("MMR")[0]
            mmr = mmr_wrapper.find_elements_by_tag_name('b')[0].get_attribute('innerHTML')
        except:
            mmr = 'N/A'

        # kda stats information block
        kill_count = class_content_search(self.kda, ["KDA", "Kill"])
        assist_count = class_content_search(self.kda, ["KDA", "Assist"])
        death_count = class_content_search(self.kda, ["KDA", "Death"])
        kda_ratio = class_content_search(self.kda, ["KDARatio", "KDARatio"])

        # +items

        # player names
        teams = self.game_player_names(is_win)

        return {
            'win': is_win,
            'queue_type': queue_type.strip(),
            'time': game_time,
            'length': game_length,
            'players': {
                'champion_played': champion_played,
                'winner': teams['winner'],
                'loser': teams['loser']
            },
            'gameplay': {
                'level': level.strip(),
                'cs' : cs_raw.strip(),
                'cs_per_min': cs_per_min,
                'pkill' : pkill.strip(),
                'build': [],
                'kda': {
                    'overall': kda_ratio,
                    'kill': kill_count,
                    'death': death_count,
                    'assist': assist_count
                },
                'tieravg': mmr
            }        
        }

    def click_expansion(self):
        # click expand button
        link = self.match.find_element_by_id('right_match')
        link.click()

        # wait until detaillayout is expanded
        WebDriverWait(self.match, 10).until(
            EC.presence_of_element_located((
            By.CLASS_NAME, "MatchDetailLayout")))

        # extraction logic
        return self.match.find_elements_by_class_name("MatchDetailLayout")[0]

    def player_stats(self, username):
        matchdetail = self.click_expansion()

        # find username row
        head = matchdetail.find_element(By.PARTIAL_LINK_TEXT, username)

        # find row container from username row
        parent = head.find_element_by_xpath('../..')

        # data from row container
        champion_played = class_content_search(parent, ["ChampionImage", "Image"])
        level = class_content_search(parent, ["ChampionImage", "Level"])
        elo = class_content(parent, "Tier")

        opscore = class_content_search(parent, ["OPScore", "Text"])
        opscore_rank = class_content_search(parent, ["OPScore", "Badge"])

        kda_ratio = class_content_search(parent, ["KDA", "KDARatio"])
        kill = class_content_search(parent, ["KDA", "Kill"])
        assist = class_content_search(parent, ["KDA", "Death"])
        death = class_content_search(parent, ["KDA", "Assist"])
        
        pkill = class_content_search(parent, ["KDA", "CKRate"])

        damage = class_content_search(parent, ["Damage", "ChampionDamage"])

        ward = parent.find_elements_by_class_name("Ward")[0]
        ward_title = ward.get_attribute('title').split('<br>')
        control = remove_nonnumerical(ward_title[0])
        placed = remove_nonnumerical(ward_title[1])
        destroyed = remove_nonnumerical(ward_title[2])

        cs = class_content_search(parent, ["CS", "CS"])
        cs_per_min = class_content_search(parent, ["CS", "CSPerMinute"]).replace('/m', '')

        # look in header for game status
        header_wrapper = parent.find_element_by_xpath('../..').find_elements_by_class_name("Header")[0]
        is_victory = class_content_search(header_wrapper, ["Row","HeaderCell", "GameResult"])

        return {
            'username': username,
            'win': is_victory,
            'player': {
                'elo': remove_spaces(elo),
                'champion_played': champion_played,
                'rank': opscore_rank, # mvp, 2nd, 3rd (...)
                'opscore': opscore,
            },
            'gameplay': {
                'level': level,
                'cs' : cs,
                'cs_per_min': cs_per_min,
                'pkill' : pkill,
                'build': [],
                'kda': {
                    'overall': kda_ratio,
                    'kill': kill,
                    'death': death,
                    'assist': assist
                },
                'damage': damage,
                'wards': {
                    'control': control,
                    'total': placed,
                    'destroyed': destroyed
                }
            }        
        }

    def overview(self):
        is_win = class_content(self.gamestats, "GameResult") == 'Victory'
        players = self.game_player_names(is_win)

        matchdetail = self.click_expansion()
        result = matchdetail.find_elements_by_class_name("GameResult")[0] # victory or loss

        inner_wrapper = result.find_element_by_xpath('..')
        inner = inner_wrapper.get_attribute('innerHTML')
        team = find_between(inner, '(', ')') # result of team with player on it - op.gg auto formats like this
        
        summary = matchdetail.find_elements_by_class_name('Summary')[0]

        # objective assignments
        # assumes that game is lost
        winner, loser = (0, 0)
        extract_number = lambda inp: remove_nonnumerical(inp.get_attribute("innerHTML"))
        objectives = summary.find_elements_by_class_name("ObjectScore")
        loser = {
            'baron': extract_number(objectives[0]),
            'dragon': extract_number(objectives[1]),
            'tower': extract_number(objectives[2]),
        }
        winner = {
            'baron': extract_number(objectives[3]),
            'dragon': extract_number(objectives[4]),
            'tower': extract_number(objectives[5]),
        }

        if (is_win): # if is_win, swap
            loser, winner = winner, loser

        red = {}
        blue = {}

        # total kill/gold assignments
        totals = summary.find_elements_by_class_name("total--container")
        left = {}
        right = {}
        for container in totals:
            _left = class_content(container, "graph--data__left")
            _right = class_content(container, "graph--data__right")
            if class_content(container, "graph--title") == "Total Kill":
                left['kill'] = _left
                right['kill'] = _right
            elif class_content(container, "graph--title") == "Total Gold":
                left['gold'] = _left
                right['gold'] = _right
            else:
                print("error")

        # assignment to red/blue teams        
        if (is_win and team == "Red Team") or (not is_win and team != "Red Team"):
            # won, red team is player
            # lost, blue team is enemy
            red = left
            red["objectives"] = winner
            blue = right
            blue["objectives"] = loser
        else:
            red = right
            red["objectives"] = loser
            blue = left
            blue["objectives"] = winner
        
        return {
            'players': players,
            'player_stats': {
                'team': team,
                'result': result.text
            },
            'blue': blue,
            'red': red
        }

    # player stats
    def build(self):
        item = [
            ('0 min', ['potion', 'dorans', 'ward']),
            ('5 min', ['potion', 'dorans', 'ward']),
            # extract all -min items
        ]
        skill = [
            ('1', 'Q')
            ('2', 'W')
            # extract all (order, ability)
            ('16', 'R')
        ]
        runes = {
            'sorcery': [],
            'domination': [],
            'runestats': []
        }

        return {
            'item': item,
            'skill': skill,
            'runes': runes
        }

# helper functions

# extract first element content (by class)
def class_content(parent, className):
    first_element = parent.find_elements_by_class_name(className)[0]
    return first_element.get_attribute('innerHTML')
def a_textcontent(parent):
    first_element = parent.find_elements_by_tag_name('a')[0]
    return first_element.get_attribute('innerHTML')

# classList is [firstClassToFind, secondClassToFind, etc.]
def class_content_search(parent, classList):
    head = parent
    while classList:
        head = head.find_elements_by_class_name(classList[0])[0]
        classList.pop(0)
    return head.get_attribute('innerHTML')

def remove_spaces(inp):
    return "".join(inp.split())

def remove_nonnumerical(inp):
    return re.sub("[^0-9]", "", inp)
    
def find_between(string, char_start, char_end):
    return string[string.find(char_start)+1 : string.find(char_end)]