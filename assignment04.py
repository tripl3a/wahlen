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
chdir("/home/arndt/Documents/DSM/PythonDS/assignments")

################
# Assignment 3 #
################

#----------------------------------------------------------------------------
# 1. Implement the method of Saint-Lesque/Schepers in a reusable manner
#----------------------------------------------------------------------------
   
def distributeSeats(total_seats, votes, debug=False, steps=1):
    """
    Method of Saint-Lesque/Schepers to distribute seats
    votes = list of votes
    returns: list of seats (in same order as the input list of votes)
    """
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
            d=(d-steps)+d%steps
        elif assigned_seats > total_seats:
            d=(d+steps)-d%steps
        else:
            break
        
        if debug: print("d=" + str(d) + "; assigned_seats=" + str(assigned_seats))
        if debug: print("")
    
    print("FINAL: d=" + str(d) + "; assigned_seats=" + str(assigned_seats) + "; total votes: " + str(total_votes))
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

# obtain state names by state key from population dict
seatsPerState["state_nm"] = [population[s][0] for s in seatsPerState["state"]]
    
print(seatsPerState)

#-----------------------------------------------------------------------------
# 2. For each constituency, compute the winning party of the direct seat (Direktmandat). 
#-----------------------------------------------------------------------------

dfResults = pandas.DataFrame(result_list, columns=["state","constituency","party","votes1","votes2"])
dfResults[["state","constituency","votes1","votes2"]] = dfResults[["state","constituency","votes1","votes2"]].apply(pandas.to_numeric) 

dfDirectMandates=dfResults.sort_values(["state","constituency","votes1"], ascending=[True,True,False])
# select top 1 from each constituency:
dfDirectMandates=dfDirectMandates.groupby(["state","constituency"]).head(1)

### For each state, compute the number of direct seats per party

# count rows grouped by state and party:
dfDirectSeatsPerState = dfDirectMandates.groupby(["state","party"], as_index=False).count() 
# rename series accordning to content:
dfDirectSeatsPerState = dfDirectSeatsPerState.rename(index=str, columns={"votes1": "direct_seats"})
# only columns "state","party","direct_seats" remain:
dfDirectSeatsPerState = dfDirectSeatsPerState.drop(["constituency", "votes2"], axis=1)
dfDirectSeatsPerState = dfDirectSeatsPerState.merge(seatsPerState[["state_nm","state"]]
                                                    , left_on=["state"], right_on=["state"], how='inner')

#-----------------------------------------------------------------------------
# 4. For each state, compute the assignment of seats to the parties according to the share of Zweitstimmen.
#-----------------------------------------------------------------------------

dfVotesPerStateAndParty = dfResults.groupby(["state","party"], as_index=False).sum() 
dfVotesPerStateAndParty = dfVotesPerStateAndParty.drop(["constituency"], axis=1)
dfVotesPerStateAndParty = dfVotesPerStateAndParty[ dfVotesPerStateAndParty["party"].isin(whitelist) ] 

# obtain state names by state key from population dict
dfVotesPerStateAndParty["state_nm"] = [population[s][0] for s in dfVotesPerStateAndParty["state"]]

dfListSeats = None

for k in set(dfVotesPerStateAndParty.groupby(["state"], as_index=False).sum()["state"]):
    for index, row in seatsPerState.iterrows():
        if row["state"] == int(k):
            seats2dist = row["seats"]
            
            # distribute seats according to Zweitstimmen
            dfCurrentState = dfVotesPerStateAndParty[ dfVotesPerStateAndParty["state"]==k ]
            
            distributedSeats = distributeSeats(seats2dist, list(dfCurrentState["votes2"]), False)
            distributedSeats = list(zip([k] * len(distributedSeats) # state number
                                , dfCurrentState["party"]
                                , distributedSeats))
            
            result = pandas.DataFrame(distributedSeats, columns=["state","party","list_seats"])
            result = result.merge(dfCurrentState, left_on=["state", "party"], right_on=["state", "party"], how='inner')
            if dfListSeats is None: 
                dfListSeats = result
            else:
                dfListSeats = dfListSeats.append(result, ignore_index=True)
            
print(dfListSeats)

#-----------------------------------------------------------------------------
# 5. Print out a list of states (by name) and parties with number of direct seats and list seats, 
# as well as the number of seats by  which the direct seats are larger than the list seats (Überhangmandate) 
# (0 if the number is not larger). Produce a CSV output of the form
#-----------------------------------------------------------------------------

dfUeberhang = dfListSeats.merge(dfDirectSeatsPerState[["state", "party","direct_seats"]]
                                 , left_on=["state", "party"]
                                 , right_on=["state", "party"]
                                 , how='outer')[["state","state_nm", "party","direct_seats", "list_seats"]]
dfUeberhang["direct_seats"].fillna(0, inplace=True)
dfUeberhang["ueberhang"] = dfUeberhang["direct_seats"] - dfUeberhang["list_seats"]
dfUeberhang["ueberhang"] = dfUeberhang["ueberhang"].apply(lambda x:0 if x<0 else x) # replace ueberhang values < 0

print(dfUeberhang)

# export csv file
pandas.DataFrame.to_csv(dfUeberhang, path_or_buf="dfUeberhang.csv", index=False)

