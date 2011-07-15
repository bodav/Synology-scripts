"""
    Torrent Tracker Proxy Server
    
    Some info about setup here...
"""

import urlparse
import urllib
import copy

class tracker_request:
    def __init__(self, reqStr):
        self.requestString = reqStr
        self.headers = {}
        self.torrentInfoHash = None
        self.originalTrackerUrl = None #call with geturl()
        self.alteredTrackerUrl = None #call with geturl()
        self.leftValue = 0
        self.isScrapeRequest = False
        self.isStartRequest = False
        self.__parseRequestString(reqStr)
    
    def __toRequestString(self, trackerUrl, headers):
        self.alteredTrackerUrl = trackerUrl
        
        requestStr = "GET " + trackerUrl.path + "?" + trackerUrl.query + " HTTP/1.1\n"
        
        for key, value in self.headers.items():
            requestStr += key + ": " + value + "\n"
        
        return requestStr
    
    def createRequest(self):
        return self.__toRequestString(self.originalTrackerUrl, self.headers)
    
    def createStallDownloadRequest(self, leftValue):
        splitQueryStr = self.originalTrackerUrl.query.split("&")
        
        if splitQueryStr.count("event=completed") != 0:
            splitQueryStr.pop(splitQueryStr.index("event=completed"))
        
        
        for index, param in enumerate(splitQueryStr[:]):
            if param.startswith("downloaded"):
                splitQueryStr[index] = param[0:11] + "0"
            elif param.startswith("uploaded"):
                splitQueryStr[index] = param[0:9] + "0"
            elif param.startswith("corrupt"):
                splitQueryStr[index] = param[0:8] + "0"
            elif param.startswith("left"):
                splitQueryStr[index] = param[0:5] + leftValue
        
        newQuery = "&".join(splitQueryStr)
        newUrl = self.originalTrackerUrl.scheme + "://" + self.originalTrackerUrl.netloc + self.originalTrackerUrl.path + "?" + newQuery
        newUrlParsed = urlparse.urlparse(newUrl)
        
        return self.__toRequestString(newUrlParsed, self.headers)
    
    def __parseRequestString(self, reqStr):
        reqSplit = reqStr.split("\n")
        urlPart = reqSplit[0].split(" ")[1]
        
        for header in reqSplit:
            if not header.startswith("GET"):
                splitHeaderString = header.split(" ")
                
                if len(splitHeaderString) > 1:
                    if splitHeaderString[0]:
                        self.headers[splitHeaderString[0].strip(":").strip()] = splitHeaderString[1].strip("\r").strip()
        
        tmpUrl = "http://" + self.headers["Host"] + urlPart
        parsedTmpUrl = urlparse.urlparse(tmpUrl)
        parsedQueryStr = urlparse.parse_qs(parsedTmpUrl.query)
        
        self.originalTrackerUrl = parsedTmpUrl
        self.isScrapeRequest = parsedTmpUrl.path.find("scrape") > -1
        self.isStartRequest = parsedTmpUrl.query.find("&event=started") > -1
        
        if not self.isScrapeRequest:
            self.torrentInfoHash = parsedQueryStr["info_hash"][0]
            self.leftValue = parsedQueryStr["left"][0]






if __name__ == "__main__":
    testcase = """GET /announce.php?info_hash=%19%5b%bf%f1%2a%23%b1%ff%3f%ea%ad%01b%27%2a%e2p%b1%cb%b7&peer_id=-UT2210-%2ab%ad%a7%db%a3%cbU0%20%5dM&port=20459&uploaded=0&downloaded=0&left=194136669&corrupt=0&key=0FE1A1ED&event=started&numwant=200&compact=1&no_peer_id=1 HTTP/1.1
Host: tracker.filepost.org:81
User-Agent: uTorrent/2210(25130)
Accept-Encoding: gzip
Connection: Close
    
"""

    testcase2 = """GET /725676/vJSTVT4N/announce?info_hash=%9a%95-w%e8%af%b9%2a%cd%bf%3d%2bD%ac%3a%a4%27%0cK1&peer_id=-UM1020-%8f%5b%9d%2a%5bG%f6%ae%be%26%c0%96&port=41118&uploaded=0&downloaded=0&left=419686180&corrupt=0&key=B655BEA9&event=completed&numwant=200&compact=1&no_peer_id=1&ipv6=fe80%3a%3aca2a%3a14ff%3afe1b%3add82 HTTP/1.1
Host: hank.cheggit.net:2710
User-Agent: uTorrentMac/1020(23439)
Accept-Encoding: gzip
        
"""

    testcase3 = """GET /725676/vJSTVT4N/announce?info_hash=%9a%95-w%e8%af%b9%2a%cd%bf%3d%2bD%ac%3a%a4%27%0cK1&peer_id=-UM1020-%8f%5b%9d%2a%5bG%f6%ae%be%26%c0%96&port=41118&uploaded=0&downloaded=0&left=419686180&corrupt=0&key=B655BEA9&numwant=200&compact=1&no_peer_id=1&ipv6=fe80%3a%3aca2a%3a14ff%3afe1b%3add82 HTTP/1.1
Host: hank.cheggit.net:2710
User-Agent: uTorrentMac/1020(23439)
Accept-Encoding: gzip
        
"""

tr = TrackerRequest(testcase3)
print tr.createStallDownloadRequest("41")

