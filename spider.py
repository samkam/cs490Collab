__author__ = 'Samuel'
import google
import urllib.request
import urllib.error
import WebDB
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from nltk import stem
import re
import os
import WebDB
import shutil
import time
import sys
import threading
verbosity = 0
Cache_folders = ["item","raw","header","clean"]
item_files = ["book","movie", "music"]
class Spider:
    def __init__(self, filelocation="./Data" ):
        #set up file directory system
        DBname = filelocation+"/cache.db"
        #TODO make it so that folders are created without being read-only
        if not os.path.exists(filelocation):
            os.mkdir(filelocation)
            for folder in Cache_folders:
                temp = filelocation+"/"+folder
                os.mkdir(temp)

            DB = open(DBname,'w')
            DB.close()
            for i in item_files:
                print(i)
                shutil.copyfile("./itemBank/"+i+".txt",filelocation+"/item")


        self.folder = filelocation
        self.database = WebDB.WebDB(DBname)
        #need to bring in items.txt to this
        #need to insert items into database
        self.contentType = ""
        self.title = ""
        self.url = ""
        self.url_id = 1 # might not be necessary
        self.item_id =1
        self.url_to_item_id = 1
        self.itemName = ""#eg, "beatles"
        self.itemType = ""#eg, "music"

        self.header = ""
        self.rawHTML = ""
        self.tokens = []

    def URLs_from_query(self, query, n):
        query = '"'+query+'"'+" "+self.itemType
        results_iterator = google.search(query, stop = n)
        URLs = []
        for i in results_iterator:
            URLs.append(i)
        return URLs


    def remove_duplicates(self,str_list):
        out = []
        for token in str_list:
            if token not in out:
                out.append(token)
        return out
    #retrieves webpage as string
    def URL_to_rawHTML(self, urlStr):
            urllib.request.HTTPCookieProcessor(cookiejar=google.cookie_jar)
            httpRes = urllib.request.urlopen(urlStr)
            rawHTML = httpRes.read()


            return rawHTML

    def fetch(self,URL):
        #time.sleep(10)
        #print("in fetch")
        Req = urllib.request.Request(URL)
        Req.add_header('User-Agent', 'Opera/9.80 (Windows NT 6.1; WOW64; U; de) Presto/2.10.289 Version/12.01')
        Req.add_header('Accept-Language', 'de-DE,de;q=0.9,en;q=0.8')
        Req.add_header('Accept', 'text/html, application/xml;q=0.9, application/xhtml+xml, image/png, image/webp, image/jpeg, image/gif, image/x-xbitmap, */*;q=0.1')

        urllib.request.HTTPCookieProcessor(cookiejar=google.cookie_jar)
        try:
            httpRes = urllib.request.urlopen(Req)
        except urllib.error.HTTPError:
            print("http error: skipping entry")
            return
        temp_header = str(httpRes.info())
        #print(temp_header)

        #get content-type from header
        temp_list = temp_header.split("\n")
        for item in temp_list:
            if "Content-Type" in item:
                #print("content-type found")
                start= item.find(":")+1
                end = item.find(";")
                #get substring
                self.contentType = item[start:end].strip()
                #print(self.contentType)
                break
        self.header = temp_header
        self.url = URL
        self.rawHTML= httpRes.read()#.encode(sys.stdout.encoding, errors='replace')
        temp = self.parser(self.rawHTML)
        temp = self.lower(temp)
        temp = self.stem(temp)
        #temp = self.remove_duplicates(temp)
        self.tokens = temp
        #TODO: add header info to forge browser identity
    def cache_results(self):
        '''
        writes all stored information in spider class to appropiate text files.
        also creates database entries. purges data members when finished.
        :return:
        '''
        self.url_id = self.database.insertCachedURL(self.url,self.contentType,self.title)
        self.url_to_item_id= self.database.insertURLToItem(self.url_id,self.item_id)

        filename = formatID(self.url_id, 5)+".txt"

        with open(self.folder+"/raw/"+filename,'w',encoding='utf-8')as f:
            try:
                temp_soup= BeautifulSoup(self.rawHTML)
                erte = temp_soup.decode()
                f.write(erte)
            except Exception:
                print("failed to write rawHTML file")
                f.write("NOTOKENS")
        with open(self.folder+"/header/"+filename,'w')as f:
            f.write(self.header)
        with open(self.folder+"/clean/"+filename,'w')as f:
            for i in self.tokens:
                try:
                    f.write(i+'\n')
                except UnicodeEncodeError:
                    pass
        self.url = ""
        self.contentType = ""
        self.title = ""
        self.rawHTML = ""
        self.header = ""
        self.tokens = []

    def parser(self, rawHTML):
        soup = BeautifulSoup(rawHTML)
        try:
            self.title = soup.title.string
        except AttributeError:
            self.title = "no title"
        #removes all script tags from soup
        for i in soup.find_all("script"):
            i.clear()
        for i in soup.find_all("style"):
            i.clear()
        content = soup.get_text().strip('\n ')

        #use regular expressions to process content
        raw_tokens = re.split('\W+', content)
        #self.tokens = raw_tokens
        return raw_tokens
    # lower- converts all tokens to lowercase, removes empty strings and duplicates
    def lower(self,tokens):
        out = []
        for i in range(len(tokens)):
            if tokens[i] == '':
                pass
            else:
                out.append(tokens[i].lower())
        self.tokens = out
        #out = self.remove_duplicates(out)
        #self.numTokensUniqueNoCase = len(out)
        return out
    # stem- applies porter stemmer algorithm to list, and filters out duplicate terms
    def stem(self,tokens):
        pStem = stem.PorterStemmer()
        temp = []
        for token in tokens:
            temp.append(pStem.stem(token))
        #out = self.remove_duplicates(temp)
        #self.numTokensStemmed = len(out)
        return temp
    # getTerms- returns a sorted list of unique tokens found in input list
    # (to be fully implemented)
    def getTerms(self, tokens):
        out = tokens.sort()
        return out

    def toString(self):
        print("title: "+self.title)
        print("number of tokens: {0}".format(self.numTokensRaw))
        print("number of terms: {0}".format(self.numTokensUnique))
        print("number of terms after lowercase: {0}".format(self.numTokensUniqueNoCase))
        print("number of terms after porter stemmer: {0}".format(self.numTokensStemmed))
    def driver(self):
        dirr = self.folder+"/item/"
        for i in item_files:
            self.itemType = i
            with open(dirr+i+".txt") as f:
                for item in f:
                    print(item)
                    time.sleep(5)
                    self.itemName = item
                    self.item_id = self.database.insertItem(self.itemName,self.itemType)
                    URLS = self.URLs_from_query(item, 10)
                    for url in URLS:
                        if self.database.lookupCachedURL_byURL(url):
                            print(url+" has already been cahced")
                            continue
                        try:
                            self.fetch(url)
                            self.cache_results()
                            print(url + "successfully added")
                        except Exception:
                            pass


def formatID(id,decimals):
    out = str(id)
    if len(out) < decimals:
        numZeroes = decimals - len(out)
        out = ("0"*numZeroes) + out
    return out
def driver():
    items = []
    with open("./Data/item/movie.txt") as f:
        for line in f:
            items.append(line)
    itsybitsy = Spider()

    queries = itsybitsy.URLs_from_query(items[0], 10)

#    URL = input("enter URL")
#    rawHTML = spider.URL_to_rawHTML(URL)
#    tokens =spider.parser(rawHTML)#"http://www.cnn.com/2015/01/31/us/texas-chris-kyle-day/index.html")
#    print(tokens)
#    downcase_tokens = spider.lower(tokens)
#    stemmed_tokens = spider.stem(downcase_tokens)
#    spider.toString()
def main():
    itsybitsy = Spider()
    itsybitsy.driver()
main()
