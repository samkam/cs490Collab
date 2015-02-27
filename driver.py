#Interface for boolean search engine
import Index
import WebDB
import sys
from nltk import stem
class UserInterface:

    def __init__(self):
        self.database = WebDB.WebDB("./Data/cache.db")
        self.index = Index.Index()
        print("Welcome to Sam's search engine. Please wait while we populate the index")
        self.index.populate()
        print("index populated")
        #while True:
        #    self.print_menu()
        #    self.select_option()
    def print_menu(self):
        print('''Welcome to the search engine!
        1) single search
        2) and search
        3) or search
        4) near terms search
        5) phrasal query
        ''')
    def select_option(self):

        selection = 0
        while(selection <1 or selection >5):
            print("to quit, enter 'QUIT'")
            a = input("enter menu option number (1-5): ")
            if a == "QUIT":
                sys.exit(0)
            try:
                selection = int(a)
            except ValueError:
                pass #user attempted to use invalid input
        try:
            if selection ==1:
                self.single_search()
            elif selection ==2:
                self.and_search()
            elif selection ==3:
                self.or_search()
            elif selection ==4:
                self.near_search()
            elif selection ==5:
                self.phrasal_search()
            '''
            option = {1:self.single_search(), 2: self.and_search(), 3: self.or_search(),
                  4: self.near_search(), 5:self.phrasal_search()}
            option[selection]
            return
            '''
        except UnicodeEncodeError:#Exception:
            print("you might have typed something wrong")

    def print_by_urlID(self,list_url_id):
        print(list_url_id)
        for i in list_url_id:
            holder = self.database.lookupCachedURL_byID(i)
            for j in holder:
                print(j)
    def single_search(self):
        print("--Single search--")
        query = input("input single term to search:")
        Doc_ids = self.index.singleQuery(query)
        print(str(len(Doc_ids))+"results")
        #self.print_by_urlID(Doc_ids)
    def and_search(self):
        print("--AND search--")
        query1 = input("input first term to search:")
        query2 = input("input second term to search:")
        Doc_ids = self.index.andQuery(query1,query2)
        print(str(len(Doc_ids))+"results")
        #self.print_by_urlID(Doc_ids)
    def or_search(self):
        print("--OR search--")
        query1 = input("input first term to search:")
        query2 = input("input second term to search:")
        Doc_ids = self.index.orQuery(query1,query2)
        print(str(len(Doc_ids))+"results")
        #self.print_by_urlID(Doc_ids)
    def near_search(self):
        print("--NEAR search--")
        query1 = input("input first term to search:")
        query2 = input("input second term to search:")
        distance = int(input("input max distance between terms:"))
        Doc_ids = self.index.nearQuery(query1,query2,distance)
        print(str(len(Doc_ids))+"results")
        #self.print_by_urlID(Doc_ids)
    def phrasal_search(self):
        print("--phrasal search--")
        query = input("input phrase").split()
        if len(query) <2:
            print("invalid input")
            return
        Doc_ids = self.index.phrasalQuery(query[0],query[1])
        print(str(len(Doc_ids))+"results")
        #self.print_by_urlID(Doc_ids)
def main():
    a = UserInterface()
    while True:
        a.print_menu()
        a.select_option()

'''
    print("in main")
    a = Index.Index()
    print("index instantiated")
    a.populate()
    print("done populating")
    query = "Dickens"
    query2 = "Charles"
    #stemmer= stem.PorterStemmer()
    #stemmed_query = stemmer.stem(query)
    q_single = a.singleQuery(query)
    q_and = a.andQuery(query, query2)
    q_or = a.orQuery("electric","guitar")
    q_near = a.nearQuery("beatles","album",15)
    q_phrasal= a.phrasalQuery("john","lennon")
    a.print_by_urlID(q_and)
'''
main()