# compute the Mindessitzzahl

dfUeberhang["Mindestsitzzahl"] = dfUeberhang["list_seats"] + dfUeberhang["ueberhang"]
dfUeberhang.groupby(["party"]).sum()["Mindestsitzzahl"]
sum(dfUeberhang["Mindestsitzzahl"])
dfUeberhang[dfUeberhang["party"]=="CDU"]["Mindestsitzzahl"].sum()

# alternativ for total sum:
mindestsitzzahl = sum([max(x,y) for x,y in zip(dfUeberhang["direct_seats"], dfUeberhang["list_seats"])])

# create data frame with party and 2nd votes columns
dfSeatsPerPartyBy2ndVotes = pandas.DataFrame(list(result_2nd_votes.items()), columns=["party","votes2"])
# join Mindessitzzahl
dfSeatsPerPartyBy2ndVotes = dfSeatsPerPartyBy2ndVotes.merge(dfUeberhang.groupby(["party"], as_index=False).sum()[["party","Mindestsitzzahl"]]
                                ,how='inner',left_on="party",right_on="party")
dfSeatsPerPartyBy2ndVotes["allocated_seats"] = 0

# add seat distribution according to 2nd votes
# Mindessitzzahl is being raised by 1, until each party gets it's Mindessitzzahl
while list(dfSeatsPerPartyBy2ndVotes["allocated_seats"]) < list(dfSeatsPerPartyBy2ndVotes["Mindestsitzzahl"]):
    dfSeatsPerPartyBy2ndVotes["allocated_seats"] = distributeSeats(mindestsitzzahl, dfSeatsPerPartyBy2ndVotes["votes2"])
    mindestsitzzahl = mindestsitzzahl + 1

    
def get_sorted_direct_seats(sort_keys, party_filter=None):
    """returns a list of direct seats"""
    if (party_filter==None):
        return list(dfUeberhang.sort_values(by=sort_keys)["direct_seats"])
    else:
        return list(dfUeberhang[dfUeberhang["party"]==party_filter].sort_values(by=sort_keys)["direct_seats"])

def get_sorted_ueberhang(sort_keys, party_filter=None):
    """returns a list of ueberhang values"""
    if (party_filter==None):
        return list(dfUeberhang.sort_values(by=sort_keys)["ueberhang"])
    else:
        return list(dfUeberhang[dfUeberhang["party"]==party_filter].sort_values(by=sort_keys)["ueberhang"])

def get_sorted_min_seats(sort_keys, party_filter=None):
    """returns a list of minimum seats"""
    if (party_filter==None):
        return list(dfUeberhang.sort_values(by=sort_keys)["Mindestsitzzahl"])
    else:
        return list(dfUeberhang[dfUeberhang["party"]==party_filter].sort_values(by=sort_keys)["Mindestsitzzahl"])

def get_sorted_votes2(sort_keys, party_filter=None):
    """returns a list of 2nd votes"""
    if (party_filter==None):
        return list(dfVotesPerStateAndParty.sort_values(by=sort_keys)["votes2"])
    else:
        return list(dfVotesPerStateAndParty[dfVotesPerStateAndParty["party"]==party_filter].sort_values(by=sort_keys)["votes2"])

def get_sorted_parties():
    """returns alphabetically sorted list of parties"""
    return list(dfSeatsPerPartyBy2ndVotes.sort_values(by=["party"])["party"])

def get_sorted_allocated_seats():
    """"returns a list of allocated seats sorted by party"""
    return list(dfSeatsPerPartyBy2ndVotes.sort_values(by=["party"])["allocated_seats"])


def final_seat_assignment():
    """ 
    Distributes the total number of seats per party by 2nd votes.
    Ensures that the following condition is met for each party: 
        (# distributed seats >= # minimum seats) on state level   
    
    Returns:
    A list containing # of distributed seats
    """
    parties = get_sorted_parties()
    allocated_seats = get_sorted_allocated_seats()    
    #list(zip(parties, allocated_seats))
    #pandas.concat([parties, allocated_seats], axis=1)
    distributed_seats = []
    for i in range(0, len(parties)):
        list_votes2 = get_sorted_votes2(["state"], parties[i])  
        list_min_seats = get_sorted_min_seats(["state"], parties[i])     
        list_ueberhang = get_sorted_ueberhang(["state"], parties[i])
        seats2dist = allocated_seats[i] - sum(list_ueberhang)
        print(parties[i])
        distributed_seats.append((parties[i]
            , max(distributeSeats(seats2dist, list_votes2, False, 100) , list_min_seats)
            )) # adding tuples
    
    return distributed_seats

# sum correct?
[(x[0], sum(x[1])) for x in final_seat_assignment()]
    
dfVotesPerStateAndParty = dfVotesPerStateAndParty.sort_values(by=["party", "state"])

# add seat distribution to data frame:
flat_seat_list = sum(list(map(lambda x: x[1], final_seat_assignment())), []) # flat seats list
dfVotesPerStateAndParty = dfVotesPerStateAndParty.assign(dist_seats=flat_seat_list) # assign flat list of dist seats
dfVotesPerStateAndParty.groupby(["party"]).sum() # check sum
