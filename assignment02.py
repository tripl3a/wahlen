#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 20:26:31 2017

@author: Arndt Allhorn
"""

#%%
################
# Assignment 1 #
################

import csv
from collections import defaultdict
 
zweitstimmenGruppe = defaultdict(float)

with open('ergebnisse.csv', newline='') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=';')
    for row in csvreader:
        try:
            # cumulate value of "zweitstimmen" under the key of "gruppe"
            # and do some cleansing
            if row[2] == "DIE LINKE.":
                zweitstimmenGruppe["DIE LINKE"] += float(row[4])
            elif row[2] == "GRÜNE/B 90":
                zweitstimmenGruppe["GRÜNE"] += float(row[4])
            else:
                zweitstimmenGruppe[row[2]] += float(row[4])
        except ValueError:
            pass # do nothing

gueltige = zweitstimmenGruppe["Gültige"]
zweitstimmenGruppe.pop("Gültige") # remove non-party
zweitstimmenGruppe.pop("Ungültige") # remove non-party
partyPercentage = defaultdict(float) # for storing key-value-pairs of party (Gruppe) and their relativ result

for k in zweitstimmenGruppe:
    if zweitstimmenGruppe[k] > 0:
        percentage = zweitstimmenGruppe[k]/gueltige
        partyPercentage[k] = percentage
        print (k + ";" + str(round(percentage*100,1)) + "%")

#%%
################
# Assignment 2 #
################
        
### merge every party below 5% ###

sonstige = 0.0
sonstigeGruppen = list();

# sum up the results of groups below 5%
for k in partyPercentage:
    if partyPercentage[k]<0.05:
        sonstige += partyPercentage[k]
        sonstigeGruppen.append(k)

# remove groups below 5% from dictionary
for i in sonstigeGruppen:
    partyPercentage.pop(i)
    
# add sonstige to dictionary
partyPercentage["Sonstige"] = sonstige

# print out the dictionary
for k in partyPercentage:
    print (k + ";" + str(round(partyPercentage[k]*100,1)) + "%")

#%%

### plot the data ###

import matplotlib.pyplot as plt

# color coding
colors = defaultdict()
colors["AfD"] = '#8B4726' # #009EE0
colors["CDU"] = '#000000'
colors["CSU"] = '#008AC5'
colors["DIE LINKE"] = '#BE3075'
colors["FDP"] = '#FFED00'
colors["GRÜNE"] = '#64A12D'
colors["SPD"] = '#EB001F'
colors["Sonstige"] = 'grey'

x=[]
y=[]
c=[]
for i in partyPercentage.items():    
    x.append(i[0])
    y.append(i[1])
    c.append(colors[i[0]])

barchart = plt.bar(x,y, color=c)

# display the numeric values on top of the bar
for a,b in zip(x, y): 
    plt.text( a, b, str(round(b*100,1)) )

plt.title("Bundestagswahl 2017: Ergebnis Zweitstimmen")
plt.show()
