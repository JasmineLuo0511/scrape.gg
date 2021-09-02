from scrapegg import scrapeGG
init = scrapeGG('luckypants177')

import json # for testing

# test match api class
recent = init.getMatch(1)
# second = init.getMatch(2)
# top10 = init.getMatchSequence(10)

# match class tests
# print(json.dumps(recent.game_player_names(True), indent=2))
# print(recent.game_player_names(True)) # stable

# print(json.dumps(recent.self_stats(), indent=2))
# print(recent.self_stats()) # stable

# print(json.dumps(recent.player_stats('API'), indent=2))
# print(recent.player_stats('API')) # stable

# print(json.dumps(recent.overview(), indent=2))
# print(recent.overview()) # unstable

# print(json.dumps(recent.build(), indent=2))
# print(recent.build()) # unstable


# profile details class
profile = init.getProfile() # stable
# print(json.dumps(profile.recently_played_with(), indent=2))
# print(profile.recently_played_with()) # stable

# print(json.dumps(profile.queue_stats('Total'), indent=2))
# print(profile.queue_stats('Total')) # stable

# print(json.dumps(profile.top_played_champions(), indent=2))
# print(profile.top_played_champions()) # not really implemented but ok

print(json.dumps(profile.rank('Ranked Solo'), indent=2))
# print(profile.rank('Ranked Solo')) # not really implemented but ok

init.quit()