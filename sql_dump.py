#!/usr/bin/env python
# coding: utf-8
# Author: Cong Zhu
# In[107]:


import os
from pathlib import Path
import sqlite3
import pandas as pd
import csv




# In[32]:


def sql_dump(*args):
    for file in args:
        fname = file.split(".")[0]
        dbname = '.'.join([fname,'db'])
        
        f_tmp = pd.read_csv(file)
        conn = sqlite3.connect(dbname)
        f_tmp.to_sql(fname, conn, if_exists = 'replace')
        
        print("{} is created".format(dbname))
        conn.close()


# In[187]:


class pick_authors:
    def __init__(self,*args):
        self.authornames = args
        
    def namelist(self):
        nlist_new = list()
        for name in self.authornames:
            name_break = name.split(" ")


            first_name_init = name_break[0][0]
            last_name = name_break[1]
            if len(name_break) ==2:
                name_alter = " ".join([first_name_init, last_name])
                nlist_new.append(name_alter)
            else:
                mid_name_init = name_break[1][0]
                last_name = name_break[-1]
                name_alter = " ".join([first_name_init, mid_name_init, last_name])
                name_alter2 = " ".join([name_break[0], mid_name_init, last_name])


                nlist_new.append(name_alter)
                nlist_new.append(name_alter2)
    
            
        nlist_new = nlist_new + list(self.authornames)
        return nlist_new
        
    
    def pub_rec(self, save_name):
        conn = sqlite3.connect('abstract_tab.db')
        c = conn.cursor()
        c.execute("ATTACH ? AS author_tab", ('author_tab.db',))

        sql_script = '''SELECT abst.Title,abst.PMID,auth.Authors,abst.Abstract FROM abstract_tab abst, author_tab auth
             where auth.Authors IN {} and (auth.PMID = abst.PMID)'''.format(tuple(self.namelist()))

        c.execute(sql_script)
        result = c.fetchall()

        fp = open('{}.csv'.format(save_name), 'w',newline='')
        myFile = csv.writer(fp)
        myFile.writerow(['Title','PMID','Author Name','Abstract'])
        myFile.writerows(result)
        fp.close()
        conn.commit()
        conn.close()

