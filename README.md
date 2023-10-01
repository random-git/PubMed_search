# PubMed_search
Author: Cong Zhu
### Introduction 
The pubmeb crawler is multi-threaded web crawler designed to extract publication records from PubMed via user defined key words and timeframe, as well as performing post hoc data management and analyses.
![erd](https://user-images.githubusercontent.com/62033407/106549698-24053780-64d7-11eb-9211-9dabba80ad43.png)<br/>

The program consists of three modules:
1. PubMed scaping module: [pub_retrieve_thread](https://github.com/random-git/PubMed_search/blob/main/pub_retrieve_thread.py).<br/>
2. SQL database generation module: [sql_dump](https://github.com/random-git/PubMed_search/blob/main/sql_dump.py).<br/>
3. Visualization module: [visualization](https://github.com/random-git/PubMed_search/blob/main/visualization.py).<br/>
### User guide
#### Installation
Please save the following .py files in the same folder
```Python
pub_retrieve_thread.py, sql_dump.py, visualization.py
```
#### Third party packages
```Python
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
```

#### Web crawler

pub_retrieve_thread module collects paper’s title, authors, publication time, and abstract from PubMed (https://pubmed.ncbi.nlm.nih.gov/) according to user-defined keyword(s) and time frame (YYYY/MM/DD-YYYY/MM/DD).
Search results are returned as two csv files that store abstract information(PMID, paper title, publication date, abstract) and authors names(PMID and author full names) respectively. By default, the files are saved in the same working directory of the module. <br/>
First, import the module: <br/>
```Python
import pub_retrieve_thread as pr
```

Create an web crawler object and call the function:  <br/>
```Python
abstract_tab, author_tab = pr.pubmed_record().pub_tab_all_main()
```

The above function returns two pandas dataframes Abstract_tab and author_tab  that store abstract records and author names respectively.
The window will prompt the user to enter key words and time frame. Press enter button after finishing each entry otherwise kernel will keep running. Once finished, the following output will be displayed:
```
Please enter a keyword: precision radiotherapy
Number of publications: 651
Number of pages: 66
651 papers were downloaded with 53.54137420654297 seconds
```

#### SQL management

Sql_dump module loads saved csv files that contain search results and convert them into SQL database automatically. The module allows the user to extract full publication records by simply entering the author name(s) only without efforts to implement sql scripts . Extracted records will be saved in csv format.

Use the module: <br/>
```Python
import sql_dump as sdp
```
Load .csv files and convert them into SQL databases:<br/>
```Python
sdp.sql_dump('author_tab.csv', 'abstract_tab.csv')
```

The user will see following message being displayed once finished:<br/>
```
author_tab.db is created
abstract_tab.db is created
```

The above SQL databases are saved in the same directory as input .csv files.
Extract publication records by author names from SQL database: <br/>
```Python
pick_authors = sdp.pick_authors('Sarah Hazell','Katsuyuki Kiura','Mark Kidd','Lisa Bodei').pub_rec("Extract_records")
```

pick_authors: retrieve records by author names. Break entries by comma. <br/>
pub_rec: save the extracted records as .csv file. Saved file name is defined by the user. <br/>
Search results are saved in the Extract_records.csv.
