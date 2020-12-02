#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Author: Cong Zhu
#Date: 2020/12
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


# ### Search by key words and specified time frame, return two dataframes: 1) abstract dataframe (PMID,title,abstract,publication date) 2) authors dataframe in long format (PMID, author names)

# In[ ]:


'''modify the pathway as necessary'''
os.chdir("")


# In[2]:


class pubmed_record:
    #search_term = "oncology drug repurposing"
    #start_time = '2020/03/01'
    #end_time = '2020/10/10'
    def __init__(self,search_term = None,start_time= None,end_time= None):
        self.search_term=input("Please enter a keyword:")
        self.start_time, self.end_time = input("Range of publication time to be searched (YYYY/MM/DD - YYYY/MM/DD): ").split("-")
        #self.start_time=input("Enter a start date (YYYY/MM/DD): \n")
        #self.end_time=input("Enter an end date (YYYY/MM/DD): \n")
        
    
    def tab_generate(self):
        search_term_list = self.search_term.split()
        if len(search_term_list) >1:
            search_term_url = "+".join(search_term_list)
        else:
            search_term_url = search_term



        start_y = self.start_time.split('/')[0]
        start_m = self.start_time.split('/')[1]
        start_d = self.start_time.split('/')[2]

        end_y = self.end_time.split('/')[0]
        end_m = self.end_time.split('/')[1]
        end_d = self.end_time.split('/')[2]

        #url = 'https://pubmed.ncbi.nlm.nih.gov/?term=%28{}%29+AND+%28%28%22{}%2F{}%2F{}%22%5BDate+-+Modification%5D+%3A+%22{}%2F{}%2F{}%22%5BDate+-+Modification%5D%29%29&sort='\
        #.format(search_term_url,start_y,start_m,start_d,end_y,end_m,end_d)
        
        url_p1 = 'https://pubmed.ncbi.nlm.nih.gov/?term=({})'.format(search_term_url)
        url_p2 = '%20AND%20(({}%2F{}%2F{}%5BDate%20-%20Publication%5D%20%3A%20{}%2F{}%2F{}%5BDate%20-%20Publication%5D))'        .format(start_y,start_m,start_d,end_y,end_m,end_d)
        url = url_p1 + url_p2
        



        '''get the total number of publications'''
        soup = BeautifulSoup(urlopen(url).read(), 'html.parser')
        n_pub = int(soup.find_all("meta", attrs={'name':'log_resultcount'})[0]['content'])
        print("Number of publications:",n_pub)

        '''get number of pages'''
        total_pages = int(math.ceil(n_pub/10))
        print('Number of pages:',total_pages)

  

        df_all_paper_info = pd.DataFrame()
        df_all_author_info = pd.DataFrame()
        #for i in range(1,2):
        for i in range(1,total_pages+1):
            df_page_paper_info = pd.DataFrame()
            df_page_author_info = pd.DataFrame()


            '''Browse contents by page'''
            url2 = url + '&page={}'.format(i)
            soup_page = BeautifulSoup(urlopen(url2).read(), 'html.parser')

            pmid_1page = soup_page.find_all("meta", attrs={'name':'log_displayeduids'})[0]['content'].split(",")


            '''Fetch contents of single page'''
            for pmid in pmid_1page:
                url_1paper = "https://pubmed.ncbi.nlm.nih.gov/"+pmid

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
                
                sig_paper_title = soup_1paper.find("meta", attrs={'name':'citation_title'},recursive = True)['content']

                pub_summary_paper_info = {"Title":[sig_paper_title],
                               "PMID":[pmid],
                               "Publication Date:":[sig_paper_date],
                               "Abtract":[abs_content]}
                
                pub_summary_author_info = {
                               "PMID":pmid,
                               "Authors":sig_paper_authors_list}
                

                pub_summary_df_paper_info = pd.DataFrame(pub_summary_paper_info)
                pub_summary_df_author_info = pd.DataFrame(pub_summary_author_info)

                df_page_paper_info = df_page_paper_info.append(pub_summary_df_paper_info)
                df_page_author_info = df_page_author_info.append(pub_summary_df_author_info)

            df_all_paper_info = df_all_paper_info.append(df_page_paper_info)
            df_all_author_info = df_all_author_info.append(df_page_author_info)
        return df_all_paper_info, df_all_author_info


# In[3]:


abstract_tab, author_tab = pubmed_record().tab_generate()


# In[4]:


abstract_tab.shape


# In[5]:


author_tab.shape


# In[6]:


abstract_tab.head()


# In[7]:


author_tab.head()


# In[8]:


author_tab.to_csv("author_tab.csv")
abstract_tab.to_csv("abstract_tab.csv")

