'''
    Takes the filtered articles generated by pmd_filter and creates a directed 
    graph out of them.
'''
import os
import pickle
import bz2
import copy
import networkx as nx

all_articles={}
os.chdir('..')
os.chdir('pmd_baseline\pmd_filtered')
for file in os.scandir():
    pubmedentries=bz2.BZ2File(file, 'r')
    index=pickle.load(pubmedentries)
    for article in index:
        node_name=article['PMID']
        all_articles[node_name]=article
#   loading in the selected articles and decompressing
#   Creating keys for each pmid - use to construct graph

Net=nx.DiGraph()
for key in all_articles:
    Net.add_node(key)
for key in all_articles:
    article=all_articles[key]
    for citation in article['citations']:
        if str(citation) in all_articles.keys() and str(citation)!=article['PMID']:
            #this had been also returning the article itself, for some reason. never investigated why
            Net.add_edge(key,citation)
    #generating graph...

def filter_singletons(graph):
    """
    

    Parameters
    ----------
    graph : the graph of all entries by their PMIDs. removes all singleton nodes
            from the network

    Returns
    -------
    y : how many nodes have >0 connections
    n : how many single (disconnected) nodes there are

    """
    
    y=0
    n=0
    testnet=copy.deepcopy(graph)
    testnet=nx.Graph(testnet)
    for each_node in testnet:
        current_neighbors=Net.neighbors(each_node)
        all_neighbors=[]
        for neighbr in current_neighbors:
            all_neighbors.append(neighbr)
        if all_neighbors:
            y+=1
        if not all_neighbors:
            n+=1
            graph.remove_node(each_node)
    print('In a network:',y)
    print('Singleton:',n)
    return (y,n)
    
# getting somewhere!
#i think, dont bother trying to visualize with python standalone. use networkx for
# its graph objects and support and then export the result to cytoscape for vis...

#nothing much left to do now but load up everything...
# for final filter, try looking at neighbors of neighbors,...& etc to root out small
#disconnected networks. then, assess nodes by accessibility metrics. also research
#centrality measurements
firstfilter=filter_singletons(graph=Net)
# longest=[{'0'}]
total_subgraphs=0
for item in nx.connected_components(nx.Graph(Net)):
    total_subgraphs+=1
    # for subgraph in longest:
    #     if len(item)>len(subgraph):
    #         longest.append(item)
    #         longest.remove(longest[0])
    if len(item)<10 and len(item)>0:
    #     # for node in item:
    #     #     print(all_articles[node])
    #     # prompt=input('Reject network? [y/n]')
    #     # if prompt == 'y':
        for node in item:
            edge_removal=[]
            for neighbor in Net.neighbors(node):
                edge_removal.append(neighbor)
            for edge in edge_removal:
                Net.remove_edge(node,edge)
            try:
                Net.remove_node(node)
            except:
                continue
        else:
            continue
        #removing small subgraphs. thresholds here can be adjusted.
postfilter_subgraphs=0
postfilter_nodes=0
for item in nx.connected_components(nx.Graph(Net)):
    postfilter_subgraphs+=1
    postfilter_nodes+=len(item)
    print(item)
print ('Number of subgraphs passing filter:',postfilter_subgraphs,'/',total_subgraphs)
print('Nodes represented:',postfilter_nodes,'/',firstfilter[0], '('+str(round(postfilter_nodes/firstfilter[0],3)*100)+'%)')
# as it turns out (from actually reading the documentation) you can just use max(nx.connected_components)
#to find the largest subgraph. since i've already written it this way and I also included
#the filter of everything else i'm leaving it as is
def make_subgraphs(Net):
    for item in nx.connected_components(nx.Graph(Net)):
        subg=nx.subgraph(Net,item)
        yield subg
max_graph=len(max(nx.connected_components(Net.to_undirected())))
for item in make_subgraphs(Net):
    if len(item)==max_graph:
          Net=item
#Net is now equal to the single largest graph, which hopefully represents the vast 
#   majority of nodes
#nx.draw_networkx(Net)
# ^this is useless, creates a hairball

#so, this can let me sort for the largest subgraphs - or rather, review and filter out
# small irrelevant ones. problem may arise if there are multiple large(>a few thousand)
#graphs that are relevant. or, how would you determine + discriminate their relevance?
# ...looks like it is finding all subgraphs fine, it just wont graph anything smaller than 
#like, 10 nodes or something like that

#ok now to assess importantness of each node within the graph.
#there are many ways to do this and they are all computationally expensive
#x=nx.betweenness_centrality(Net)
    #do not do this^
#i'm thinking; we can get some measure of network centrality by looking only
#at shortest paths from source (indegree=0) to destination (outdegree=0) nodes,
#which is a lot less intensive than calculating betweenness for every single pair...
s=set()
t=set()
lengths=[]
for node in Net:
    try:
        if Net.in_degree(node)==0 and int(all_articles[node]['date'][0])<2000:
            s.add(node)
        elif Net.out_degree(node)==0 and int(all_articles[node]['date'][0])>2000:
            t.add(node)
    except ValueError:
        continue
#more pairs are better but I can't afford to have this thing run for more than like 12 hours
visited={}
uniNet=Net.to_undirected()
def find_paths(uniNet,s,t,visited):
    i=0
    for source in s:
        i+=1
        print(i)
        for target in t:
             l,path=nx.bidirectional_dijkstra(uniNet, source, target)
             path.pop(l)
             path.pop(0)
             yield path
for path in find_paths(uniNet,s,t,visited):
    for node in path:
        if not node in visited:
            visited[node]=1
        else:
            visited[node]+=1

central=max(visited, key=lambda key:visited[key])
    #this returns the key of the highest centrality valued node
i=Net.in_degree(central)
print('the most central node is',central+ ', which is cited',i,'times')

download_graph=bz2.BZ2File('Net','w')
pickle.dump(uniNet,download_graph)
#cant pickle digraphs????
download_graph.close()
download_all_articles=bz2.BZ2File('articles','w')
pickle.dump(all_articles, download_all_articles)
download_all_articles.close()
download_centrality=bz2.BZ2File('Centrality','w')
pickle.dump(visited, download_centrality)
download_centrality.close()
pubmedentries.close()
