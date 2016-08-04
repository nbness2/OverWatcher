from pylinkedlists import DoubleLinkedList
import time
import requests

# requests from https://api.lootbox.eu/ api V0.6

#regions
na = 'us'
us = 'us'
eu = 'eu'
kr = 'kr'
cn = 'cn'
gb = 'global'


#platforms
PC = 'pc'
XBL = 'xbl'
PS4 = 'ps4'

#heroes

hero_mei = 'Mei'
hero_genji = 'Genji'
hero_tracer = 'Tracer'
hero_zenyatta = 'Zenyatta'
hero_dva = 'DVa'
hero_soldier = 'Soldier76'
hero_harambe = 'Winston'
hero_widowmaker = 'Widowmaker'
hero_ana = 'Ana'
hero_mccree = 'Mccree'
hero_pharah = 'Pharah'
hero_zarya = 'Zarya'
hero_torb = 'Torbjoern'
hero_lucio = 'Lucio'
hero_reaper = 'Reaper'
hero_hanzo = 'Hanzo'
hero_mercy = 'Mercy'
hero_bastion = 'Bastion'
hero_junkrat = 'Junkrat'
hero_reinhardt = 'Reinhardt'
hero_roadhog = 'Roadhog'
hero_symmetra = 'Symmetra'

heroes = {
    hero_mei: 'Mei',
    hero_genji: 'Genji',
    hero_tracer: 'Tracer',
    hero_zenyatta: 'Zenyatta',
    hero_dva: 'DVa',
    hero_soldier: 'Soldier76',
    hero_harambe: 'Winston',
    hero_widowmaker: 'Widowmaker',
    hero_ana: 'Ana',
    hero_mccree: 'Mccree',
    hero_pharah: 'Pharah',
    hero_zarya: 'Zarya',
    hero_torb: 'Torbjoern',
    hero_lucio: 'Lucio',
    hero_reaper: 'Reaper',
    hero_hanzo: 'Hanzo',
    hero_mercy: 'Mercy',
    hero_bastion: 'Bastion',
    hero_junkrat: 'Junkrat',
    hero_reinhardt: 'Reinhardt',
    hero_roadhog: 'Roadhog',
    hero_symmetra: 'Symmetra',
}

#gamemodes
mode_quick = 'quick-play'
mode_comp = 'competitive-play'


class OWException(Exception):
    def __init__(self, error, response):
        self.error = error
        self.err_headers = response.headers
        print(self)

    def __str__(self):
        return str(self.error)

    def __eq__(self, other):
        if type(other) == str:
            return self.error == other
        elif type(other) == OWException:
            return self.error == other.error and self.err_headers == other.err_headers
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

errors = {
    400: 'Bad Request',
    401: 'Unauthorized',
    404: 'Data not found',
    429: 'Too many requests',
    500: 'Internal server error',
    503: 'Service Unavailable'
}


def raise_status(response):
    if 'statusCode' in response.json():
        code = response.json()['statusCode']
    else:
        code = response.status_code
    if code == 200:
        return 'nice'
    elif code in errors.keys():
        raise OWException(code, response)
    else:
        raise NotImplementedError('not implemented code: {}'.format(code))


def sanitize_string(tag):
    #replaces # with - and removes spaces
    return tag.replace('#', '-').replace(' ', '')


class RateLimiter:
    #up to max_requests per seconds seconds
    def __init__(self, max_requests, seconds):
        self.max_requests = max_requests
        self.seconds = seconds
        self.requests = DoubleLinkedList()

    def refresh(self):
        t = time.time()
        while len(self.requests) > 0 and self.requests[0] < t:
            self.requests.pop(0)

    def add_request(self):
        self.requests.append(time.time() + self.seconds)

    def request_available(self):
        self.refresh()
        return (len(self.requests) < self.max_requests, self.refresh())[0]


class OverWatcher:

    def __init__(self, region=na, limits=(RateLimiter(100, 10), RateLimiter(36000, 3600))):
        self.region = region
        self.limits = limits

    def can_make_request(self):
        for lim in self.limits:
            if not lim.request_available():
                return False
        return True

    def add_request(self):
        for limit in self.limits:
            limit.add_request()

    def base_request(self, url, tag, platform, region):
        tag = sanitize_string(tag)
        base = 'https://api.lootbox.eu/{}/{}/{}/{}'
        request = requests.get(base.format(platform, region, tag, url))
        raise_status(request)
        self.add_request()
        return request.json()

    def get_achievements(self, tag, platform, region):
        #gets all achievements and wether or not the specified tag has completed each.
        return self.base_request('achievements', tag, platform, region, )

    def get_profile(self, tag, platform, region):
        #gets general profile stats such as account level and games played per mode.
        return self.base_request('profile', tag, platform, region)

    def get_general_stats(self, tag, platform, region, mode=mode_quick):
        #gets general stats for all heroes combined such as Damage Done and Cards
        return self.base_request('{}/allHeroes/'.format(mode), tag, platform, region)

    def get_heroes_stats(self, tag, heroes, platform, region, mode=mode_quick):
        #use the hero_heroname variables from above in your heroes iterable (list) unless you are comfident in your capitalizing abilities.
        heroes = str(heroes).strip('()[]').replace('\'', '').replace(' ', '')
        return self.base_request('{}/hero/{}/'.format(mode, heroes), tag, platform, region)

    def get_hero_playtime(self, tag, platform, region, mode=mode_quick):
        #returns list of hero playtime dictionaries.
        return self.base_request('{}/heroes'.format(mode), tag, platform, region)
