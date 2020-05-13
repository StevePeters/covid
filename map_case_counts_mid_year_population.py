#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 15:49:03 2020

@author: stevepeters
"""

import pandas as pd
import geopandas as gpd
import geoplot
import mapclassify
import requests
from io import StringIO
from datetime import datetime
import matplotlib.pyplot  as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable


def drawChart( gPos, ctitle, setForMap ):
    
    ax=fig.add_subplot(gPos)
    ax.axis('off')
    tmax=setForMap['popRatio'].max()
    setForMap.plot(column='popRatio', cmap=cMap, linewidth=0.2, ax=ax, vmin=vmin, vmax=vmax, edgecolor='0.8')
    ax.set_title(ctitle,fontdict=fontSubhead)
    for idx, row in setForMap.iterrows():
            if row.popRatio == tmax:
                ax.text(row.coords[0]+0.2, row.coords[1], s=row['Area'], horizontalalignment='right', fontsize=3, bbox={'facecolor': 'white', 'alpha':0.5, 'pad': 1, 'edgecolor':'none'})
    
  
# load UTLA boundaries
latestDate=datetime.strptime('2020-03-20', "%Y-%m-%d")
utla_geom_url = "data/utla_regions.gpkg"
utla_geom_data = gpd.read_file(utla_geom_url)
utla_geom_data['coords'] = utla_geom_data['geometry'].apply(lambda x: x.representative_point().coords[:])
utla_geom_data['coords'] = [coords[0] for coords in utla_geom_data['coords']]


# load 2018 mid year population estimates
df_mypops = pd.read_csv("data/2018_mid_year_population_estimates.csv") 
df_mypops["MYE_2018_total"] = df_mypops["MYE_2018_total"].apply(pd.to_numeric,errors='coerce')

# load latest case counts
utla_case_counts_url="https://coronavirus.data.gov.uk/downloads/csv/coronavirus-cases_latest.csv"
s=requests.get(utla_case_counts_url).text
df=pd.read_csv(StringIO(s),parse_dates=True)
df.rename(columns={'Daily lab-confirmed cases': 'TotalCases'}, inplace=True)
df.rename(columns={'Specimen date': 'Date'}, inplace=True)
df.rename(columns={'Area code': 'AreaCode'}, inplace=True)
df.rename(columns={'Area name': 'Area'}, inplace=True)
df.drop(columns=['Previously reported daily cases', 'Change in daily cases', 'Cumulative lab-confirmed cases', 'Previously reported cumulative cases', 'Change in cumulative cases', 'Cumulative lab-confirmed cases rate'], inplace=True)


# fix data type errors
df.drop(df.loc[df['Area type']=="Region"].index, inplace=True)
df.drop(df.loc[df['Area type']=="Nation"].index, inplace=True)
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

# join to population estimates to get max value
df_pr=df.set_index('AreaCode').join(df_mypops.set_index('AreaCode'))
df_pr.reset_index(inplace=True)
df_pr['popRatio']=((df_pr.cumCases/df_pr.MYE_2018_total) * 100000)


#  get unique list of dates
dict_date_range=df_pr.Date.unique()
dict_date_range.sort()
dict_regions=utla_geom_data.RGN19CD.unique()

# set up map parameters
fontMainhead = {'family': 'serif',
    'color':  'darkred',
    'weight': 'bold',
    'size': 12,
}
cMap='OrRd'
vmin= 0

for td in dict_date_range:
    
    # filter case list by dates
    tdd=datetime.strptime(td, "%Y-%m-%d")
    if tdd>=latestDate:    
        tdt = tdd.strftime("%d %b %Y")
        dfilter=df_pr['Date'] == td
        thisDateDF=(df_pr[dfilter])
        setForMap = utla_geom_data.set_index('AreaCode').join(thisDateDF.set_index('AreaCode'))
        setForMap["cumCases"].fillna(0, inplace = True)
        setForMap["MYE_2018_total"].fillna(0, inplace = True)
        setForMap["popRatio"].fillna(0, inplace = True)
        vmax=setForMap["popRatio"].max()

        fig = plt.figure(constrained_layout=False,figsize=[50,10])
        fig.suptitle('COVID-19 daily cases per 100,000 people in English Upper Tier LAs: ' + tdt, fontdict=fontMainhead, x=0.505)
        
        grid = fig.add_gridspec(ncols=5, nrows=4, figure=fig, wspace=0.2, hspace=0.1)
        ax_eng = fig.add_subplot(grid[:3, :2])
        ax_eng.axis('off')
        
        # set up map classifier
        npopr=setForMap['popRatio'].fillna(0)
        scheme=mapclassify.NaturalBreaks(npopr, k=5)
        #geoplot.choropleth(
        #    setForMap, hue=npopr, scheme=scheme,
        #    cmap='Greens',ax=ax_eng
        #)
        
        setForMap.plot(column='popRatio', cmap=cMap, linewidth=0.2, ax=ax_eng, vmin=vmin, vmax=vmax, edgecolor='0.8')
        
        

        # create figure and axes for Matplotlib
        fontSubhead = {'family': 'serif',
            'color':  'darkred',
            'weight': 'normal',
            'size': 10,
        }
        ax_eng.set_title('England' ,fontdict=fontSubhead)
        
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
            
        fig.text( 0.205,0.93,'Source: Public Health England, ONS 2018 mid-year population estimates',  fontsize=8)
        fig.text( 0.76,0.93,'Made by @SemanticSteve', fontsize=8)
        fig.subplots_adjust(top=0.7)
        grid.tight_layout(fig, rect=[0.2, 0.2, 0.9, 0.9])
        fig.subplots_adjust(top=0.7)
        fig.set_size_inches(w=11.69,h=8.27)
        
        fig_name = "img_per100k/" + td + '_utla_covid_pop_ratios.png'
        fig.savefig(fig_name, bbox_inches='tight', dpi=300)
        plt.close(fig)
            
