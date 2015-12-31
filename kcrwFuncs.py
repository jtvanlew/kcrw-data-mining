import json
import requests
from gmusicapi import Mobileclient
import numpy as np
import datetime
import pandas
from collections import Counter
import matplotlib.pyplot as plt
import os, sys
from matplotlib.pyplot import cm 

import matplotlib
csfont = {'fontname':'Roboto'}
hfont = {'fontname':'Roboto'}
matplotlib.rcParams.update({'font.size': 16})

# TO-DO:

# cumulative DJ popular songs
# give an artist, plot the song count over time
# something about time of day playing

# seasonal favorites -- summer hits, etc.
# dj played with most variety (and fewest replays)

# track spelling errors and frequency per dj to harrass them.
# DJ seeding 
# DJ seeding awards -- most influential, biggest follower (poser/imitator)
# song grouping? e.g. david bowie near gardens & villa, tame impala and UMO
# "pie chart" of genres
# releaes date of song -- playing new or old
# most tracks from single artist
# artist with most plays
# average amount of months a dj plays a particular song
# most popular song 
# number of unique tracks / number of total tracks for each DJ

# DONE:
# how many DJ played a song - plot_yearly_song
# find popular song from a DJ and plot its play counts over time - plot yearly song
# who played school night and why? - NOT FOUND

def pull_kcrw_data(start_page, stop_page):
	# ORIGINAL LOOP FOR PULLING DATA FROM SERVERS. USE THIS ONCE AND THEN SAVED TO HDF5
	df = []
	for i in np.arange(start_page, stop_page+1, 1):
	    print("Scanning page "+str(i)+" on kcrw site...")
	    r = requests.get("http://tracklist-api.kcrw.com/Simulcast/all/"+str(i))
	    results = json.loads(r.text)
	    df.append(pandas.read_json(r.text))
	x = pandas.concat(df)
	return x

def pull_eclectic24_data(start_page, stop_page):
	# ORIGINAL LOOP FOR PULLING DATA FROM SERVERS. USE THIS ONCE AND THEN SAVED TO HDF5
	df = []
	for i in np.arange(start_page, stop_page+1, 1):
	    print("Scanning page "+str(i)+" on kcrw site...")
	    r = requests.get("http://tracklist-api.kcrw.com/Music/all/"+str(i))
	    results = json.loads(r.text)
	    df.append(pandas.read_json(r.text))
	x = pandas.concat(df)
	return x

def get_dj_list(x):
	dj_list = list(set(x['host']))
	return dj_list

def save_dj_images(dj_list):
	import urllib
	for host in dj_list:
		host = host.replace(' ', '-').lower()
		host = host.replace('.', '')
		host_path = "http://www.kcrw.com/people/"+host+"/@@images/square_image/feature"
		print(host_path)
		urllib.urlretrieve(host_path, "host_images/"+host+".jpg")

def get_song_artist(x, song):
	artists = x.loc[x['title']==song]['artist']
	return artists

def find_N_most_popular_songs(x, N):
	# top 10 songs played by kcrw and artist name
	artists, titles = get_artists_titles_lists(x)
	sorted_df = get_sorted_counts(titles)
	return sorted_df[-N:]

def find_N_most_popular_artists(x, N):
	# top 10 songs played by kcrw and artist name
	artists, titles = get_artists_titles_lists(x)
	sorted_df = get_sorted_counts(artists)
	return sorted_df[-N:]

# def find_N_most_popular_albums(x, N):
# 	# top 10 songs played by kcrw and artist name
# 	albums = [i for i in x['album']]
# 	sorted_df = get_sorted_counts(albums)
# 	top_N_strings = []
# 	for key, val in sorted_df[-N:].iteritems():
# 	 	print(key, val)
# 	return top_N_strings

def find_DJs_favorite_song(x, host):
	# FIND MOST POPULAR SONG PLAYED BY GIVEN DJ
	x = x.loc[x['host']==(host)]
	artists, titles = get_artists_titles_lists(x)
	title_counts = Counter(titles)
	df = pandas.DataFrame.from_dict(title_counts, orient='index')
	popular_song_title = df.idxmax()
	popular_song_plays = df.max() 
	# popular_song_data = x.loc[x['title'] == popular_song_title[0]]
	song = {}
	song[x.loc[x['title'] == popular_song_title[0]]['artist'].values[0]]=popular_song_title[0]
	return song, popular_song_plays.values[0]

def get_artists_titles_lists(x):
	artists = [i for i in x['artist']]
	titles = [i for i in x['title']]
	return artists, titles

def get_sorted_counts(field):
	field_counts = Counter(field)
	df = pandas.DataFrame.from_dict(field_counts, orient='index')
	df.columns = ['count']
	sorted_df = pandas.DataFrame.sort(df, columns='count')
	return sorted_df

