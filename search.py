#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 13:28:25 2018

@author: nate
"""
#Nate Levy, Alan Sato
#search.py: inputs: a preprocessed set of query terms, (q_words), a reverse-index output file(ri)
#generates document and query vectors and returns urls sorted by cosine similarity 
#of their document vector to the query vector (descending)

import collections
import math
import numpy as np
import operator


def retrieve(q_words, ri):
    q_vec = []
    #harvest all docs that contain any q_words
    relevant_docs = []  
    for qw in q_words:
        if dict(ri.get(qw)) != None:    #avoid keyerrors at all cost
            for d in ri[qw]:
                if ri[qw] != 0.0 and d != '<df>' and d != '<total>':
                    relevant_docs.append(d)
    #remove duplicates       
    doclist = list(set(relevant_docs)) 
    
    #generate document vectors
    docveclist = []
    for rd in doclist:    
        vec = []
        for i in range(len(q_words)): #still no keyerrors here, thank you very much
            if ri.get(q_words[i]) == None:
                weight = 0.0
            elif ri[q_words[i]].get(rd) == None:
                weight = 0.0
            else:
                weight = ri[q_words[i]][rd]
            vec.append(weight) # sets the vector to the tf-idf weights as stored in the revese index
        docveclist.append(vec)
    
    #generate frequency info for later weighting
    freq_info = collections.Counter(q_words)
    max_freq = freq_info.most_common(1)[0][1] #make query vectors
    
    #do all that math from the powerpoint, trust us it's there
    for i in range(len(q_words)): 
        freq_wq = freq_info[q_words[i]]
        if ri.get(q_words[i]) != None:
            if ri[q_words[i]]['<df>'] <= 0.0:
                q_vec.append(0.0)
            else:
                q_vec.append((freq_wq / max_freq) * math.log10(ri['<total>']/ri[q_words[i]]['<df>'] ))
        else:
            q_vec.append(0.0)
        
    #compute cosine similarities
    cos_similarity = []
    for h in range(len(docveclist)):
        cos_similarity.append(cos_sim(q_vec, docveclist[h]))
     
    urllist = []
    #access the urls corresponding to the scanned documents
    for d in range(len(doclist)):
        urllist.append(ri['<urldict>'][doclist[d]])
    results_w_score = list(zip(urllist, cos_similarity))
    results_w_score.sort(key = operator.itemgetter(1), reverse = True)
    for r in range(len(results_w_score)):
         print('{0}'.format(results_w_score[r]))
 
def cos_sim(a,b):
    dp = np.dot(a,b)
    aM = np.linalg.norm(a)
    bM = np.linalg.norm(b)
    cs = dp/(aM*bM)
    #due to discrepancies in numpy's sigfigs for the relevant data, 
    #comparisons that should yield a cs of 1 yield 1.00000002.
    #since that as a value would ve visibly impossible, and since rounding of these "numpy.float64" objects wouldn;t
    #have that demoralizing in any other situation, this is how we're gonna feel ok about ourselves
    if cs > 1.0:   
        cs = 1.0
    return cs
