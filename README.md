# COVID 19 in England - assorted data and visualisations
---
Hello!

This is my assorted set of data and visualisations about the COVID 19 emergency in England.

I'm focussing on how COVID is developing in Upper Tier Local Authorities.

My first attempt is a series of static maps showing daily cumulative growth in the number of cases by English Upper Tier Local Authorities.  I've also made a similar series showing the daily number of cases per 100,000 people, also by UTLA. 

I have published these to the 'img' folder in this repo. The Python code published here too (NB: I'm still a Python noob so please be nice!).  

For conveniences, I have stitched the daily images into a 60 second animated GIF 
<img src="img_casecounts/covid_cum_cases.gif" width="400">
<img src="img_per100k/covid_pop_ratios.gif" width="400">

Huge thanks to Ordnance Survey for the BoundaryLine data, which I've used to create the GeoPackage of English Upper Tier Authorities, cross referenced to their parent Region.   Data is available in the 'data' folder.

I'm also massively grateful to [Tom White](https://github.com/tomwhite/covid-19-uk-data) for maintained, up-to-date tidy CSV of daily historic case counts. You'll see from the Python code that I'm reading this directly to generate the maps, saving me loads of time storing and crunching the original sources from [Public Health England](https://www.gov.uk/government/publications/covid-19-track-coronavirus-cases).   Thank you Tom!
