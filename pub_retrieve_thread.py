#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#Author:Cong Zhu
#revision: implement multithreading with concurrent library to boost speed
import concurrent.futures
from urllib.request import urlopen, urlretrieve
import time
from bs4 import BeautifulSoup
import os
import pandas as pd
import numpy as np
import csv
import requests
import math
import datetime


# In[ ]:


'''modify as necessary'''
max_threads = 50


# In[ ]:


class pubmed_record:
    def __init__(self,search_term = None,start_time= None,end_time= None):
        self.search_term=input("Please enter a keyword:")
        self.start_time, self.end_time = input("Range of publication time to be searched (YYYY/MM/DD - YYYY/MM/DD): ").split("-")
        
    def pub_number_get(self):
    
        search_term_list = self.search_term.split()
        if len(search_term_list) >1:
            search_term_url = "+".join(search_term_list)
        else:
            search_term_url = self.search_term



        start_y = self.start_time.split('/')[0]
        start_m = self.start_time.split('/')[1]
        start_d = self.start_time.split('/')[2]

        end_y = self.end_time.split('/')[0]
        end_m = self.end_time.split('/')[1]
        end_d = self.end_time.split('/')[2]

        url_p1 = 'https://pubmed.ncbi.nlm.nih.gov/?term=({})'.format(search_term_url)
        url_p2 = '%20AND%20(({}%2F{}%2F{}%5BDate%20-%20Publication%5D%20%3A%20{}%2F{}%2F{}%5BDate%20-%20Publication%5D))'.format(start_y,start_m,start_d,end_y,end_m,end_d)
        #url_p1 = 'https://pubmed.ncbi.nlm.nih.gov/?term=%28{}%29+AND+%28%28'.format(search_term_url)
        #url_p2 = '{}%2F{}%2F{}%5BDate+-+Publication%5D+%3A+{}%2F{}%2F{}%5BDate+-+Publication%5D%29%29&size=200'.format(start_y,start_m,start_d,end_y,end_m,end_d)
        url = url_p1 + url_p2




        '''get the total number of publications'''
        soup = BeautifulSoup(urlopen(url).read(), 'html.parser')
        n_pub = int(soup.find_all("meta", attrs={'name':'log_resultcount'})[0]['content'])
        print("Number of publications:",n_pub)

        '''get number of pages'''
        total_pages = int(math.ceil(n_pub/10))
        print('Number of pages:',total_pages)

        url_page = []
        for i in range(1, total_pages+1):
            url2 = url + '&page={}'.format(i)
            url_page+= [url2]

        #return url_page[:10]
        return url_page
    
    def pmid_get(self,url):
        #url = self.pub_number_get()
        soup_page = BeautifulSoup(urlopen(url).read(), 'html.parser')

        pmid_1page = soup_page.find_all("meta", attrs={'name':'log_displayeduids'})[0]['content'].split(",")
        time.sleep(0.3)
        return pmid_1page
    
    def pmid_all(self,url_allpage):
        
        threads = min(max_threads, len(url_allpage))

        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
             pmids = executor.map(self.pmid_get, url_allpage)
        
        return pmids
    
    def pmid_get_main(self):
        
        pmid_all = self.pmid_all(self.pub_number_get())
        
        pmid_url=[]
        for pmid_1page in list(pmid_all):
            for pmid in pmid_1page:
                p_url = "https://pubmed.ncbi.nlm.nih.gov/"+pmid
                pmid_url+=[p_url]
        
        return pmid_url
    
    
    def pub_tab(self,url_1paper):
    
        start_d = self.start_time.split('/')[2]

        pub_record = []
        soup_1paper = BeautifulSoup(urlopen(url_1paper).read(), 'html.parser')
        try:
            abs_content = soup_1paper.find("meta", attrs={'name':'citation_abstract'})['content']
        except:
            abs_content = "No abstract available"

        sig_paper_authors = soup_1paper.find_all("meta", attrs={'name':'citation_author'})
        sig_paper_authors_list = list()
        for a in sig_paper_authors:
            sig_paper_authors_list += [a.get('content')]

        try:
            sig_paper_date = soup_1paper.find("meta", attrs={'name':'citation_publication_date'},recursive = True)['content']
        except TypeError:
            sig_paper_date = soup_1paper.find("meta", attrs={'name':'citation_online_date'},recursive = True)['content']

        sig_paper_date_break = sig_paper_date.split("/")

        if len(sig_paper_date_break)==1:
            sig_paper_date2 = '/'.join([sig_paper_date_break[0],"01","01"])
        elif len(sig_paper_date_break)==2:   
            sig_paper_date2 = '/'.join(sig_paper_date_break+[start_d])
        else:
            sig_paper_date2 = sig_paper_date
        
        if sig_paper_date2>self.end_time:
            sig_paper_date2 = self.end_time
        else:
            sig_paper_date2 = sig_paper_date2

        sig_paper_title = soup_1paper.find("meta", attrs={'name':'citation_title'},recursive = True)['content']
        
        pmid = url_1paper.split("/")[3]

        pub_summary_paper_info = {"Title":[sig_paper_title],
                       "PMID":[pmid],
                       "Publication Date":[sig_paper_date2],
                       "Abstract":[abs_content]}

        pub_summary_author_info = {
                       "PMID":pmid,
                       "Authors":sig_paper_authors_list}


        pub_summary_df_paper_info = pd.DataFrame(pub_summary_paper_info)
        pub_summary_df_author_info = pd.DataFrame(pub_summary_author_info)
        pub_record += [pub_summary_df_paper_info,pub_summary_df_author_info]
        time.sleep(0.3)
        
        return(pub_record)
    
    def pub_tab_all(self):
        url_allpage = self.pmid_get_main()
        threads = min(max_threads, len(url_allpage))

        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
             records_all = executor.map(self.pub_tab, url_allpage)
        
        return records_all
    
    
    def pub_tab_all_main(self):
        
        df_paper_info = pd.DataFrame()
        df_author_info = pd.DataFrame()

        t0 = time.time()
        records_all = self.pub_tab_all()
        
        
        for records in list(records_all):
            df_paper_info = df_paper_info.append(records[0])
            df_author_info = df_author_info.append(records[1])
            
        df_author_info.to_csv("author_tab.csv", index=False)
        df_paper_info.to_csv("abstract_tab.csv", index=False)
        
        t1 = time.time()
        print(f"{df_paper_info.shape[0]} papers were downloaded with {t1-t0} seconds")
        
        return df_paper_info, df_author_info

