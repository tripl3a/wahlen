#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 15:38:39 2017

@author: Arndt Allhorn
"""

import numpy as np
import pandas
import csv
from collections import defaultdict

### set working directory

from os import chdir
chdir("/home/arndt/Documents/DSM/PythonDS/")

################
# Assignment 3 #
################

#----------------------------------------------------------------------------
# 1. Implement the method of Saint-Lesque/Schepers in a reusable manner
#----------------------------------------------------------------------------
   
# method of Saint-Lesque/Schepers to distribute seats
# votes = list of votes
# returns: list of seats (in same order as the input list of votes)
def distributeSeats(total_seats, votes, debug=False):
    seats=[0]*len(votes)
    total_votes = np.array(votes).sum()    
    d = round(total_votes/total_seats, 0)
    
    assigned_seats = 0
    while assigned_seats != total_seats: 
        i = 0
        for e in votes:
            seats[i] = round(e/d, 0) 
            if debug: print("e=" + str(e) + " seats[i]=" + str(seats[i]))
            i=i+1
        
        assigned_seats = np.array(seats).sum()
        if assigned_seats < total_seats:
            d=d-1
        elif assigned_seats > total_seats:
            d=d+1
        else:
            break
        
        if debug: print("d=" + str(d) + "; assigned_seats=" + str(assigned_seats))
        if debug: print("")
        
    return seats

#----------------------------------------------------------------------------
# Import second vote results
#----------------------------------------------------------------------------

# records that don't constitute parties
blacklist = set(("Wahlberechtigte",
                 "Wähler",
                 "Gültige",
                 "Ungültige"))

def numberofvotes(record, votetype):
    """Return the number of votes value as a number.
       Depending on the vote type, 1st or 2nd votes are returned."""
    if (votetype == 1):
        value = record['erststimmen']
    elif (votetype == 2):
        value = record['zweitstimmen']
    else:
        raise ('Invalid votetype provided. Parameter value must be 1 or 2.')
    
    if value == '-':
        return 0
    return int(value)

cleaned_names = {
    "DIE LINKE.":"DIE LINKE",
    "GRÜNE/B 90":"GRÜNE"
    }

# data driven approach to clean the names (by using a dict)
def clean_name(name):
    return cleaned_names.get(name, name) # 2nd parameter is the default value, if get returns None 

# for easier summing up, use a default dict defaulting to 0
result_2nd_votes = defaultdict(int)

with open("ergebnisse.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter=';')
    for record in reader:
        if record['gruppe'] in blacklist:
            continue # skip extra records
        result_2nd_votes[clean_name(record['gruppe'])] += numberofvotes(record, 2)

# drop entries with zero zweitstimmen
result_2nd_votes = {k: v for k, v in result_2nd_votes.items() if v != 0}

total = sum(v for v in result_2nd_votes.values())

# compute fractions whilst dropping parties below 5%
result_2nd_votes_rel = {k: v/total*100 for k, v in result_2nd_votes.items() if v/total*100>=5}
# drop parties below 5%
whitelist = set(result_2nd_votes_rel.keys())
result_2nd_votes = {k: v for k, v in result_2nd_votes.items() if k in whitelist}

#----------------------------------------------------------------------------
# Import all results
#----------------------------------------------------------------------------

with open("ergebnisse.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter=';')
    result_list = []    
    for record in reader:
        if record['gruppe'] in blacklist:
            continue # skip extra records
        list_entry = [v for v in record.values()]
        list_entry = [list_entry[0], list_entry[1], clean_name(list_entry[2]), numberofvotes(record, 1), numberofvotes(record, 2)]
        result_list.append(list_entry)

#-----------------------------------------------------------------------------
# 2. For each constituency, compute the winning party of the direct seat (Direktmandat). 
#-----------------------------------------------------------------------------

dfResults = pandas.DataFrame(result_list, columns=["state","constituency","party","votes1","votes2"])
dfResults[["votes1","votes2"]] = dfResults[["votes1","votes2"]].apply(pandas.to_numeric) # convert votes to numeric

dfDirectMandates=dfResults.sort_values(["constituency","votes1"], ascending=[True,False]) # sort by consituency asc, first votes desc
dfDirectMandatesTemp=dfDirectMandates
dfDirectMandates=dfResults.groupby(["constituency"]).head(1) # select top 1 from each constituency

### For each state, compute the number of direct seats per party

dfDirectSeatsPerState = dfDirectMandates.groupby(["state","party"]).count() # count rows grouped by state and party
dfDirectSeatsPerState = dfDirectSeatsPerState["votes1"].rename("direct_seats") # rename series accordning to content
dfDirectSeatsPerState = pandas.DataFrame({'state':dfDirectSeatsPerState.index.levels[0]
                  , 'party': dfDirectSeatsPerState.index.levels[1][dfDirectSeatsPerState.index.labels[1]]  
                    , 'direct_seats':dfDirectSeatsPerState.values}) # convert series to dataframe
   
#-----------------------------------------------------------------------------
# 3. Compute a distribution of 598 seats to the states, 
#    according to the population count in population.csv (source: bundeswahlleiter.de)
#-----------------------------------------------------------------------------

# Import population
population = defaultdict(None)
with open("population.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter=';')
    for record in reader:
        population[int(record['state'])] = (record['name'], record['population']) # tuple values

seatsPerState = np.zeros((len(population), 3), dtype=int)

i=0
for k, v in population.items():
    seatsPerState[i,0]=int(k) # state key
    seatsPerState[i,1]=int(v[1]) # state population
    i=i+1

seatsPerState[:,2] = distributeSeats(598, seatsPerState[:,1]) # assign seat distribution to 3rd column
seatsPerState = pandas.DataFrame(seatsPerState, columns=["state","population","seats"])
state_names = []
for s in seatsPerState["state"]:
    state_names.append(population[s][0])
seatsPerState["state_nm"] = state_names
    
print(seatsPerState)

#%%
#-----------------------------------------------------------------------------
# 4. For each state, compute the assignment of seats to the parties according to the share of Zweitstimmen.
#-----------------------------------------------------------------------------

dfVotesPerStateAndParty = dfResults.groupby(["state","party"], as_index=False).sum() 
dfVotesPerStateAndParty = dfVotesPerStateAndParty[ dfVotesPerStateAndParty["party"].isin(whitelist) ] 

dfListSeats = None

for k in set(dfVotesPerStateAndParty.groupby(["state"], as_index=False).sum()["state"]):
    for index, row in seatsPerState.iterrows():
        if row["state"] == int(k):
            seats2dist = row["seats"]
            
            # distribute seats according to Zweitstimmen
            dfCurrentState = dfVotesPerStateAndParty[ dfVotesPerStateAndParty["state"]==str(k) ]
            
            distributedSeats = distributeSeats(seats2dist, list(dfCurrentState["votes2"]), False)
            distributedSeats = list(zip([k] * len(distributedSeats) # state number
                                , [population.get(int(k))[0]] * len(distributedSeats)  # state name
                                , dfCurrentState["party"]
                                , distributedSeats))
            
            result = pandas.DataFrame(distributedSeats, columns=["state","state_nm","party","list_seats"])
            result = result.merge(dfCurrentState, left_on=["state", "party"], right_on=["state", "party"], how='inner')
            if dfListSeats is None: 
                dfListSeats = result
            else:
                dfListSeats = dfListSeats.append(result, ignore_index=True)
            
print(dfListSeats)

#%%
#-----------------------------------------------------------------------------
# 5. Print out a list of states (by name) and parties with number of direct seats and list seats, 
# as well as the number of seats by  which the direct seats are larger than the list seats (Überhangmandate) 
# (0 if the number is not larger). Produce a CSV output of the form
#-----------------------------------------------------------------------------

dfUeberhang = dfListSeats.merge(dfDirectSeatsPerState
                                 , left_on=["state", "party"]
                                 , right_on=["state", "party"]
                                 , how='outer')[["state_nm", "party","direct_seats", "list_seats"]]
dfUeberhang["direct_seats"].fillna(0, inplace=True)
dfUeberhang["ueberhang"] = dfUeberhang["direct_seats"] - dfUeberhang["list_seats"]
dfUeberhang["ueberhang"] = dfUeberhang["ueberhang"].apply(lambda x:0 if x<0 else x) # replace ueberhang values < 0

print(dfUeberhang)

# export csv file
pandas.DataFrame.to_csv(dfUeberhang, path_or_buf="dfUeberhang.csv", index=False)

    