#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2018-01-04

@author: Arndt Allhorn
"""

# prerequisites:
#conda install basemap
#conda install pyshp

from os import chdir
chdir("/home/arndt/git-reps/wahlen/")

from mpl_toolkits.basemap import Basemap
import shapefile # from library pyshp
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

""" Import the shapefile(s) """

shp_file_base='Geometrie_Wahlkreise_19DBT_geo'
dat_dir='shapefiles/'+shp_file_base +'/'
sf = shapefile.Reader(dat_dir+shp_file_base)

print ('number of shapes imported: ',len(sf.shapes()),"\n")
print ('geometry attributes in each shape:')
for name in dir(sf.shape()):
    if not name.startswith('__'):
       print (name)

""" Plot using Basemap """

map = Basemap(llcrnrlon=5.87,llcrnrlat=47.27,urcrnrlon=15.04,urcrnrlat=55.06,
              resolution='i', projection='tmerc', lat_0 = 51.16, lon_0 = 10.45)
map.drawmapboundary(fill_color='aqua')
map.fillcontinents(color='#ddaa66',lake_color='aqua')
map.drawcoastlines()

map.readshapefile(dat_dir+shp_file_base, shp_file_base)

""" Import elected direct candidates """

df_elected = pd.read_csv("btw17_gewaehlte_utf8.csv", delimiter=";")
df_elected = df_elected[df_elected["Gewählt_Wahlkreis_Nr"]>0]
df_elected = df_elected[["Gewählt_Wahlkreis_Nr","Gewählt_Wahlkreis_Bez","Name","Vorname","Partei_KurzBez","Gewählt_Land"]]
df_elected["Name"] = df_elected["Vorname"] + " " + df_elected["Name"]
df_elected = df_elected.drop("Vorname", axis=1)

""" Add candidate names to map """

for shapeRec in sf.shapeRecords():    
    x_lon = np.zeros((len(shapeRec.shape.points),1))
    y_lat = np.zeros((len(shapeRec.shape.points),1))
    for ip in range(len(shapeRec.shape.points)):
        x_lon[ip] = shapeRec.shape.points[ip][0]
        y_lat[ip] = shapeRec.shape.points[ip][1]
    
    mid_x_lon = (min(x_lon)+max(x_lon))/2
    mid_y_lat = (min(y_lat)+max(y_lat))/2
    x, y = map(mid_x_lon, mid_y_lat) # convert lon,lat to x,y coordinates on the map
    
    wahlkreis=shapeRec.record[0]
    candidate = df_elected[df_elected["Gewählt_Wahlkreis_Nr"]==wahlkreis]["Name"].iloc[0]
    
    plt.text(x, y, candidate, fontsize=10, ha='center',va='center')

plt.show()
#plt.savefig("constmap.png",dpi=900) # export plot as image