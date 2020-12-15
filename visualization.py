#!/usr/bin/env python
# coding: utf-8


#Author: Wanqi Chen
#Date: 2020/12

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

os.getcwd()

# Read .csv file and data preparation
def read_csv(path):
	data = pd.read_csv(path)
	data['Publication Month']= pd.to_datetime(data['Publication Date'],format='%Y-%m-%d').dt.to_period('M')
	data['Publication Date']= pd.to_datetime(data['Publication Date'],format='%Y-%m-%d')
	return data

# Bar Plot by Month
def bar_plot(data, save=True, x_label='Publication Date', y_label='Total Number of Publications', title='Bar Plot by Month', label_fontsize=16, axis_fontsize=12, rotation=0, title_fontsize=20, figsize=(12,8)):
	ax = data["Publication Date"].groupby(data["Publication Month"]).count().plot(kind="bar", figsize=figsize, fontsize=axis_fontsize)
	ax.set_xlabel(x_label, fontsize=label_fontsize)
	ax.xaxis.set_tick_params(rotation=rotation)
	ax.set_ylabel(y_label, fontsize=label_fontsize)
	ax.set_title(title, fontsize=title_fontsize)
	for p in ax.patches:
		ax.annotate(str(p.get_height()), (p.get_x()+0.1, p.get_height()+1))
	
	if save == True: 
		plt.savefig('bar_plot.pdf')
	
	plt.show()
	return ax


# Line Plot by Month
def line_plot(data, save=True, marker='o', x_label='Publication Date', y_label='Average Number of Daily Publications', title='Line Plot by Month', label_fontsize=16, axis_fontsize=12, rotation=0, title_fontsize=20, figsize=(12,8)):
	data["count"] = 1
	test = data["count"].groupby([data["Publication Month"], data["Publication Date"]]).size().reset_index()
	test.columns = ['Month','Date','Count']
	
	ax2 = test.groupby(test["Month"]).mean().plot(kind="line", marker=marker, figsize=figsize, fontsize=axis_fontsize)
	ax2.xaxis.set_tick_params(rotation=rotation)
	ax2.set_xlabel(x_label, fontsize=label_fontsize)
	ax2.set_ylabel(y_label, fontsize=label_fontsize)
	ax2.set_title(title, fontsize=title_fontsize)
	
	if save == True: 
		plt.savefig('line_plot.pdf')

	plt.show()
	return ax2


# Table of Descriptive Statistics
def describe(data, save=True):
	data["count"] = 1
	test = data["count"].groupby([data["Publication Month"], data["Publication Date"]]).size().reset_index()
	test.columns = ['Month','Date','Count']
	result = test.groupby(test["Month"]).describe()["Count"]
	print (result)

	if save==True:
		output = pd.DataFrame.from_records(result)
		output.to_csv("description.csv")
	return result
