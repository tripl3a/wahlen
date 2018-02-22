# German Elections 2017

This repository was created during my first semester in the Master's program Data Science at the Beuth University of Applied Sciences, Berlin as part of the course Practice of Data Science Programming. The main goal of this course was to learn the basics of Python.

The example we worked on was the German Bundestag elections in 2017, where we reprogrammed the alogrithems used to calculate the distribution of seats in the German Bundestag. We also practiced web scraping.

## Computation of Mindestsitzzahl

For a given election result, each party in each state deserves a minimum number of seats (Mindestsitzzahl). Minimally, anybody obtaining the majority of first votes (Erststimmen) in each constituency is elected; this candidate has won a "direct seat" (Direktmandat). So number of seats for a party must be equal to or larger than the number of direct seats it won in a state.

In addition, each party gets a number of seats based on their portion of second votes (Zweitstimmen). The mandates for these seats come from per-state per-party candidate lists (Listenplätze, list seats). Again, the ultimate number of seats for a party in a state must be larger than this share. Thus, the minimum number of seats is the maximum of the direct seats and the number of list seats.

To compute the share of seat from second votes, the total amount of seats is distributed in two steps. In the first step, the seats are distributed by population count. In the second step, the seats are distributed to all eligible parties by second votes. A party is eligible if it has either 5% of the votes on the federal level, or three direct seats.

Note: In the 2017 election, no party became eligible only by receiving three direct seats; all parties which met this condition also received 5% of the second votes.

Note: Special consideration would be necessary if a candidate was elected for a direct seat who doesn't belong to a party, or whose party was not eligible for seats from the lists. This did not happen in the 2017 election, and thus does not need to be considered for the exercises.

## Assignment 1

Compute the percentage of Zweitstimmen for each political party in the 2017 Bundestagswahlen, using ergebnisse.csv as your data source.

Upload a Python script to this assignment that produces the results as a CSV output to the terminal, in the format

Party;Percentage

## Assignment 2

Write a Python script that displays a bar chart of the Zweitstimmen result of the elections. Use pyplot to draw the diagram.

The diagram should look similar to https://www.bundeswahlleiter.de/bundestagswahlen/2017/ergebnisse.html. You  should use color codes for the parties, and combine every party below 5% into Sonstige. You do not need to add bars for the last election. Displaying the numeric values at the top of the bar is optional.

## Assignment 3

For this and the next exercise, familiarize yourself with the procedure for seat distribution in the Bundestag. In particular, consider the material in this Moodle course:

* Method of Sainte-Laguë/Schepers

* Computation of Mindestsitzzahl

For this assignment, compute the Mindestsitzzahl for each party and each state. Upload your Python code to this course.

1. Implement the method of Saint-Lesque/Schepers in a reusable manner
1. For each constituency, compute the winning party of the direct seat (Direktmandat). For each state, compute the number of direct seats per party
1. Compute a distribution of 598 seats to the states, according to the population count in population.csv (source: bundeswahlleiter.de)
1. For each state, compute the assignment of seats to the parties according to the share of Zweitstimmen.
1. Print out a list of states (by name) and parties with number of direct seats and list seats, as well as the number of seats by  which the direct seats are larger than the list seats (Überhangmandate) (0 if the number is not larger). Produce a CSV output of the form

state;party;direct_seats;list_seats;ueberhang

## Assignment 4

Compute the number of elected candidates for each state and party.

This is an iterative process, finding the size of the parliament first. Starting with 598, increase the size of the parliament in increases of 1 until each party gets its Mindestsitzzahl (as an optimization, you could start with the sum of the Mindestsitzzahl instead).

In this process, only consider parties that got elected lists, i.e. at least 5% of the votes. Distribute the seats amont the parties using the Federal total of the Zweitstimmen, using the method of Sainte-Laguë/Schepers. The same divisor will be used for all parties, guaranteeing that each seat in the parliament will have the same number of voters behind it.

Then, distribute the seats for each party by states, distributed by Zweitstimmen for the party. Since each party needs to get at least the Direktmandate (by Erststimmen), the divisor needs to be different for each party, so that the party gets exactly the number of seats allocated in the previous step.

As an example (from the Bundeswahlleiter German documentation), the proper divisor for CDU will be 76 000. The distribution by Sainte-Lague will allocate only 5 seats to CDU in Thuringia. Since CDU won 8 seats in that state, they will get 8 seats regardless. So for each state, the allocated seats will be the maximum of the state's share, and the number of direct seats. These maximum values must add up to the number of seats for the party.

## Assignment 5

Compute the list of elected candidates, based on your results of assignment 4.

As an input, get the list of candidates (recursively) from https://www.bundeswahlleiter.de/bundestagswahlen/2017/wahlbewerber.html

You find the lists of party candidates e.g. in

https://www.bundeswahlleiter.de/bundestagswahlen/2017/wahlbewerber/bund-99/land-8.html

The party candidates are inside tr Elements that also contain a span with the id "party_runningnumber".

The direct candidates are e.g. in

https://www.bundeswahlleiter.de/bundestagswahlen/2017/wahlbewerber/bund-99/land-8/wahlkreis-258.html

Knowing the number of seats per party and state, the elected candidates are computed as follows:

Each direct candidate is elected and counts as a seat for the party in that state. The remaining seats for a party are given to the top of the party's list, skipping candidates that got already elected directly.

Produce an output list of the form

state;party;candidatename

## Assignment 6

Display a map of all consituencies, based on the data in

https://www.bundeswahlleiter.de/dam/jcr/f92e42fa-44f1-47e5-b775-924926b34268/btw17_geometrie_wahlkreise_geo_shp.zip

(from https://www.bundeswahlleiter.de/bundestagswahlen/2017/wahlkreiseinteilung/downloads.html)

Inside each constituency, place the name of the elected candidate in the center.
