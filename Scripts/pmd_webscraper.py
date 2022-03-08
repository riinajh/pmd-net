'''
    adapted from https://towardsdatascience.com/how-to-web-scrape-with-python-in-4-minutes-bc49186a8460
    parses online pubmed baseline and downloads all .xml.gz files (1114 as of 20211212)
    to the specified directory. This takes a while. 
'''
import time
import os
import urllib.request
import requests
from bs4 import BeautifulSoup as bs
os.chdir(r'C:\path\to\your\pmd-bib')
url='https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/'
response=requests.get(url)
soup=bs(response.text,"html.parser")
first=soup.findAll('a')[2124]
    #this is lazy cuz next time the baseline gets updated it'll only read the first 1062 entries
for tag in first:
    link=tag['href']
    download='https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/'+link
    urllib.request.urlretrieve(download,link)
        #this line will download to your working directory
    print(link, 'downloaded!')
    time.sleep(0.35) # so NCBI doesn't block your ip address
    #double check that this doesn't exceed what NCBI specifies as max # requests per min