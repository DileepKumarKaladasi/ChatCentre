from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import math


#load model
#idata = pd.read_csv('qna_v1.csv')
#model  = SentenceTransformer("SentenceTranformerBert")
# see the details of model with print 
#model = SentenceTransformer("SentenceTranformerMPNET")
#prompt = "State Distribution not present"
#


def predictions(idata,model,prompt):
    data1 = idata.copy()
    data2 = idata.copy()
    data2['Answers']=data2['Issues']

    data = pd.concat([data1,data2])
    data = data.reset_index().drop(columns='index')
    sentences_list = data['Answers'].to_list()
    #taking embedding of list
    embeddings =  model.encode(sentences_list)
    prompt_embedding = model.encode(prompt)
    
    
    def cosineValue(v1,v2):
        "compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)"
        sumxx, sumxy, sumyy = 0, 0, 0
        for i in range(len(v1)):
            x = v1[i]; y = v2[i]
            sumxx += x*x
            sumyy += y*y
            sumxy += x*y
        return sumxy/math.sqrt(sumxx*sumyy)
    
    sim_lst = []
    for i in range(len(embeddings)):
        sim_lst.append(cosineValue(prompt_embedding,embeddings[i]))
    indices = sorted(range(len(sim_lst)), key=lambda i: sim_lst[i], reverse=True)[:3]
    
    iss_lst=[]
    mdl_lst = []
    cos_lst = []
    sys_lst = []
    for i in indices:
        iss_lst.append(data['Issues'][i])
        mdl_lst.append(data['ModelType'][i])
        cos_lst.append(sim_lst[i])
        sys_lst.append(data['System'][i])
        
    return sys_lst,mdl_lst,iss_lst,cos_lst
    
#sys_lst,mdl_lst,iss_lst,cos_lst = predictions(idata,model,prompt)
