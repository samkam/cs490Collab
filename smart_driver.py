__author__ = 'Samuel'
import WebDB, Index, collections,sys
class controller:
    def __init__(self):
        self.database = WebDB.WebDB("./Data/cache.db")
        self.index = Index.Index()
        print("Welcome to Sam and Grayson's search engine version 2. Please wait while we populate the index")
        self.index.populate()
        print("index populated")
        self.is_nnn_query = True
        self.is_nnn_index = True
        self.k = 10
        self.top_items = {}

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
        self.print_top_items(results)
        out = []
        for i in range(self.k):
            out.append(results[i])
        return out

    def print_top_items(self,all_results):
        item_dict = dict()
        for i in all_results:
            item_name = self.database.ItemIDfromUrlID(i[0])
            #print(item_name)
            #print(i)
            #print(i[1])
            if item_name not in item_dict:
                item_dict[item_name] = 0.0
            item_dict[item_name] += i[1]
        s = collections.OrderedDict(sorted(item_dict.items(), key=lambda t: t[1],reverse=True))
        for i in range(self.k):
            print(s.popitem(last=False))

    def print_by_urlID(self,list_url_id):
        #print(list_url_id)
        print("\n")
        count = 1
        for i in list_url_id:
            holder = self.database.lookupCachedURL_byID(i[0])
            place = 1
            for j in reversed(holder):
                if place == 1:
                    print(str(count) + ") " + str(j))
                    place = 2
                elif place == 2:
                    place = 3
                    continue
                elif place == 3:
                    place = 1
                    print(j)
            print("weight: "+str(round(i[1], 4)))
            print("from: "+str(self.database.ItemIDfromUrlID(i[0])))
            print("\n")
            count += 1

def evaluation():
    isIndexNNN = [True, False]
    isQueryNNN = [True, False]
    for IndexType in isIndexNNN:
        current_index = Index.Index()
        current_index.populate()
        if IndexType:
            current_index._addWeights_nnn()
        else:
            current_index._addWeights_ltc()
        for queryType in isQueryNNN:
            items = []
            average_results = [0,0,0,0]
            # items =current_index.database.Get_All_ITEmS
            items = current_index.database.getItems() #list of tuple of id, name, type
            #print(items)
            #sys.exit(0)
            for item in items:
                query_results = []
                #print(item[2])
                if queryType:
                    query_dic = current_index.nnn_query(item[1]+" "+item[2])
                else:
                    query_dic = current_index.ltc_query(item[1]+" "+item[2])

                results = current_index.process_query(query_dic)
                #print(results)
                for result in results:
                    query_results.append(result[0])
                print("item[0] is "+str(item[0]))
                results = current_index.database.lookupURLs_byItemID(item[0]) # list of tuples of url and id number
                expected_results = []
                for result in results:
                    expected_results.append(result[1])

                print(query_results)
                print(expected_results)
                binary_list = []
                for i in query_results:
                    if i in expected_results:
                        binary_list.append(1)
                    else:
                        binary_list.append(0)
                print(binary_list)
                sys.exit(0)
                #get results of item name inputted as search query
                #compare to list of URLids associated with that item in the database
                #do all of the calculations (ap, r, k, AUC)
                #add to average results
            print(average_results)
#utility functions
def tabbed_print(list):
    temp = ""
    for item in list:
        temp+= str(item)+"\t"
    print(temp)

def main():
    evaluation()
    '''
    a = controller()
    a.userInit()
    while(True):
        temp = a.search()
        a.print_by_urlID(temp)
    '''
main()