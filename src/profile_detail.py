from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import os
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from utility import *

class profile:
    def __init__(self, source):
        self.source = source

    def top_played_champions(self):
        return {
            '1': {
                'champion': 'Shyvana',
                'games_played': 44,
                'winrate': 0.66,
                'kda': {
                    'overall': 3.88,
                    'kill': 6.8,
                    'death': 3.8,
                    'assist': 7.8
                },
                'cs': 333,
                'cs_per_minute': 30
            }
        }
    #WORK
    def rank(self, type): 
        #Clicks on Ranked Solo 
        nav = self.source.find_element_by_class_name("Navigation")
        
        link = nav.find_element_by_id('right_gametype_soloranked')
        link.click()
        
        WebDriverWait(self.source, 10).until(
            EC.presence_of_element_located((
            By.CLASS_NAME, "GameAverageStats")))

     
        #Finds all teammate names and champions played for past 20 ranked solo/duo games 
        people = []
        champions = []
        teams = self.source.find_elements_by_xpath("//div[@class='Team']//div[@class='Summoner Requester']")
        for team in teams:
            #temp = man.find_elements_by_class_name('SummonerName')
            parent = team.find_element_by_xpath('..')
            temp = parent.find_elements_by_class_name('SummonerName')
            temp2 = parent.find_elements_by_class_name("ChampionImage")  
            for inner in temp:
                user = inner.text
                people.append(user)
            for champ in temp2:
                champName = champ.find_element_by_xpath(".//*").get_attribute("title")
                champions.append(champName) 
        

        
                

        i = 0
        for userName in people:
            
            # a = self.source.find_elements_by_class_name("LastUpdate")
            # updatebutton = self.source.find_elements_by_id("SummonerRefreshButton")[0]
            # ActionChains(self.source).click(updatebutton).perform()
            # WebDriverWait(self.source, 10).until(
            #     lambda wd: a != self.source.find_elements_by_class_name("LastUpdate")[0].text
            # )   
            
            
            self.source.get('https://na.op.gg/summoner/champions/userName=' + userName)
            #print(self.source.current_url)
            currChamp = champions[i]
            if (currChamp.find("'")):
                currChamp= currChamp.replace("'", "', \"'\", '")
                currChamp= "concat('" + item_text+ "')"
            tempNode = self.source.find_element_by_xpath("//td[@data-value = '"+ currChamp +"']")
            print(tempNode.find_element_by_xpath(".//*").text)
            i = i + 1



        return {
            'type': 'Ranked Solo',
            'lp': 61,
            'wlratio': 0.58,
            'win_count': 92,
            'loss_count': 68,
        }


    # bar above match stats
    def queue_stats(self, game_type='Total'): 
        # click correct game_type if specified
        if game_type != 'Total': 
            nav = self.source.find_element_by_class_name("Navigation")
            if (game_type == 'Ranked Solo'):
                link = nav.find_element_by_id('right_gametype_soloranked')
                link.click()
            elif (game_type == 'Ranked Flex'): 
                link = nav.find_element_by_id('right_gametype_flexranked')
                link.click()
        
        WebDriverWait(self.source, 10).until(
            EC.presence_of_element_located((
            By.CLASS_NAME, "GameAverageStats")))

        # get loaded game stats container
        gameavg_container = self.source.find_element_by_class_name("GameAverageStats")

        # win loss ratio data
        win_ratio = gameavg_container.find_elements_by_class_name("WinRatioTitle")[0]
        win = class_content(win_ratio, "win")
        lose = class_content(win_ratio, "lose")

        # kda data
        kda = gameavg_container.find_element_by_xpath("//tr/td[@class='KDA']") # parent tr, with child td class='KDA'
        kill = class_content_search(kda, ["KDA", "Kill"], 'innerHTML')
        assist = class_content_search(kda, ["KDA", "Assist"], 'innerHTML')
        death = class_content_search(kda, ["KDA", "Death"], 'innerHTML')
        kdaratio = class_content_search(kda, ["KDARatio", "KDARatio"], 'innerHTML')
        
        pkill = class_content_search(kda, ["KDARatio", "CKRate"], 'innerHTML')
        pkill = pkill.replace('(<span>', '').replace('%</span>)', '')
        pkill = float(pkill) / 100

        # positioning preference data
        preferred = []
        pref_position = class_content_search(gameavg_container, ["PositionStats", "Content"])
        for position in pref_position.find_elements_by_class_name("PositionStatContent"):
            role = class_content(position, "Name")
            rolerate = class_content_search(position, ["RoleRate"]).find_elements_by_tag_name('b')[0].get_attribute("innerHTML")
            winrate = class_content_search(position, ["WinRatio"]).find_elements_by_tag_name('b')[0].get_attribute("innerHTML")
            
            # validity check
            if (rolerate.isnumeric() and winrate.isnumeric()):
                winrate = float(winrate) / 100 # format
                rolerate = float(rolerate) / 100
                preferred.append({ 'role': role, 'rolerate': rolerate, 'winrate': winrate })

        # champion preferencing data
        champion = {}
        champion_prefer = class_content_search(gameavg_container, ["MostChampion"])
        for position in champion_prefer.find_elements_by_class_name("Content"):
            champion_name = class_content(position, "Name")
            winratio_wrapper  = class_content_search(position, ["WonLose"])
            
            champion_ratio = class_content(winratio_wrapper, "tip")
            champion_ratio = float(champion_ratio.replace('%', '')) / 100
            
            champion_win = class_content(winratio_wrapper, "win")
            champion_lose = class_content(winratio_wrapper, "lose")
            champion_kda = class_content_search(position, ["KDA"]).find_element_by_tag_name("span").get_attribute("innerHTML")
            champion[champion_name] = {
                'winratio': champion_ratio,
                'kda': {
                    'overall': champion_kda,
                    'win': champion_win,
                    'lose': champion_lose
                }
            }

        return {
            'type': game_type, 
            'win': win,
            'loss': lose,
            'kda': {
                'overall': kdaratio,
                'kill': kill,
                'assist': assist,
                'death': death
            },
            'pkill': pkill,
            'top3champions': champion,
            'preferred': preferred
        }

    def recently_played_with(self):
        res = {}
        rank = 1
        summoner_table = self.source.find_element_by_class_name("SummonersMostGameTable").find_element_by_class_name("Body")
        for summoner in summoner_table.find_elements_by_class_name("Row"):
            name = class_content_search(summoner, ["SummonerName", "Link"], 'innerHTML')
            row_container = summoner.find_element_by_xpath("..")
            game_count = class_content(row_container, "GameCount")
            win = class_content(row_container, "Win")
            lose = class_content(row_container, "Lose")

            win_ratio = class_content(row_container, "WinRatio")
            win_ratio = remove_spaces(win_ratio)
            win_ratio = win_ratio.replace('%', '')
            win_ratio = float(win_ratio) / 100

            res[str(rank)] = {
                'username': name,
                'played': game_count,
                'win': remove_spaces(win),
                'lose': remove_spaces(lose),
                'ratio': win_ratio
            }
            rank += 1
        
        if len(res) > 0:
            return res
        else:
            return None

    # -------dont bother until finish everything else-----
    def all_champions(self):
        # https://na.op.gg/summoner/champions/userName=API
        return 'asdf'
    # ----------------------------------------------------