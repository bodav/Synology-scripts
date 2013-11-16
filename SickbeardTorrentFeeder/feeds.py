import urllib, urllib2, json, gzip, config
import xml.etree.ElementTree as ET
from StringIO import StringIO


class FeedItem(object):
    def __init__(self, title, uri, source):
        self.title = title
        self.uri = uri
        self.source = source

def get_combined_feeds():
    print("Getting combined feeds...")
    eztv = get_eztv_feed()
    kateztv = get_katph_eztv_feed()
    ettv = get_katph_ettv_feed()
    vtv = get_katph_vtv_feed()

    combined = eztv + kateztv + ettv + vtv

    print("Total items in combined feeds: {0}".format(len(combined)))
    return combined

def get_eztv_feed():
    print("Getting EZTV.it feed...")
    data = urllib2.urlopen(config.EZTV_FEED_URL).read()
    root = ET.fromstring(data)
    items = []

    try:
        for item in root.iter("item"):
            if item.find("link").text.startswith("magnet"):
                items.append(FeedItem(item.find("title").text, 
                    item.find("link").text,
                    "EZTV.it"))
    except Exception as ex:
        print("Error getting EZTV.it feed, Error: {0}".format(ex))

    print("Total items in EZTV.it feed: {0}".format(len(items)))
    return items

def get_katph_eztv_feed():
    items = _get_katph_feed(config.EZTV_KAT_FEED_URL, "KATPH.EZTV")
    print("Total items in katph eztv feed: {0}".format(len(items)))
    return items

def get_katph_ettv_feed():
    items = _get_katph_feed(config.ETTV_FEED_URL, "KATPH.ETTV")
    print("Total items in katph ettv feed: {0}".format(len(items)))
    return items

def get_katph_vtv_feed():
    items = _get_katph_feed(config.VTV_FEED_URL, "KATPH.VTV")
    print("Total items in katph vtv feed: {0}".format(len(items)))
    return items

def _get_katph_feed(url, source):
    items = []
    page = 1

    try:
        while page <= config.KATPH_FEED_PAGES:
            data = urllib2.urlopen(url.format(page)).read()
            root = ET.fromstring(data)

            for item in root.iter("item"):
                items.append(
                    FeedItem(item.find("title").text,
                             item.find("torrent:magnetURI", 
                                       namespaces=config.NAMESPACES).text,
                             source))
            page += 1

    except Exception as err:
        print("Error getting katph feed {0}, Error: {1}".format(url, err))

    return items



def search_katph_feed(showname, season, episode):
    providers = " OR ".join(config.SEARCH_ALLOWED_PROVIDERS)
    args = "{0} {1} category:tv season:{2} episode:{3}/?rss=1".format(
        showname, providers, season, episode)
    url = "{0}{1}".format(config.KATPH_BASE_SEARCH_URL, args)
    print "KAT.PH search feed url: {0}".format(url)

    items = []

    try:
        data = urllib2.urlopen(url).read()
        root = ET.fromstring(data)

        for item in root.iter("item"):
            items.append(FeedItem(item.find("title").text, 
                                  item.find("torrent:magnetURI", 
                                            namespaces=config.NAMESPACES).text,
                                  "KAT.PH search"))
    except Exception as ex:
        print("Error searching kat.ph, Error: {0}".format(ex))

    return items


if __name__ == "__main__":
    get_combined_feeds()
