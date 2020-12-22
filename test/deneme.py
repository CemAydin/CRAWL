# This script is used to crawl a site, and store some information including the meta title, meta description, canonical, no of internal links and no of external links
# This script is used to crawl a site, and store some information including the meta title, meta description, canonical, no of internal links and no of external links
import sqlite3
import re
import requests
from bs4 import BeautifulSoup
import time

start = time.time()

# connect to database
db = sqlite3.connect('site_crawl.db')
cursor = db.cursor()


# get the URL to crawl
url = input("URL to crawl: ")
if len(url) < 1:
    url = "http://charlieojackson.co.uk"


def get_db_name(url):
    """Takes a URL and strips it to use as a table name"""
    if 'www' in url:
        url_clense = re.findall('ht.*://www\.(.*?)\.',url)
        url_clense = url_clense[0].capitalize()
        return url_clense
    else:
        url_clense = re.findall('ht.*://(.*?)\.',url)
        url_clense = url_clense[0].capitalize()
        return url_clense

db_name = get_db_name(url)

# Create database
cursor.execute("CREATE TABLE IF NOT EXISTS " + db_name + " (URLID INTEGER PRIMARY KEY AUTOINCREMENT,URL varchar(255),Title varchar(255),Description varchar(255),InternalLinks INTEGER,ExternalLinks INTEGER, PageContents TEXT, Canonical varchar(255), Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")

all_urls = []
all_urls.append(url)

def extract_content(soup):
    """Extract required data for crawled page"""
    title = soup.title.string
    try:
        description = soup.find("meta", {"name":"description"})['content']
    except:
        description = 'Null'

    try:
        canonical = soup.find('link', {'rel':'canonical'})['href']
    except:
        canonical = "Null"

    contents_dirty = soup.text
    contents = contents_dirty.replace("\n","")
    return (title, description, contents, canonical)


def extract_links(soup):
    """"Extract links and link counts from page"""
    links_dirty = soup.find_all('a')
    for link in links_dirty:
        if str(link.get('href')).startswith(url) == True and link.get('href') not in all_urls:
            if '.jpg' in link.get('href') or '.png' in link.get('href'):
                continue
            else:
                all_urls.append(link.get('href'))

    return (len(links_dirty))


def insert_data(extracted_data):
    """Insert the crawled data into the database"""
    url,title, description, contents, no_of_links, canonical = extracted_data
    #print(title,"\n", description,"\n", contents,"\n",no_of_links,"\n", deduped_links)
    cursor.execute("INSERT INTO " + db_name + " (URL, Title, Description, ExternalLinks, PageContents, Canonical) VALUES(?,?,?,?,?,?)",(url, title, description, no_of_links, contents, canonical,))
    db.commit()


link_counter = 0
while link_counter < len(all_urls):

    try:
        print(str(link_counter) + " crawling: " + all_urls[link_counter])
        r = requests.get(all_urls[link_counter])
        if r.status_code == 200:
            html = r.text
            soup = BeautifulSoup(html, "html.parser")
            no_of_links = extract_links(soup)
            title, description, contents, canonical = extract_content(soup)
            insert_data((all_urls[link_counter], title, description, contents, no_of_links,canonical))

        link_counter += 1

    except Exception as e:
        link_counter += 1
        print(str(e))


cursor.close()
db.close()
end = time.time()
print(end - start)