__author__ = 'Samuel'
import WebDB, Index
class controller:
    def __init__(self):
        self.database = WebDB.WebDB("./Data/cache.db")
        self.index = Index.Index()
        print("Welcome to Sam's search engine version 2. Please wait while we populate the index")
        self.index.populate()
        print("index populated")
        self.is_nnn_query = True
        self.is_nnn_index = True
        self.k = 10
    def userInit(self):
        index_type = input("would you like nnn or ltc Indexing? ").lower()
        query_type = input("would you like nnn or ltc queries? ").lower()
        if index_type == "ltc":
            #self.is_nnn_query = True
            self.is_nnn_index = False
        if query_type == "ltc":
            self.is_nnn_query = False
        if self.is_nnn_index:
            self.index._addWeights_nnn()
        else:
            self.index._addWeights_ltc()
        print("weighting complete")

    def search(self):
        query = input("enter your search phrase: ")
        temp = {}
        if self.is_nnn_query:
            temp = self.index.nnn_query(query) #query dic
        else:
            temp = self.index.ltc_query(query)
        results = self.index.process_query(temp)
        out = []
        for i in range(self.k):
            out.append(results[i])
        return out
    def print_by_urlID(self,list_url_id):
        print(list_url_id)
        for i in list_url_id:
            print("weight:"+str(i[1]))
            holder = self.database.lookupCachedURL_byID(i[0])
            for j in holder:
                print(j)
            #print("\n")
def main():
    a = controller()
    a.userInit()
    while(True):
        temp = a.search()
        a.print_by_urlID(temp)
main()