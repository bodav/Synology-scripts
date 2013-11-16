import config
import urllib, urllib2, json

def get_missed_episodes():
    print("Getting missed episodes from Sickbeard")
    api = SickbeardApi()
    missed = []

    for episode in api.get_future_missed()["data"]["missed"]:
        missing = Episode(episode["show_name"].replace("'", ""), 
                          episode["season"], 
                          episode["episode"], 
                          episode["quality"])
        missed.append(missing)
        print("Found missed episode: {0}".format(missing.get_title()))

    print("Found {0} missed episodes".format(len(missed)))
    return missed


def get_backlogged_episodes():
    print("Getting backlogged episodes from Sickbeard")
    api = SickbeardApi()
    backlogged = []
    shows = api.get_all_shows()["data"]

    for showkey in shows:
        seasons = api.get_show_seasons(showkey)["data"]

        for seasonkey in seasons:
            for episodekey in seasons[seasonkey]:
                if seasons[seasonkey][episodekey]["status"] == "Wanted":
                    print("Found backlogged episode: {0} - S{1}E{2}".format(
                        shows[showkey]["show_name"], seasonkey, episodekey))

                    backlogged.append(Episode(
                        shows[showkey]["show_name"].replace("'", ""), 
                        seasonkey, episodekey, 
                        seasons[seasonkey][episodekey]["quality"]))

    return backlogged


class SickbeardApi(object):

    def get_future_missed(self):
        return self._get("future", **{"type": "missed", "paused": "0"})

    def get_all_shows(self):
        return self._get("shows", **{"paused": "0"})

    def get_show_seasons(self, show_tvdbid):
        return self._get("show.seasons", **{"tvdbid": show_tvdbid})

    def _get(self, cmd, **kwargs):
        url =  "{0}{1}/?cmd={2}&{3}".format(
            config.SICKBEARD_API_URL, config.SICKBEARD_API_KEY, 
            cmd, urllib.urlencode(kwargs))
        #print("SBAPI: Requesting " + url)
        data = urllib2.urlopen(url).read()
        return json.loads(data)


class Episode(object):
    def __init__(self, showname, season, episode, quality):
        self.showname = showname
        self.season = str(season)
        self.episode = str(episode)
        self.quality = quality

    def get_title(self):
        return "{0} S{1} E{2}".format(
            self.showname, self.season, self.episode)

    def get_title_search_strings(self):
        #show name SxxExx
        #show name xxXxx
        str1 = "{0} S{1}E{2}".format(
            self.showname, self.season.zfill(2), self.episode.zfill(2))
        str2 = "{0} {1}x{2}".format(
            self.showname, self.season, self.episode.zfill(2))
        return (str1, str2)

    def get_quality(self):
        if self.quality == "HD":
            return "720p"
        else:
            return "HDTV"

    def matches_title_and_quality(self, title):
        search_title1, search_title2 = self.get_title_search_strings()

        if search_title1 in title or search_title2 in title:
            quality = self.get_quality()
            if quality == "HDTV" and quality in title and "720p" not in title:
                return True
            elif quality == "720p" and quality in title:
                return True

        return False


if __name__ == "__main__":
    get_sickbeard_missed_episodes()
    get_sickbeard_backlogged_episodes()
