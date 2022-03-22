# imports

import os
import re
import sqlite3
import requests
import logging
import pandas as pd
import numpy  as np

from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy import create_engine


# Data Collection

def data_collection(url, headers):
	# request to URL
	page = requests.get(url, headers=headers)

	# Beautiful Soup object
	soup = BeautifulSoup(page.text, 'html.parser')

	# =============== Products Data =============================

	products = soup.find('ul', class_='products-listing small')
	product_list = products.find_all('article', class_='hm-product-item')

	# product_id
	product_id = [p.get('data-articlecode') for p in product_list]

	# product_category
	product_category = [p.get('data-category') for p in product_list]

	# product_name
	product_list = products.find_all('a', class_='link')
	product_name = [p.get_text() for p in product_list]

	# price
	product_list = products.find_all('span', class_='price regular')
	product_price = [p.get_text() for p in product_list]

	data = pd.DataFrame([product_id, product_category, product_name, product_price]).T
	data.columns = ['product_id', 'product_category', 'product_name', 'product_price']

	return data

# Data Collection by product

def data_collection_by_product(data, headers):

	# empty dataframe
	df_composition_s = pd.DataFrame()

	# empty list to collect names of unique columns for all products composition
	aux = []

	# pattern dataframe with the columns I want to collect from each product if exist
	df_pattern = pd.DataFrame(columns=['Art. No.', 'Composition', 'Fit'])

	for i in range(len(data)):
   
		# API Requests
		url = 'https://www2.hm.com/en_us/productpage.' + data.loc[i, 'product_id'] + '.html'
   		
		logger.debug('Product URL: %s', url)
		
		# page = requests.get(url, headers=headers)
		page = ''
		while page == '':
			try:
				page = requests.get(url,headers=headers)
				break
			except:
				print("Connection refused by the server..")
				print("ZZzzzz...")
				time.sleep(3)
				print("Now let's continue...")
				continue 
		
		# Beautiful Soup object
		soup = BeautifulSoup(page.text, 'html.parser')
		
		# ================ Product Color ==================
		
		gen_color_list = soup.find_all('a', class_='filter-option miniature active') + soup.find_all('a', class_='filter-option miniature')
		
		# product colors
		product_colors = [c.get('data-color') for c in gen_color_list]
		
		# product id
		product_id = [c.get('data-articlecode') for c in gen_color_list]
		
   		# dataframe color
		df_color = pd.DataFrame(list(zip(product_id, product_colors)))
		df_color.columns = ['product_id', 'product_colors']
		
		for j in range(len(df_color)):
	
			# API Requests
			url = 'https://www2.hm.com/en_us/productpage.' + df_color.loc[j, 'product_id'] + '.html'
			logger.debug('Color: %s', url)
			
			page = requests.get(url, headers=headers)
			
			# Beautiful Soup object
			soup = BeautifulSoup(page.text, 'html.parser')
			
			# ================ Product Name ==================
			product_name = soup.find('h1', class_='primary product-item-headline')
			product_name = product_name.get_text()
			
			# ================ Product Price ==================
			product_price = soup.find_all('div', class_='primary-row product-item-price')
			product_price = re.findall(r'\d+\.?\d+', product_price[0].get_text())[0]
			
			# ================ Product Composition ==================
			
			gen_composition_list = soup.find_all('div', class_='details-attributes-list-item')
			gen_composition = [list(filter(None, d.get_text().split('\n'))) for d in gen_composition_list]
			
			df_composition = pd.DataFrame(gen_composition).T
			
			# rename column names
			df_composition.columns = df_composition.iloc[0]
			
			# delete first row
			df_composition = df_composition.iloc[1:]
			
			# drop columns
			df_composition = df_composition.drop(columns=['messages.garmentLength', 'messages.waistRise', 'messages.clothingStyle', 'Care instructions', 'Material', 'Collection', 'Description', 'Imported', 'Concept', 'Nice to know', 'More sustainable materials', 'Size'], axis=1, errors='ignore')
			
			# reset index
			df_composition = df_composition.reset_index(drop=True)
			
			# remove pocket lining, shell, and lining
			df_composition['Composition'] = df_composition['Composition'].replace('Pocket lining: ', '', regex=True)
			df_composition['Composition'] = df_composition['Composition'].replace('Shell: ', '', regex=True)
			df_composition['Composition'] = df_composition['Composition'].replace('Lining: ', '', regex=True)
			
			# guarantee the same selected columns for all products
			aux = aux + df_composition.columns.tolist()
			df_composition = pd.concat([df_pattern, df_composition], axis=0)
			
			# fill NA with info from the cell above
			df_composition = df_composition.fillna(method='ffill')
			
			# rename columns
			df_composition.columns = ['product_id', 'composition', 'fit']
			df_composition['product_name'] = product_name
			df_composition['product_price'] = product_price
			
			# merge composition and color dataframes
			df_composition = pd.merge(df_composition, df_color, how='left', on='product_id')
			
			
			# all products details
			df_composition_s = pd.concat([df_composition_s, df_composition], axis=0)
			
			# extract style id and article id from product_id
			# generate style id + composition id
	df_composition_s['style_id'] = df_composition_s['product_id'].apply(lambda x: x[:-3])
	df_composition_s['article_id'] = df_composition_s['product_id'].apply(lambda x: x[-3:])
			
	# scrapy datetime
	df_composition_s['scrapy_datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			
	return df_composition_s

# Data Cleaning

def data_cleaning(data_product):

	df_data = data_product

	# product_name
	df_data['product_name'] = df_data['product_name'].str.replace('\n', '')
	df_data['product_name'] = df_data['product_name'].str.replace('  ', '')
	df_data['product_name'] = df_data['product_name'].str.replace('', '')
	df_data['product_name'] = df_data['product_name'].str.replace(' ', '_').str.lower() 

	# product_price
	df_data['product_price'] = df_data['product_price'].astype(float)

	# product_color
	df_data['product_colors'] = df_data['product_colors'].str.replace(' ', '_').str.replace('/', '_').str.lower()

	# fit
	df_data['fit'] = df_data['fit'].apply(lambda x: x.replace(' ', '_').lower() if pd.notnull(x) else x)

	# =============== Column 'composition' has several information ======================

	# break the actual column 'composition' by comma into a new dataframe, df1
	df1 = df_data['composition'].str.split(',', expand=True).reset_index(drop=True)

	# create a new empty dataframe with the columns from 'composition': cotton | polyester | spandex | elastomultiester 
	# same len as data
	df_ref = pd.DataFrame(index=np.arange(len(df_data)), columns=['cotton', 'polyester', 'spandex', 'elastomultiester'])

	# fill up and attach df_ref to data column by column:

	# -------------- cotton --------------

	df_cotton_0 = df1.loc[df1[0].str.contains('Cotton', na=True), 0]
	df_cotton_0.name = 'cotton'
	df_cotton_1 = df1.loc[df1[1].str.contains('Cotton', na=True), 1]
	df_cotton_1.name = 'cotton'

	df_cotton = df_cotton_0.combine_first(df_cotton_1)  # combine cotton

	df_ref = pd.concat([df_ref, df_cotton], axis=1) # concatenate with df_ref
	df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated(keep='last')]

	# -------------- polyester --------------

	df_polyester = df1.loc[df1[0].str.contains('Polyester', na=True), 0]
	df_polyester.name = 'polyester'

	df_ref = pd.concat([df_ref, df_polyester], axis=1) # concatenate with df_ref
	df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated(keep='last')]

	# -------------- spandex --------------
	
	df_spandex_1 = df1.loc[df1[1].str.contains('Spandex', na=True), 1]
	df_spandex_1.name = 'spandex'
	df_spandex_2 = df1.loc[df1[2].str.contains('Spandex', na=True), 2]
	df_spandex_2.name = 'spandex'

	df_spandex = df_spandex_1.combine_first(df_spandex_2)  # combine spandex

	df_ref = pd.concat([df_ref, df_spandex], axis=1) # concatenate with df_ref
	df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated(keep='last')]

	# -------------- elastomultiester --------------

	df_elastomultiester = df1.loc[df1[1].str.contains('Elastomultiester', na=True), 1]
	df_elastomultiester.name = 'elastomultiester'

	df_ref = pd.concat([df_ref, df_elastomultiester], axis=1) # concatenate with df_ref
	df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated(keep='last')]


	# join of composition combined with product_id
	df_aux = pd.concat([df_data['product_id'].reset_index(drop=True), df_ref], axis=1) 

	# format composition data
	df_aux['cotton'] = df_aux['cotton'].apply(lambda x: int(re.search('\d+', x).group(0))/100 if pd.notnull(x) else x)
	df_aux['polyester'] = df_aux['polyester'].apply(lambda x: int(re.search('\d+', x).group(0))/100 if pd.notnull(x) else x)
	df_aux['spandex'] = df_aux['spandex'].apply(lambda x: int(re.search('\d+', x).group(0))/100 if pd.notnull(x) else x)
	df_aux['elastomultiester'] = df_aux['elastomultiester'].apply(lambda x: int(re.search('\d+', x).group(0))/100 if pd.notnull(x) else x)

	# final join
	df_aux = df_aux.groupby('product_id').max().reset_index().fillna(0) # chooses max value of each column to keep
	df_data = pd.merge(df_data, df_aux, on='product_id', how='left')

	# drop columns
	df_data = df_data.drop(columns=['composition'], axis=1)

	# drop duplicates
	df_data = df_data.drop_duplicates()

	# reset index
	df_data = df_data.reset_index(drop=True)

	return df_data


