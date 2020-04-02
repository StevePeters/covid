#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 15:49:03 2020

@author: stevepeters
"""

import pandas as pd
import geopandas as gpd
import mapclassify as mc
import requests
from io import StringIO
from datetime import datetime
import matplotlib.pyplot  as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable


def drawChart( gPos, ctitle, setForMap ):
    
    ax=fig.add_subplot(gPos)
    ax.axis('off')
    setForMap.plot(column='cumCases', cmap=cMap, linewidth=0.2, ax=ax, vmin=vmin, vmax=vmax, edgecolor='0.8')
    ax.set_title(ctitle,fontdict=fontSubhead)
    
  
# load UTLA boundaries
utla_geom_url = "/Users/stevepeters/Documents/___Steve Peters/__COVID/utla_regions.gpkg"
utla_geom_data = gpd.read_file(utla_geom_url)

# load latest case counts
utla_case_counts_url="https://raw.githubusercontent.com/tomwhite/covid-19-uk-data/master/data/covid-19-cases-uk.csv"
s=requests.get(utla_case_counts_url).text
df=pd.read_csv(StringIO(s),parse_dates=True)

# fix data type errors
df.drop(df.loc[df['Country']=="Scotland"].index, inplace=True)
df.drop(df.loc[df['Country']=="Wales"].index, inplace=True)
df["TotalCases"] = df["TotalCases"].apply(pd.to_numeric,errors='coerce')
df.loc[df.Area=='To be confirmed', 'AreaCode'] = "TBC"
df.loc[df.Area=='awaiting clarification', 'AreaCode'] = "AWC"
df.loc[df.Area=='Awaiting confirmation', 'AreaCode'] = "AWC"
df.loc[df.Area=='Bournemouth', 'AreaCode'] = "E06000058"
df.loc[df.Area=='Poole', 'AreaCode'] = "E06000058"
df.loc[df.Area=='Resident outside Wales', 'AreaCode'] = "ROW"
df.loc[df.Area=='Unknown', 'AreaCode'] = "UNK"


cumsums = df.groupby(['AreaCode', 'Date']).sum().fillna(0).groupby(level=0).cumsum()
df.reset_index(inplace=True)
df.set_index(['AreaCode', 'Date'], inplace=True)
df['cumCases'] = cumsums
df.reset_index(inplace=True)

#  get unique list of dates
dict_date_range=df.Date.unique()
dict_regions=utla_geom_data.RGN19CD.unique()

# set up map parameters
fontMainhead = {'family': 'serif',
    'color':  'darkblue',
    'weight': 'bold',
    'size': 13,
}
cMap='YlGnBu'
vmin= 0
vmax=df["cumCases"].max()

for td in dict_date_range:
    
    # filter case list by dates
    tdd=datetime.strptime(td, "%Y-%m-%d")
    tdt = tdd.strftime("%d %b %Y")
    dfilter=df['Date'] == td
    thisDateDF=(df[dfilter])
    setForMap = utla_geom_data.set_index('AreaCode').join(thisDateDF.set_index('AreaCode'))
    
    fig = plt.figure(constrained_layout=False,figsize=[50,10])
    fig.suptitle('COVID-19 Cases in English Upper Tier LAs, by region: ' + tdt, fontdict=fontMainhead, x=0.47)
    
    grid = fig.add_gridspec(ncols=5, nrows=4, figure=fig, wspace=0.2, hspace=0.1)
    ax_eng = fig.add_subplot(grid[:3, :2])
    ax_eng.axis('off')
    setForMap.plot(column='cumCases', cmap=cMap, linewidth=0.2, ax=ax_eng, vmin=vmin, vmax=vmax, edgecolor='0.8')

    
    # create figure and axes for Matplotlib
    fontSubhead = {'family': 'serif',
        'color':  'darkred',
        'weight': 'normal',
        'size': 10,
    }
    ax_eng.set_title('England - ' ,fontdict=fontSubhead)
    
    # Create colorbar as a legend
    sm = plt.cm.ScalarMappable(cmap=cMap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm._A = []
    divider = make_axes_locatable(ax_eng)
    cax1 = divider.append_axes("left", size="2%", pad=0.05)
    fig.colorbar(sm, cax=cax1, orientation="vertical")   
    regList={}
    setForMap.set_index('RGN19CD')
    rowCounter=0
    colCounter=2
    
    for region in dict_regions:
       
        rfilter=setForMap['RGN19CD'] == region
        trset=(setForMap[rfilter])
        trname=trset['RGN19NM'][0]
        if trname=='Yorkshire and The Humber':
            trname='Yorks & Humbs'
        regList[region]={}
        regList[region]['title']=trname
        regList[region]['set']=trset
        regList[region]['gpos']=grid[rowCounter, colCounter]
        if colCounter==4:
            rowCounter=rowCounter+1
            colCounter=2
        else:
            colCounter=colCounter+1
            
    for region in regList:
        drawChart( regList[region]['gpos'], regList[region]['title'], regList[region]['set'] )
        
    fig.text( 0.21,0.93,'Source: Public Health England')
    fig.text( 0.73,0.93,'Made by @SemanticSteve')
    fig.subplots_adjust(top=0.7)
    grid.tight_layout(fig, rect=[0.2, 0.2, 0.9, 0.9])
    fig.subplots_adjust(top=0.7)
    fig.set_size_inches(w=11,h=7)
    
    fig_name = "img/" + td + '_utla_covid_cases.png'
    fig.savefig(fig_name,  dpi=300)
    plt.close(fig)
            
