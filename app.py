from flask import Flask, render_template
import random
from flask import request, redirect
import matplotlib
matplotlib.use('Agg') # this allows PNG plotting

from kcrwFuncs import *


app = Flask(__name__)
store = pandas.HDFStore('static/playlist-2015.h5')
x = store['kcrw_df'] # load it back into x

@app.route('/search', methods=['POST'])
def my_form_post():
    text = request.form['text']
    processed_text = text.title()
    return redirect("search?title="+processed_text)

@app.route('/search', methods=['GET', 'POST'])
def indexPage(): 
    song = request.args.get('title')

    if not song:
        plotPng = 'let-it-happen-2015.png'
        song = "Let It Happen"
        song_count = len(x.loc[x['title']==song])
    else:    
        song_count = len(x.loc[x['title']==song])
        plotPng = plot_yearly_song_by_month(x, song)
        
    previewPng = ["can't-keep-checking-my-phone-2015.png","heart-is-full-2015.png","hot-coals-2015.png","by-fire-2015.png"]
    previewList = ["Can't Keep Checking My Phone", "Heart Is Full", "Hot Coals", "By Fire"]
    with open('static/KCRW-top-10-2015.json') as data_file:    
        dj_info = json.load(data_file)

    return(render_template(
        'figures.html',
        plotPng=plotPng,
        previewPng=previewPng,
        previewList=previewList,
        songCount=song_count,
        song=song,
        dj_top10s=dj_info))

@app.route('/')
def kcrwIndex(): 
    with open('static/KCRW-total-top-10-2015.json') as data_file:    
        kcrw_info = json.load(data_file)
    with open('static/KCRW-total-top-2015-histories.json') as data_file:    
        history_plots = json.load(data_file)
    return(render_template(
        'kcrw_index.html',
        kcrw_top10s=kcrw_info,
        historyPlots=history_plots,))

@app.route('/hosts')
def hostIndex(): 
    with open('static/KCRW-top-10-2015.json') as data_file:    
        dj_info = json.load(data_file)
    return(render_template(
        'host_index.html',
        dj_top10s=dj_info))

@app.route('/hosts/<hostname>')
def hostPage(hostname):
    with open('static/KCRW-top-10-2015.json') as data_file:    
        dj_info = json.load(data_file)
    with open('static/published_kcrw_dj_top_10s_2015.json') as data_file:    
        dj_info_published = json.load(data_file)
    with open('static/data_kcrw_dj_top_10s_2015.json') as data_file:    
        dj_info_data = json.load(data_file)
    return(render_template(
        'host.html',
        dj_top10s=dj_info,
        dj_top10s_data=dj_info_data,
        dj_top10s_published=dj_info_published,
        hostname=hostname))

@app.route('/plots')  
def plotsIndex():  
    pics = os.listdir('static/year_track_summary/')  
    return render_template("plots.html", pics=pics) 

if __name__ == '__main__':
    app.debug=True
    #app.run()
    app.run(host='128.97.32.123')