# Data Insert

def data_insert(df_data):

	data_insert = df_data[[
	'product_id',
	'style_id',
	'article_id',
	'product_name',
	'product_colors',
	'fit',
	'product_price',
	'cotton',
	'polyester',
	'spandex',
	'elastomultiester',
	'scrapy_datetime'  
	]]

	# create database connection
	conn = create_engine('sqlite:///database_hm.sqlite', echo=False)

	# data insert
	data_insert.to_sql('showroom', con=conn, if_exists='append', index=False)

	return None


if __name__ == '__main__':

	# logging
	path = '/Users/fabic/repos/Data_Engineering/'
	if not os.path.exists(path + 'Logs'):
		os.makedirs(path + 'Logs')

	logging.basicConfig(
		filename = path + 'Logs/webscrapping_hm.log',
		level = logging.DEBUG,
		format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
		datefmt = '%Y-%m-%d %H:%M:%S'
	)

	logger = logging.getLogger('webscraping_hm')

	# parameters and constants
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'}
	url = 'https://www2.hm.com/en_us/men/products/jeans.html'

	# data collection
	data = data_collection(url, headers)
	logger.info('data collection done')

	# data collection by product
	data_product = data_collection_by_product(data, headers)
	logger.info('data collection by product done')

	# data cleaning
	data_product_cleaned = data_cleaning(data_product)
	logger.info('data product cleaned done')

	# data insertion
	data_insert(data_product_cleaned)
	logger.info('data insertion done')	