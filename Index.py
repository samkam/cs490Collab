import pickle
import collections
import WebDB
from nltk import stem
import os
import pickle
import math
import random
import re
class Index:
    def __init__(self, dbfile ="Data/cache.db" ):
        print("initializing index")
        self.database = WebDB.WebDB(dbfile)
        self.index = dict()
        self.total_count = 0 #number of documents we have
        self.nnn_indexing = True
    def filename2ID(filename):
        temp = filename.rstrip(".txt")
        return int(temp)
    def populate(self):
        list1 = os.walk("Data/clean")
        #os walk is a generator, and returns a tuple. Weird shit
        list2 = []
        for i in list1:
            list2 = i[2]
        self.total_count = len(list2)
        if os.path.exists("data/index.p"):
            print("Index pickle file found")
            self.index = pickle.load(open("data/index.p", "rb"))

        else:
            print("making pickle")

            for DocID, filename in enumerate(list2):
                #this is running under the assumption  that walk itemizes files in ascii order
                with open("./Data/clean/"+filename, 'r') as f:
                    #print("size of f.readlines: {}".format(len(f.readlines())))
                    for position, token in enumerate(f.readlines()):
                        stripped_token = token.rstrip("\n")
                        self._addToken(stripped_token,DocID+1,position)
            print("population complete")
            pickle.dump(self.index, open("data/index.p", "wb"))
    def nnn_query(self, query_string):
        terms = []
        for term in query_string.split():
            terms.append(self._stem_query(term))
        query_dic = dict()
        for term in terms:
            if term not in query_dic:
                query_dic[term] = 1
            else:
                query_dic[term] += 1
        return query_dic
    def ltc_query(self, query_string):
        terms = []
        for term in query_string.split():
            terms.append(self._stem_query(term))
        query_dic = dict()
        for term in terms:
            if term not in query_dic:
                query_dic[term] = 1
            else:
                query_dic[term] += 1

        for key in query_dic.keys():
            term_freq = 1+ math.log10(query_dic[key])
            try:
                #print("len(self.index[term].keys())")
                #print(len(self.index[term].keys()))
                #print("self.total_count")
                #print(self.total_count)
                inverse_document_freq = math.log10(self.total_count/(len(self.index[term].keys())))
                query_dic[key] = term_freq * inverse_document_freq
            except KeyError:
                query_dic[key] = 0.0

        return query_dic
    def process_query(self, query_dic):
        scores = dict()
        for term in query_dic.keys():
            for DocID in self.index[term].keys():
                #multiply weights of each term in query by document weight to find cosine distance
                if DocID not in scores:
                    scores[DocID] = 0.00001*random.random()
                scores[DocID] +=query_dic[term] *self.index[term][DocID][0]
        s = collections.OrderedDict(sorted(scores.items(), key=lambda t: t[1],reverse=True))
        #iter_dic = s.iterkeys()
        #for i in range(max(len(s),num_results)
        #count = num_results
        out = []
        for key in s.keys():
            out.append((key, s[key]))
        return out



    def _stem_query(self, word):
        word = word.lower()
        word = re.sub('\W+','', word)
        s = stem.PorterStemmer()
        return s.stem(word)
    def _addToken(self, token, DocID, token_position):
        #print("token {0}, DocID {1}, token_position {2}".format(token, DocID,token_position))
        if token not in self.index:
            self.index[token] = dict() #empty dictionary
            #print("novel token added")
        if DocID not in self.index[token]:
            self.index[token][DocID] = [0.0]# 0th position will contain weight for dodcuments
            #print("novel docId added to ")
        self.index[token][DocID].append(token_position)
    def _addWeights_nnn(self):
        print("adding nnn weighting to Index")
        for term in self.index.keys():
            for docID in self.index[term].keys():
                self.index[term][docID][0]= len(self.index[term][docID]) -1
    def _addWeights_ltc(self):
        '''
        adds weight calculated by (ltc) idf and tf values for each key in the sub dictionary
        :return:
        '''
        print("adding ltc weighting to Index")
        N = self.total_count #number of all documents
        docLengths = dict()
        for term in self.index.keys():
            inverse_document_freq = math.log10(N/(len(self.index[term].keys())))
            for docID in self.index[term].keys():
                term_freq = 1+ math.log10(len(self.index[term][docID]) -1)
                if docID not in docLengths:
                    docLengths[docID] = 0.0
                weight =  term_freq * inverse_document_freq
                self.index[term][docID][0]= weight
                docLengths[docID] = docLengths[docID]+ weight*weight #why do we do this :(((((

        #go through loop again and normalize all weights by document length
        for term in self.index.keys():
            for docID in self.index[term].keys():
                self.index[term][docID][0] = self.index[term][docID][0]/math.sqrt(docLengths[docID])
    def print_by_urlID(self,list_url_id):
        print(list_url_id)
        for i in list_url_id:
            holder = self.database.lookupCachedURL_byID(i)
            for j in holder:
                print(j)
            #print("\n")
    def singleQuery(self,term):
        #if term not in self.index:
        #   return []
        #stemmed_term = stem.PorterStemmer.stem(term)
        stemmed_word = self._stem_query(term)
        print("stemmed word is "+stemmed_word)
        out_list = list(self.index[stemmed_word].keys())
        return out_list
    def andQuery(self, term1, term2):
        list1 = self.singleQuery(term1)
        list2 = self.singleQuery(term2)
        out = []
        for item in list1:
            if item in list2:
                out.append(item)
        return out
    def orQuery(self, term1, term2):
        list1 = self.singleQuery(term1)
        list2 = self.singleQuery(term2)
        for item in list1:
            if item not in list2:
                list2.append(item)
        return list2
    def nearQuery(self, term1, term2, maxDistance, isOrdered=False):
        term1 =self._stem_query(term1)
        term2 =self._stem_query(term2)
        list_of_keys = self.andQuery(term1, term2) #gets list of DocIDs in common to both terms
        dic1 = self.index[term1]
        dic2 =self.index[term2]
        out = []
        if len(list_of_keys)<1:
            return []
        for DocId in list_of_keys:
            should_break = False
            for position1 in dic1[DocId]:
                if should_break:
                    break
                for position2 in dic2[DocId]:
                    #is ordered should only be set to true if performing a phrasal query
                    #set to automatically skip any conditions where the terms are out of order
                    if isOrdered and (position1 >position2):
                        continue
                    if abs(position1-position2) <= maxDistance:
                        should_break = True
                        out.append(DocId)
                        break
        return out
    def phrasalQuery(self,term1, term2):
        return self.nearQuery(term1, term2, 1, isOrdered=True)






