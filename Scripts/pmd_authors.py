import os
import copy
import bz2
import networkx as nx
import pandas as pd

os.chdir('..')
os.chdir('pmd_baseline')
fileinfo=bz2.BZ2File('Net', 'r')
filtered_articles_net=nx.read_gpickle(fileinfo)
fileinfo=bz2.BZ2File('index', 'r')
unfiltered_articles=nx.read_gpickle(fileinfo)
fileinfo=bz2.BZ2File('Centrality', 'r')
centrality=nx.read_gpickle(fileinfo)
fileinfo.close()
#these created in pmd_network.py

def findAuthors(filtered_articles_net,unfiltered_articles):
    '''
    finds everything that was published in 2020 or 2021
    
    get authors from indexrecall
    tabulate

    construct new network with authors as nodes and common papers as edges
    intending to load into dash-cytoscape
    '''
    currentpapers=set()
    currentauthors=[]
    for node in filtered_articles_net:
        if unfiltered_articles[node]['date'][0] == '2020' or unfiltered_articles[node]['date'][0]=='2021':
            currentpapers.add(node)
    for paper in currentpapers:
        for authorTuple in unfiltered_articles[paper]['authors']:
            fullname=authorTuple[0]+', '+authorTuple[1]
            currentauthors.append(fullname)
    df=pd.DataFrame(currentauthors,columns=['Name'])
    df=df.groupby(['Name'])['Name'].count()
    df=df.to_dict()
    return [df]
def filter_low_centrality(centrality):
    centralitycopy=copy.deepcopy(centrality)
    for item in centralitycopy:
        if centrality[item]==0.0:
            centrality.pop(item)
# for item in centrality:
#     if centrality[item]>0.00001:
#         print (unfilteredarchives[item])
# I need to find how to sort the top 20 percent of these articles instead of just telling it
# a number for a significance threshold
    centralitydf=pd.DataFrame.from_dict(centrality,orient='index',columns=['Centrality'])
    centralitydf=centralitydf.sort_values(by=['Centrality'],axis=0,ascending=False)
#take size*whatever and select 0:that index position
    toptwenty=int(len(centrality)*0.2)+1
    twentypercent=centralitydf[:toptwenty]
    twenty_percent_authors=[]
    for index in twentypercent.index:
        twenty_percent_authors.append(unfiltered_articles[index]['authors'])
    topauthors=[]
    for authorset in twenty_percent_authors:
        for author in authorset:
             topauthors.append(author)
    return (centralitydf,topauthors)
if __name__=='__main__':
    # finds author with maximum occurences
    x=findAuthors(filtered_articles_net,unfiltered_articles)
    maxauth=max(x[0], key=lambda key:x[0][key])
    maxauth=maxauth.split(', ')
    for item in unfiltered_articles:
        for thing in unfiltered_articles[item]['authors']:
            if maxauth[0] in thing and maxauth[1] in thing:
                print(item,thing)
                

# ok, now i have a list of all authors, as well as authors from most central papers.
# how would i get from the most central papers to the current, significant ones?
# it's not possible to have recent(edge) papers be highly central. look for descendents?
# also look for author self citations, and recurrences of highly central authors in edge nodes
