# import libraries
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import json

# specify the url
site_prefix = "file:///home/arndt/Documents/DSM/PythonDS/wahlbewerber_html/www.bundeswahlleiter.de/bundestagswahlen/2017/"

# TODO: use this shiiiiiit!!!!!!!!
### columns = soup.findAll('td', text = re.compile('your regex here'), attrs = {'class' : 'pos'})

def get_links(soup, link_substr):
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
    
def get_links_old(soup, link_substr):
    # get the relevant links
    relevant_links = [links for links in soup.find_all('a') if link_substr in links.get("href")]
    
    # remove duplicates by using a dict
    relevant_links = {x.get_text() : x["href"] for x in relevant_links}        
    
    # return a list of tuples (statename, url)
    return sorted([(k, v) for k, v in relevant_links.items()])
        
# TODO: could be improved by following the button "Ein Gebiet auswählen"
def get_state_urls():
    """
    returns a list of relative URLs for each state
    """
    # query the website and return the html to the variable "page"
    page = urlopen(site_prefix + "wahlbewerber.html")
    
    # parse the html using beautiful soup and store in variable "soup"
    soup = BeautifulSoup(page, "html.parser")
        
    return get_links(soup, "wahlbewerber/bund-99/")

# TODO: could be improved by selecting link below Button "Einen Wahlkreis auswählen"
def get_constituency_urls(state_url):
    """
    return a list of relative URLs of the constituencies of a specific state
    
    :param state_url: <str> the relative state URL
    """
    page = urlopen(site_prefix + state_url)
    soup = BeautifulSoup(page, "html.parser")

    # get url part after last slash but without .html ending
    # e.g. "land-10" from "wahlbewerber/bund-99/land-10.html"
    state = state_url.rsplit("/", 1)[-1][:-5]
        
    return get_links(soup, state + "/wahlkreis")
    
def get_all_constituency_urls():
    """
    returns a list of constituency URLs for every state
    
    :return: <list> a list of lists
    """
    state_urls = get_state_urls()
    constituency_links = []
    for s in state_urls:
        constituency_links.append(get_constituency_urls(s))
    # flatten list of lists
    #constituency_links = [link for sublist in constituency_links for link in sublist]
    return constituency_links

def get_direct_candidates_per_constituency(constituency_url):
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
    for state in get_all_constituency_urls():
        state_key = state[0].split("/")[-2][5:]
        result[state_key] = {}
        for constituency_url in state:
            consituency_key = constituency_url.split("/")[-1][10:-5]
            direct_candidates = convert_dom_table(get_direct_candidates_per_constituency(constituency_url))
            result[state_key][consituency_key] = direct_candidates
    return result

def get_party_candidates(state_url):
    """
    returns the party candidates in a specific state as a dictionary
    { part_name : candidates_table }
    """
    page = urlopen(site_prefix + state_url)
    soup = BeautifulSoup(page, "html.parser")    
    result= {}
    for article in soup.find_all("article"):
        if article.h1 is not None: 
            party_nm = article.h1.span.text
            table_data = convert_dom_table(article.table)
            result[party_nm] = table_data    
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

def get_all_party_candidates():
    result = {}
    for state_url in get_state_urls():
        state_id = get_state_id_from_url(state_url)
        candidates = get_party_candidates(state_url)
        result[state_id] = candidates
    return result


#%%

get_party_candidates('wahlbewerber/bund-99/land-5.html')
#json.dumps(get_all_candidates(), sort_keys=True, indent=4)

    
state_urls = get_state_urls()
state_urls 

constituency_urls = get_constituency_urls('wahlbewerber/bund-99/land-1.html')
constituency_urls

direct_candidates_1_1 = get_direct_candidates_per_constituency("land-1/wahlkreis-1.html")
direct_candidates_1_1

direct_candidates_1_1_py = convert_dom_table( direct_candidates_1_1 )
direct_candidates_1_1_py

all_direct_candidates = get_all_direct_candidates()

party_candidates_1 = get_party_candidates('wahlbewerber/bund-99/land-1.html')
all_party_candidates = get_all_party_candidates()

#%%

page = urlopen(site_prefix + "wahlbewerber.html")

# parse the html using beautiful soup and store in variable "soup"
soup = BeautifulSoup(page, "html.parser")

d = soup.find_all("div", attrs={"class" : "dropdown"})
print(d)
    
b = soup.find("button", text="Ein Gebiet auswählen")
print(b)
children = b.findChildren()
print(children)

