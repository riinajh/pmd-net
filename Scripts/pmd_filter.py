'''
    Takes the raw xml.gz files downloaded from baseline by the webscraper and
    filters them based on keyword search, then dumps new compressed data into 'index' files
    Also accepts a text file with two lines: first, keywords to search, and second, keywords
    to filter against
'''
import glob, os
import sys
import copy
import csv
import xml.etree.ElementTree as ET
import pickle
import bz2
import gzip

os.chdir('..')
os.chdir('pmd_baseline')
if not os.path.isdir('pmd_filtered'):
    os.mkdir('pmd_filtered')
def YieldEntries(root, dicttemplate):
    for article in root.iter('PubmedArticle'):
        entry=copy.deepcopy(dicttemplate)
        for title in article.iter('ArticleTitle'):
            name=title.text
            #print(name)
            entry['title']=name
        #Can find an instance of something. looking for one thing though, don't think
        #it can find multiples. also have to double check that its searching only one article
        for author in article.iter('Author'):
            affiliations=[]
            for ln in author.iter('LastName'):
                lastname=ln.text
            try:
                testln=(lastname)
            except UnboundLocalError:
                lastname='n/a'    
            for fn in author.iter('ForeName'):
                forename=fn.text
            try:
                testfn=(forename)
            except UnboundLocalError:
                forename='n/a'
            for affil in author.iter('Affiliation'):
                affiliations.append(affil.text)
            auth=(lastname,forename,affiliations)
            entry['authors'].append(auth)
        #OK! now it can find things with multiple terms and put them into one tuple
        for journal in article.iter('Journal'):
            try:
                ISO=journal.find('.//ISOAbbreviation').text
                entry['journal']=ISO
                #print(ISO)
            except AttributeError:
                ISO='n/a'
                #print(ISO)
            #this one was easy
            try:
                year=journal.find('.//Year').text
            except AttributeError:
                year='n/a'
            try:
                month=journal.find('.//Month').text
            except AttributeError:
                month='n/a'
            try:
                day=journal.find('.//Day').text
            except AttributeError:
                day='n/a'
            #print(year,month,day)
            entry['date']=(year,month,day)
            #apparently some things dont have days or even months associated w their pub dates
            #this makes things a little more annoying.
        for abstract in article.iter('Abstract'):
            abst=[]
            for section in abstract.iter('AbstractText'):
                abst.append(section.text)
                #print(abs)
            entry['abstract']=abst
        # '...no abstract provided' i don't feel like handling that exception
        for citation in article.iter('ArticleId'):
            #print(citation.text)
            entry['citations'].append(citation.text)
            #print(entry['citations'])
        for ID in article.iter('PMID'):
            entry['PMID']=(ID.text)
        yield entry



# ok so how are we to filter?
journalkeywords=[]
def journalfilter(index,journalkeywords,relevant_journals, irrelevant_journals):
    '''
        manual review of journal titles that match keywords. auto-includes all
        papers from the selected 'relevant' journals in the final list of papers.
        Returns a list of journals specified to be interesting.
    '''
    for keyw in journalkeywords:
        for entry in index:
            if keyw in entry['journal'] and entry['journal'] not in irrelevant_journals and entry['journal'] not in relevant_journals:
                print(entry['journal'])
                prompt=input('Accept Journal? [y/n] ')
                if prompt == 'y':
                    relevant_journals.add(entry['journal'])
                if prompt == 'n':
                    irrelevant_journals.add(entry['journal'])
    return relevant_journals

keywords=[]
with open(sys.argv[1], newline='') as words:
   keys=csv.reader(words) 
   for line in keys:
       keywords.append(line)

def titlefilter(index,keywords):
    '''
    

    Parameters
    ----------
    index : List of each article in a particular archive, processed from raw xml by YieldEntries
    abskeywords : Keywords of interest
    antikeywords : keywords to throw out

    Returns
    -------
    relevant : List of papers with titles that suggest interesting content

    '''
    relevant=[]
    for entry in index:
        for keyw in keywords[0]:
            try:
                if keyw in str(entry['title']) and entry['title'] not in relevant:
                    if any(antik in str(entry['title']) for antik in keywords[1]):
                        continue
                    else:
                        print(entry['title'])
                        relevant.append(entry)
            except:
                continue
    return relevant


def abstractfilter(index,keywords):
    """
    

    Parameters
    ----------
    index : List of each article in a particular archive, processed from raw xml by YieldEntries
    abskeywords : Keywords of interest
    antikeywords : keywords to throw out

    Returns
    -------
    relevant : List of papers from index that have keywords of interest in their abstracts

    """
    
    relevant=[]
    for entry in index:
        for keyw in keywords[0]:
            try:
                if keyw in str(entry['abstract']):
                    if any(antik in str(entry['abstract']) for antik in keywords[1]):
                        continue
                    else:
                        print(entry['title'])
                        relevant.append(entry)
            except:
                continue
    return relevant

dicttemplate={'authors':[],'date':[],'title':'','journal':'','abstract':'','citations':[],'PMID':''}
relevant_journals=set()
irrelevant_journals=set()
for file in glob.glob('*.gz'):
    f = gzip.open(file, 'rb')
    file_content = f.read().decode()
    f.close()
    articleset=ET.fromstring(file_content)
   # this is actually an elementtree root element, not a tree itself. i think everything
   # still works though
    index=[]
    for article in YieldEntries(articleset,dicttemplate):
        index.append(article)
        #this is the generator that iteratively goes through all files in baseline.
        #it only needs 1 file's worth if entries at a time bc the filtered stuff is
        #getting put in another list, which is hopefully 50-100x smaller.
    relevants=[]
    relevant_titles=titlefilter(index,keywords)
    for entries in relevant_titles:
        if entries not in relevants:
            relevants.append(entries)
    relevant_abstracts=abstractfilter(index,keywords)
    for moreentries in relevant_abstracts:
        if moreentries not in relevants:
            relevants.append(moreentries)
    # relevantjournals=journalfilter(index,journalkeywords,relevant_journals,irrelevant_journals)
    # for entry in index:
    #     for journal in relevantjournals:
    #         if entry['journal'] == journal:
    #             #print(entry['title'])
    #             relevants.append(entry)
    #the journal title filter just ended up being to much stuff to sift through manually. 
    filepath=os.path.join(os.getcwd(), 'pmd_filtered\Index_'+ str(file)[9:24])
    pubmedentries=bz2.BZ2File(filepath, 'w')
    pickle.dump(relevants,pubmedentries)
    pubmedentries.close()
    #this bit here will dump compressed, filtered archives into whatever directory
    #was cd'd at the top, be that pmd-baseline or wherever else you want stuff going
