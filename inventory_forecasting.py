import pandas as pd
from fbprophet import Prophet
from multiprocessing import Pool, cpu_count
import argparse
import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient
from datetime import datetime

def train_prophet(batch):
	"""
		index or any unique key to query with
		dataframe should consist of cols 'ds' and 'y'
	"""
	key, dataframe = batch
	core = Prophet(daily_seasonality=True)
	core.fit(dataframe)
	future = core.make_future_dataframe(periods=7)
	forecast = core.predict(future)
	# core.plot_components(forecast[['ds', 'trend', 'trend_lower', 'trend_upper', 'yhat', 'yhat_lower',
	# 																'yhat_upper']])
	# core.plot(forecast[['ds', 'yhat', 'yhat_upper', 'yhat_lower']])
	# plt.savefig('./Data/demand-forecasting-kernels-only/' + str(key), format='png')
	# plt.plot(forecast[['yhat']].tail(7).values)
	# plt.show()
	
	return (key, forecast[['yhat']].tail(7))

def use_csv(file):
	csv_path = file if file != None else './Data/demand-forecasting-kernels-only/train.csv'
	df = pd.read_csv(csv_path)
	list_dfs = []
	for item in df.item.unique()[:1]:
		sanitized_df = df[df['serial'] == item][['date', 'sales']]
		sanitized_df = sanitized_df.rename(columns={'date': 'ds', 'sales': 'y'})
		list_dfs.append((item, sanitized_df))

	return list_dfs

def read_db(db):
	ds, demand, serial = [], [], []
	for document in db.equipments.find():
		item = dict()
		for serviceRecord in document['servicingRecords']:
			item['ds'] = serviceRecord['servicingDate'].strftime('%Y-%m-%d')
			item['demand'] = item['demand'] + 1 if 'demand' in item.keys() else 1
			item['serial'] = document['serial']
		
		if len(item.keys()) > 0:
			serial.append(item['serial'])
			demand.append(item['demand'])
			ds.append(item['ds'])

	df_dict = {
		'serial': serial,
		'y': demand,
		'ds': ds
	}
	df = pd.DataFrame(df_dict)
	list_dfs = []
	for item in serial:
		sanitized_df = df[df['serial'] == item][['ds', 'y']]
		if len(sanitized_df.index) > 2:
			list_dfs.append((item, sanitized_df))

	print(list_dfs)

	return list_dfs


def process(list_dfs):
	pool = Pool(2)
	results = pool.imap(train_prophet, list_dfs)
	pool.close()
	pool.join()

	for result in results:
		key, data = result
		print('for %s' % key)
		print(data)

	return results

def write_db(db, results):
	for result in results:
		key, forecast = result
		prediction = forecast['yhat'].values.toList()

		db.equipments.update_one(
			{'serial': key}, 
			{'$set': {'predictions': predictions}}
		)

	return



if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('setting', choices=['trial', 'production'])
	parser.add_argument('--path')
	args = parser.parse_args()
	list_dfs = []

	if args.setting == 'trial':
		print('starting...')
		list_dfs = use_csv(args.path)
		process(list_dfs)
	else:
		client = MongoClient('Vayusangrah.tk', 27017)
		db = client['vayusangrah']
		list_dfs = read_db(db)
		results = process(list_dfs)
		write_db(db, results)


	