def plot_yearly_song_by_week(x, song_title):
	color_idx =[[31./255., 119./255., 180./255.],
				[174./255., 199./255., 232./255.],
				[255./255., 127./255., 14./255.],
				[255./255., 187./255., 120./255.],
				[44./255., 160./255., 44./255.],
				[152./255., 223./255., 138./255.],
				[214./255., 39./255., 40./255.],
				[255./255., 152./255., 150./255.],
				[96./255., 99./255., 106./255.],
				[165./255., 172./255., 175./255.],
				[65./255., 68./255., 81./255.],
				[143./255., 135./255., 130./255.],
				[188./255., 189./255., 34./255.],
				[219./255., 219./255., 141./255.],
				[23./255., 190./255., 207./255.],
				[158./255., 218./255., 229./255.],
				[207./255., 207./255., 207./255.],
				[227./255., 119./255., 194./255.],
				[247./255., 182./255., 210./255.],]
	# NOTE: DATA SET ASSUMES A YEAR'S WORTH OF DATA
	dj_list = list(set(x['host']))
	# color=iter(cm.rainbow(np.linspace(0,1,len(dj_list))))
	dj_dict = {}
	month_dict = {}
	stacked_values = np.zeros(52)
	fig, ax = plt.subplots()
	c = 0
	for k, dj in enumerate(dj_list):
		# pull out subset of a given Dj
		subset = x.loc[x['host']==(dj)]
		# pull out subset of dj subset for a given month
		for i in np.arange(1, 53, 1):
			subset_month = subset[subset.date.dt.week == i]
			month_dict[i] = len(subset_month.loc[subset_month['title'] == song_title])
			dj_dict[dj] = month_dict
		# c = next(color)
		if np.sum(dj_dict[dj].values()) > 0:
			plt.bar(dj_dict[dj].keys(), dj_dict[dj].values(), 
				    bottom=stacked_values, 
				    align='center', 
				    color=color_idx[c], 
				    label=dj)
			c += 1
			for i in np.arange(0,52, 1):
				stacked_values[i] += dj_dict[dj].values()[i]
	handles, labels = ax.get_legend_handles_labels()
	plt.legend(handles[::-1], labels[::-1],loc='best', **csfont)

	# plt.xticks(np.arange(1,13,1))
	# labels = [item.get_text() for item in ax.get_xticklabels()]
	# labels = ['January', 'February', 'March', 'April', 'May', 'June', 'July', "August", 'September', 'October', "November", "December"]

	# ax.set_xticklabels(labels, rotation=90)
	# plt.xlim(0,13)
	ax.yaxis.grid()
	plt.ylabel("Play count")
	plt.title("KCRW DJ play counts for\n"+x.loc[x['title'] == song_title]['artist'].values[0]+' - '+song_title, **csfont)
	fig.tight_layout()
	return [fig, ax]

def plot_yearly_song_by_month(x, song_title):
	color_idx =[[31./255., 119./255., 180./255.],
				[174./255., 199./255., 232./255.],
				[255./255., 127./255., 14./255.],
				[255./255., 187./255., 120./255.],
				[44./255., 160./255., 44./255.],
				[152./255., 223./255., 138./255.],
				[214./255., 39./255., 40./255.],
				[255./255., 152./255., 150./255.],
				[96./255., 99./255., 106./255.],
				[165./255., 172./255., 175./255.],
				[65./255., 68./255., 81./255.],
				[143./255., 135./255., 130./255.],
				[188./255., 189./255., 34./255.],
				[219./255., 219./255., 141./255.],
				[23./255., 190./255., 207./255.],
				[158./255., 218./255., 229./255.],
				[207./255., 207./255., 207./255.],
				[227./255., 119./255., 194./255.],
				[247./255., 182./255., 210./255.],]
	# NOTE: DATA SET ASSUMES A YEAR'S WORTH OF DATA
	dj_list = list(set(x['host']))
	# color=iter(cm.rainbow(np.linspace(0,1,len(dj_list))))
	dj_dict = {}
	month_dict = {}
	stacked_values = np.zeros(12)

	fig, ax = plt.subplots(figsize=(7, 8), dpi=80)
	c = 0
	for k, dj in enumerate(dj_list):
		# pull out subset of a given Dj
		subset = x.loc[x['host']==(dj)]
		# pull out subset of dj subset for a given month
		for i in np.arange(1, 13, 1):
			subset_month = subset[subset.date.dt.month == i]
			month_dict[i] = len(subset_month.loc[subset_month['title'] == song_title])
			dj_dict[dj] = month_dict
		if np.sum(dj_dict[dj].values()) > 0:
			plt.bar(dj_dict[dj].keys(), dj_dict[dj].values(), 
				    bottom=stacked_values, 
				    align='center', 
				    color=color_idx[c], 
				    label=dj)
			c += 1
			for i in np.arange(0,12, 1):
				stacked_values[i] += dj_dict[dj].values()[i]
	handles, labels = ax.get_legend_handles_labels()
	plt.legend(handles[::-1], labels[::-1],loc='best', prop={'size':12})

	plt.xticks(np.arange(1,13,1))
	labels = [item.get_text() for item in ax.get_xticklabels()]
	labels = ['January', 'February', 'March', 'April', 'May', 'June', 'July', "August", 'September', 'October', "November", "December"]

	ax.set_xticklabels(labels, rotation=90, fontsize = 12, **hfont)
	plt.setp(ax.get_yticklabels(), fontsize=12)
	plt.xlim(0,13)
	plt.ylim([0, 50])
	ax.yaxis.grid()
	plt.ylabel("Play count", fontsize = 12)
	plt.title("KCRW DJ play counts: \n"+x.loc[x['title'] == song_title]['artist'].values[0]+"'s\n"+song_title, fontsize=11, loc='left', **hfont)
	fig.tight_layout()
	clean_title = song_title.replace(' ', '-').lower()
	save_img_name = clean_title+'-2015.png'
	save_img_path = 'static/year_track_summary/'+save_img_name
 	plt.savefig(save_img_path, transparent=True)
 	plt.close()
	return save_img_name

