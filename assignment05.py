# change working directory
from os import chdir
chdir("/home/arndt/git-reps/wahlen")

# import libraries
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import json
import assignment04
from functools import lru_cache
import pandas


# specify the url
site_prefix = "file:///home/arndt/Documents/DSM/PythonDS/wahlbewerber_html/www.bundeswahlleiter.de/bundestagswahlen/2017/"

def scrape_links(soup, link_substr):
    """
    from the soup return a list of links containg a specific sub-string
    
    :param soup: <BeautifulSoup> the soup to be searched
    :param link_substr: <str> the substring that is to be part of the links
    :return <list> an alphabetically sorted list of links
    """
    # get the relevant links
    relevant_links = [links["href"] for links in soup.find_all('a') if link_substr in links["href"]]
    
    # remove duplicates and sort
    return sorted(list(set(relevant_links)))
        
def scrape_state_urls():
    """
    returns a list of relative URLs for each state
    """
    # query the website and return the html to the variable "page"
    page = urlopen(site_prefix + "wahlbewerber.html")
    
    # parse the html using beautiful soup and store in variable "soup"
    soup = BeautifulSoup(page, "html.parser")
        
    return scrape_links(soup, "wahlbewerber/bund-99/")

def scrape_constituency_urls(state_url):
    """
    return a list of relative URLs of the constituencies of a specific state
    
    :param state_url: <str> the relative state URL
    """
    page = urlopen(site_prefix + state_url)
    soup = BeautifulSoup(page, "html.parser")

    # get url part after last slash but without .html ending
    # e.g. "land-10" from "wahlbewerber/bund-99/land-10.html"
    state = state_url.rsplit("/", 1)[-1][:-5]
        
    return scrape_links(soup, state + "/wahlkreis")
    
def scrape_all_constituency_urls():
    """
    returns a list of lists of constituency URLs for every state
    
    :return: <list> a list of lists
    """
    state_urls = scrape_state_urls()
    constituency_links = []
    for s in state_urls:
        constituency_links.append(scrape_constituency_urls(s))
    return constituency_links

def scrape_direct_candidates(constituency_url):
    """
    returns the DOM table of direct candidates from the constituency as a list of lists
    """
    page = urlopen(site_prefix + "wahlbewerber/bund-99/" + constituency_url)
    soup = BeautifulSoup(page, "html.parser")
    dom_table = soup.find_all("table").pop()
    
    return dom_table

def convert_dom_table(dom_table):
    """
    converts the DOM table parameter into a Python list of lists
    """
    body = dom_table.tbody
    rows = body.find_all("tr")
    result_list = []
    for r in rows: 
        header = r.find_all("th")
        columns = r.find_all("td")
        rowdata = []
        rowdata.extend([header[0].text.strip()])
        rowdata.extend([c.text.strip() for c in columns])
        result_list.append(rowdata)
    return result_list

@lru_cache(maxsize=32)
def get_all_direct_candidates():
    """
    Returns a dictionary of states containing a dictionary of constituencies 
    whose values are tables in the form of a list of lists.
    
    Structure:    
    { state_id : 
        { constituency_id : 
            [["Party", "Name", "Job", "Birth Year", "optional: Also runs for Seat in State"],
             ["Party", "Name", "Job", "Birth Year", ""]
            ]
        }
    }
    """    
    result = {}
    for state in scrape_all_constituency_urls():
        state_key = int(state[0].split("/")[-2][5:])
        result[state_key] = {}
        for constituency_url in state:
            consituency_key = int(constituency_url.split("/")[-1][10:-5])
            direct_candidates = convert_dom_table(scrape_direct_candidates(constituency_url))
            result[state_key][consituency_key] = direct_candidates
    return result

def scrape_party_candidates(state_url):
    """
    returns the party candidates in a specific state as a dictionary
    { party_name : candidates_table }
    """
    page = urlopen(site_prefix + state_url)
    soup = BeautifulSoup(page, "html.parser")    
    result= {}
    for article in soup.find_all("article"):
        if article.h1 is not None: 
            party_nm = assignment04.clean_name(article.h1.span.text)
            table_data = convert_dom_table(article.table)
            result[party_nm] = table_data    
    return result

@lru_cache(maxsize=32)
def scrape_all_party_candidates():
    """
    returns the candidates of every party in every state
    """
    result = {}
    for state_url in scrape_state_urls():
        state_id = get_state_id_from_url(state_url)
        candidates = scrape_party_candidates(state_url)
        result[state_id] = candidates
    return result

