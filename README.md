<h1>Introduction</h1>
I initially wrote this as a way to map synbio research. I'm not enthralled with searches that present results in a list, because although this is necessary to present things neatly, it doesn't actually reflect the way that the information in scientific research is structured. It seems easier to me to jump into a new subfield by getting a bird's-eye view of the particular citation clusters, and then prioritizing readings based on network analysis, rather than by however the ranking algorithm decides to present search results to you, which seems prone to bias. <sup>[Beel & Gipp](doi.org/10.1109/RCIS.2009.5089308)</sup>  

I run everything out of terminal, cd into 'Scripts', although Spyder works well too.

######**Obtaining data**
The dataset this project analyzes is [PubMed's annual baseline citation index.](https://www.nlm.nih.gov/databases/download/pubmed_medline.html), using 'pmd_webscraper'. I adapted some webscraper code from [this](https://towardsdatascience.com/how-to-web-scrape-with-python-in-4-minutes-bc49186a8460) post to download all 1000+ .xml files to new directory ('pmd_baseline') inside this cloned repo. Unfortunately, this whole process needs to be a bit slow, otherwise NIH will block your IP if you make too many requests per second - it takes a few hours to get everything in.

######**Broad filtering**
'pmd_filter' is the first stab at filtering down to only the set of articles you're interested in, based on multiple keyword search on the article title and/or abstract. It accepts a .txt file input with two lines, like so:

>metaboli,edit,synthetic,system,engineer,gene regulat

>patient,cancer,Cancer,tumor,clinic,speech,spine,bovine,mouse,osteo,syndrome

~~Case sensitive and no substring matching, sorry.~~ It generates objects for all of them, then filters. The first line catches everything you want, and the second filters out from that set things you don't.  Notice that I'm interested in metabolism and metabolites, but not 'metabolic syndrome'. These particular keywords yield about 130,000 articles, and download only the filtered set.

######**Generating networks**
'pmd_network' then goes to each filtered file, looks at all articles, their PMIDs and IDs of their citations, and builds directed graphs out of them. If you're lucky, the network size distribution obeys some rough power law and you can pretty comfortably filter out everything except the largest subgraph. 

From this chosen network, it then attempts to calculate a simplified version of betweenness centrality. I took ~200 of the oldest papers in my network with indegree==0 (have not cited by anything in network) and ~200 of the youngest papers with outdegree==0 (have not been cited by anything in network), and used a bidirectional dijkstra to calculate shortest paths between all pairs in these two sets. The network object, set of relevant articles, and centrality measurements are all then saved.

######**Analysis**
'pmd_authors' then does two things:
1. Analyzes the set of **all** relevant papers for those that are most recent (since 2020), and finds their authors and institutional affiliations
2. Analyzes the papers with high betweenness centrality to find their authors and institutional affiliations. 
It then tabulates institutions in these two sets into a csv, and downloads 'institutions' to the pmd_baseline directory.


######**In progress**  
1. Exploring clustering algorithms to reveal network substructures
2. Topic modeling with Latent Dirichlet Allocation to characterize the corpora of those clusters
3. 'pmd_dash' - Working on visualizing these networks with [Plotly Dash](https://plotly.com/dash/)
4. Continuing to clean this whole thing up!

