import time
import overwatcher

w = overwatcher.OverWatcher()

tag = 'Mei#11561'
platform = 'pc'
region = 'us'


def wait():
    while not w.can_make_request():
        time.sleep(1)


def tag_test(tag, platform, region):
    #runs basic tests to fetch info.
    print('testing with tag {}, platform {}, in region {}'.format(tag, platform, region))
    print('getting basic profile info (level, time played, competetive rank, etc.)')
    print(w.get_profile(tag, platform, region))
    print('getting achievements')
    print(w.get_achievements(tag, platform, region))
    print('getting general gameplay stats (total damage done, total healing done, cards, etc.)')
    print(w.get_general_stats(tag, platform, region))
    print('getting stats for all heroes in quick play')
    heroes = [hero for hero in overwatcher.heroes]
    print(w.get_heroes_stats(tag, heroes, platform, region))
    print('getting playtime for all heroes in quick play')
    print(w.get_hero_playtime(tag, platform, region))
    print('getting stats for all heroes in comptitive play')
    print(w.get_heroes_stats(tag, heroes, platform, region, mode='competitive-play'))
    print('getting playtime for all heroes in competitive play')
    print(w.get_hero_playtime(tag, platform, region, mode='competitive-play'))


tag_test(tag, platform, region)