def plot_dj_track_counts(x):
	# LOOP THROUGH DJS, COUNT TRACK PLAYS, PLOT.
	# THIS IS NOT VERY USEFUL RIGHT NOW, IT JUST SHOWS COUNTS WITHOUT ANY TITLES OR ANYTHING
	dj_list = list(set(x['host']))
	fig, ax = plt.subplots()
	plt.ylim([0, 100])
	for k, dj in enumerate(dj_list):
		# pull out subset of a given Dj
		subset = x.loc[x['host']==(dj)]
		# create lists of DJ tracks
		artists, titles = get_artists_titles_lists(subset)
		title_counts = Counter(titles)
		df = pandas.DataFrame.from_dict(title_counts, orient='index')
		df.columns = ['count']
		sorted_df = pandas.DataFrame.sort(df, columns='count')
		plt.plot(sorted_df, label=dj)
	plt.legend(loc='best')
	ax.yaxis.grid()

def monthly_dj_data_saving(x):
	# CREATE A NUMPY FILE FOR EACH ARTIST FOR EACH MONTH, TO BE USED FOR
	# SEARCHING ON GOOGLE AFTERWARD
	dj_list = list(set(x['host']))
	for k, dj in enumerate(dj_list):
		# pull out subset of a given Dj
		subset = x.loc[x['host']==(dj)]
		# pull out subset of dj subset for a given month
		for i in np.arange(1, 13, 1):
			subset_month = subset[subset.date.dt.month == i]
			# create lists of DJ tracks
			artists = [a for a in subset_month['artist']]
			titles = [t for t in subset_month['title']]
			if not os.path.exists(dj):
				os.makedirs(dj)
			np.save(dj+'/'+'2015-'+str(i)+'-artists.npy', artists)
			np.save(dj+'/'+'2015-'+str(i)+'-titles.npy', titles)

def google_playlists(x):
	api = Mobileclient()
	api.login('jonvanlew@gmail.com', 'rtqjkpidxwxddpur', Mobileclient.FROM_MAC_ADDRESS)
	all_playlists = api.get_all_playlists(incremental=False, include_deleted=False)
	dj_list = list(set(x['host']))
	for k, dj in enumerate(dj_list):
		# pull out subset of a given Dj
		subset = x.loc[x['host']==(dj)]
		print("\n   Analyzing "+dj+" Playlists...\n")
		# pull out subset of dj subset for a given month
		for i in np.arange(1, 12, 1):
			print('Now loading Month: '+str(i))
			artists = np.load(dj+'/'+'2015-'+str(i)+'-artists.npy')
			if len(artists) == 0:
				break
			titles  = np.load(dj+'/'+'2015-'+str(i)+'-titles.npy')
			# playlist_exists = False
			# playlist_name = 'KCRW DJ '+host+', Tracks of 2015-'+str(i)
			# print("Searching for playlist named: " + playlist_name)
			# for playlist in all_playlists:
			# 	if playlist['name'] == playlist_name:
			# 		playlist_exists = True
			# 		playlist_id = playlist['id']
			# 		print("Playlist exists, adding new songs to playlist: "+playlist_name)
			# if not playlist_exists:
			# 	playlist_id = api.create_playlist(playlist_name, description=None, public=False)
			# 	print("Playlist is new, creating playlist and adding new songs to: "+playlist_name)
			search_google(api, artists, titles)

def search_google(api, artists, titles):
	for t, artist in enumerate(artists):
		title = titles[t]
		print("Searching for: " + artist + ' - ' + title)
		aa_search = api.search_all_access(artist+' '+title, max_results=1)
		if len(aa_search['song_hits']) > 0:
			# aa_song_id = aa_search['song_hits'][0]['track']['nid']
			print("SUCCESS:       " + aa_search['song_hits'][0]['track']['artist']
				+ ' - ' + aa_search['song_hits'][0]['track']['title']+'\n')
			# api.add_songs_to_playlist(playlist_id, aa_song_id)
		else:
			print("WARNING:       "+artist + ' - ' + title + " .... wasn't found in google music\n")

def get_first_plays(x):
	song_dict = {}
	x_sorted = pandas.DataFrame.sort(x, columns="datetime", ascending=True)
	for row in x_sorted.iterrows():
		song = row[1]['title']
		host = row[1]['host']
		datetime = row[1]['datetime']
		if song not in song_dict:
			song_dict[song] = {'first_play':datetime, 'first_host':host}
		else:
			if host not in song_dict[song]:
				song_dict[song][host] = datetime
	return song_dict