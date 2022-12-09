import os
import copy
import bz2
import networkx as nx
import pandas as pd
import seaborn as sns

os.chdir('..')
os.chdir('pmd_baseline\pmd_filtered')
fileinfo=bz2.BZ2File('Net', 'r')
filtered_articles_net=nx.read_gpickle(fileinfo)
fileinfo=bz2.BZ2File('articles', 'r')
unfiltered_articles=nx.read_gpickle(fileinfo)
fileinfo=bz2.BZ2File('Centrality', 'r')
centrality=nx.read_gpickle(fileinfo)
fileinfo.close()
#these created in pmd_network.py

def find_recent_authors(filtered_articles_net,unfiltered_articles):
    '''
    finds everything that was published in 2020 or 2021
    
    get authors from indexrecall
    tabulate
    
    !!!the list this produces does not take centrality values into account!!!
    '''
    currentpapers=set()
    currentauthors={}
    for node in filtered_articles_net:
        if unfiltered_articles[node]['date'][0] == '2020' or unfiltered_articles[node]['date'][0]=='2021':
            currentpapers.add(node)
    for paper in currentpapers:
        for authorTuple in unfiltered_articles[paper]['authors']:
            fullname=str(authorTuple[0]+', '+authorTuple[1])
            if not fullname in currentauthors and len(authorTuple[2])>0:
                currentauthors[fullname]=authorTuple[2][0]
            else:
                continue
    df=pd.DataFrame.from_dict(currentauthors, orient='index', columns=['institution'])
    df=df.groupby(['institution'])['institution'].count().reset_index(name='count')
    df=df.sort_values(by=['count'],axis=0,ascending=False)
    return df
def find_central_authors(centrality,unfiltered_articles):
    '''
    find all authors in central papers and tabulate their institutions
    
    !!!this does not take recency into account!!!
    
    '''
    
    centralitydf=pd.DataFrame.from_dict(centrality,orient='index',columns=['centrality'])
    centralitydf=centralitydf.sort_values(by=['centrality'],axis=0,ascending=False)
    authors_by_paper=[]
    for index in centralitydf.index:
        authors_by_paper.append(unfiltered_articles[index]['authors'])
    authors=[]
    for authorset in authors_by_paper:
        for author in authorset:
            authors.append(author)   
    institutions=[]
    for author in authors:
        if author[2]:
            institutions.append(author[2][0])
    df2=pd.DataFrame(institutions,columns=['institution'])
    df2=df2.groupby(['institution'])['institution'].count().reset_index(name='count')
    df2=df2.sort_values(by=['count'],axis=0,ascending=False)
    return df2
if __name__=='__main__':
    # finds author with maximum occurences
    x=find_recent_authors(filtered_articles_net,unfiltered_articles)
    y=find_central_authors(centrality,unfiltered_articles)
    df3=x.merge(y,how='inner',on='institution')
    df3=df3.sort_values(by=['count_x', 'count_y'],axis=0, ascending=False)
    df3=df3.rename(columns={'count_x':'recency', 'count_y':'centrality'})
    #sns.scatterplot(data=df3,x='recency',y='centrality')
    os.chdir('..')
    df3.to_csv(os.getcwd()+'\\institutions')
    
# ok, now i have a list of all authors, as well as authors from most central papers.
# how would i get from the most central papers to the current, significant ones?
# it's not possible to have recent(edge) papers be highly central. look for descendents?
# also look for author self citations, and recurrences of highly central authors in edge nodes