def get_state_id_from_url(url):
    """
    Retuns the state id from the given URL.
    
    e.g. 15 from "land-15/wahlkreis-70.html"
    or 1 from "bund-99/land-1.html"
    
    :return: <int> the state id
    """
    url = url.replace(".html","")
    for part in url.split("/"):
        if "land-" in part:
            return int(part[5:])
    raise ValueError("The given URL does NOT contain a state part")

def get_direct_candidates_names(state, party):
    """
    returns a list of all direct candidates of the specified state and party.
    
    :param state: <int> state key
    :param party: <str> party name
    """
    dcs = get_all_direct_candidates()[state]    
    return [c[1] for constituency, candidates in dcs.items() for c in candidates if c[0]==party]

def get_party_candidate_names(state, party):
    """
    returns a list of all candidates of the specified state and party.
    
    :param state: <int> state key
    :param party: <str> party name
    """
    pcs = scrape_all_party_candidates()[state]
    return [c[1] for c in pcs[party]]
    
def get_seat_distribution():
    """
    returns the seats distribution as a list of lists 
    containing the columns [state, party, distributed_seats]
    """
    seat_distribution = assignment04.get_final_distribution()
    seat_distribution.sort_values(["state","party"])
    seat_distribution = seat_distribution[["state","party","dist_seats"]].values.tolist()
    return seat_distribution

def get_direct_seats():
    """
    returns the direct seats as a list of lists 
    containing the columns [state, constituency, party]
    """
    direct_seats = assignment04.get_direct_mandates()
    direct_seats.sort_values(["state","party"])
    direct_seats = direct_seats[["state","constituency","party"]].values.tolist()
    return direct_seats

def has_won_direct_seat(state, constituency, party):
    """
    returns True if the given party has won the direct seat in the given constituency/state,
    otherwise False
    """
    return [state, constituency, party] in get_direct_seats()

def get_winning_direct_candidate_names(state, party):
    """
    returns a list of the names of all candidates who have won a direct seat 
    for the given party in the given state
    """
    dcs = get_all_direct_candidates()[state]
    result = []
    for constituency, candidates in dcs.items():
        for c in candidates:
            if c[0] == party:
                if has_won_direct_seat(state, constituency, party):
                    result.append(c[1])
    return result

def assign_candidates():
    """
    Returns a tree structure mapping states to parties and candidate names.
    
    { state :
        { party :
            [ candidate_names ]
        }
    }
    """
    seat_distribution = get_seat_distribution()
    result = {}
    for t in seat_distribution:
        state=t[0]; party=t[1]; seats=t[2]
        
        # first the direct candidates get a seat
        dcs = get_winning_direct_candidate_names(state, party)
        
        # party canidates which have not won a direct seats
        rest = [c for c in get_party_candidate_names(state, party) if c not in dcs]
        
        # only the top n get a seat
        rest_seats = int(seats-len(dcs))
        if rest_seats>0: rest = rest[:rest_seats]
        else: rest = []

        # add concatenated lists to the result
        if not state in result: result[state] = {party : dcs + rest}
        else: result[state][party] = dcs + rest
        
    return result

def print_assignment():
    """
    Produce an output list of the form
    state;party;candidatename
    """
    assigned_candidates = [(state, party, candidate) for state, v in assign_candidates().items() for party, candidates in v.items() for candidate in candidates]
    for state, party, candidate in assigned_candidates:
        print(f"{state};{party};{candidate}")

print_assignment()

#%%

state_urls = scrape_state_urls()
state_urls 

constituency_urls_1 = scrape_constituency_urls('wahlbewerber/bund-99/land-1.html')
constituency_urls_1

direct_candidates_1_1 = scrape_direct_candidates("land-1/wahlkreis-1.html")
direct_candidates_1_1

direct_candidates_1_1_lol = convert_dom_table( direct_candidates_1_1 )
direct_candidates_1_1_lol

all_direct_candidates = get_all_direct_candidates()

party_candidates_1 = scrape_party_candidates('wahlbewerber/bund-99/land-1.html')
all_party_candidates = scrape_all_party_candidates()

len(get_direct_candidates_names(1,"CDU"))
len(get_winning_direct_candidate_names(1,"CDU"))

len(get_direct_candidates_names(1,"SPD"))
len(get_winning_direct_candidate_names(1,"SPD"))

get_party_candidate_names(1,"CDU")
get_party_candidate_names(1,"CDU")[:2]

assigned_candidates = assign_candidates()
assigned_candidates_agg = [(state, party, len(candidates)) for state, v in assigned_candidates.items() for party, candidates in v.items()]        
sorted(assigned_candidates_agg, key=lambda x: [x[1], x[0]])
df=pandas.DataFrame(assigned_candidates_agg, columns=["state","party","seats"])
df.groupby("party").sum()
