import asynchat
import asyncore
import socket
import string
import urlparse
import urllib
import copy
import sys

class proxy_server(asyncore.dispatcher):

    """Server waits for incomming connections"""
    
    def __init__(self, host, port):
        asyncore.dispatcher.__init__ (self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.tracker_addr = (host, port)
        localhost = ("", port)
        
        self.leftValuesDict = {}
        
        self.bind(localhost)
        self.listen(5)
        print "server running and listening on port: " + str(port)
            
    def handle_accept(self):
        print "Connection from torrentclient"
        print "leftValues: " + repr(self.leftValuesDict)
        proxy_receiver(self, self.accept())


class proxy_receiver(asynchat.async_chat):
    
    """Receives data from the TorrentClient"""
    
    channel_counter = 0
	
    def __init__(self, server, (conn, addr)):
        asynchat.async_chat.__init__(self, conn)
        self.set_terminator ("\r\n\r\n")
        self.server = server
        self.id = self.channel_counter
        self.channel_counter = self.channel_counter + 1
        self.sender = proxy_sender(self, server.tracker_addr)
        self.sender.id = self.id
        self.buffer = ""
	
    def collect_incoming_data(self, data):
        self.buffer = self.buffer + data
    
    def found_terminator(self):
        data = self.buffer
        self.buffer = ""
        print "<==(ReceivedFromClient) (%d) %s" % (self.id, repr(data))
        tr = tracker_request(data)
        
        if tr.isStartRequest:
            self.server.leftValuesDict[tr.torrentInfoHash] = tr.leftValue
        
        newRequest = ""
        
        if tr.isScrapeRequest:
            newRequest = tr.createRequest()
        else:
            print "leftValue: " + self.server.leftValuesDict[tr.torrentInfoHash]
            newRequest = tr.createStallDownloadRequest(self.server.leftValuesDict[tr.torrentInfoHash])
                
        print "==>(SentToTracker) (%d) %s" % (self.id, repr(newRequest))

        self.sender.push(newRequest + "\r\n\r\n")
	
    def handle_close(self):
        print "Receiver closing ID: " + str(self.id)
        
        if len(self.buffer):
            self.found_terminator()
		
        self.sender.close_when_done()
        self.close()


class proxy_sender(asynchat.async_chat):
    
    """Sends data to the TorrentTracker and passes result back to the torrent client"""
    
    def __init__(self, receiver, address):
        asynchat.async_chat.__init__(self)
        self.receiver = receiver
        self.set_terminator(None)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer = ""
        self.set_terminator("\r\n\r\n")
        self.connect(address)
	
    def handle_connect(self):
        print "Sender connected"
	
    def collect_incoming_data(self, data):
        self.buffer = self.buffer + data
	
    def found_terminator(self):
        data = self.buffer
        self.buffer = ""
        print "==>(SentToClient) (%d) %s" % (self.id, repr(data))
        self.receiver.push(data + "\r\n\r\n")
	
    def handle_close(self):
        print "Sender closing ID: " + str(self.id)
        
        if len(self.buffer):
            self.found_terminator()
        
        self.receiver.close_when_done()
        self.close()



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
    #sudo python2.7 Proxy.py 192.121.86.40 81
    if len(sys.argv) < 3:
        print 'Usage: %s <tracker-ip> <tracker-port>' % sys.argv[0]
    else:
		ps = proxy_server(sys.argv[1], int(sys.argv[2]))
		asyncore.loop()
