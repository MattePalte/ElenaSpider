from selenium import *
from selenium import webdriver
from time import sleep
import re
import selenium.common.exceptions
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import string
import datetime

words = ['anthropocene', 'tourism', 'tourist', 'environment',
         'environmental', 'art', 'museum', 'museums', 'sustainability',
         'sustainable', 'education', 'educational' , 'culture', 'cultural']

dict = {'anthropocene' : 0, 'tourism' : 0, 'tourist' : 0, 'environment' : 0,
         'environmental' : 0, 'art' : 0, 'museum' : 0, 'museums' : 0, 'sustainability' : 0,
         'sustainable' : 0, 'education' : 0, 'educational' : 0, 'culture' : 0, 'cultural' : 0}

site_root = 'http://www.deutsches-museum.de'
visited_list = []
to_visit = []
word = "museum "
english_pages = []

def count_on_this_page(driver, page):
    driver.get(page)
    global words
    #pagina = driver.page_source.lower()
    # body_visible = driver.find_element_by_tag_name("body").get_attribute("text")
    body_visible = driver.find_element_by_xpath("/html/body").text.lower()
    #print(pagina)
    for word in words:
        total = count(body_visible, word)
        #print(total)
        try:
            footer = driver.find_element_by_id("footer").text.lower()
            # print(footer)
            infooter = count(footer, word)
            #print(infooter)
        except selenium.common.exceptions.NoSuchElementException:
            infooter = 0
        result = total - infooter
        print("Result on page ->" + page + "<- (" + word + "): " + str(result))
        dict[word] = dict[word] + result

def find_between( s, start, first, last ):
    try:
        start = s.index( first, start ) + len( first )
        end = s.index( last, start )
        return ( s[start:end], end)
    except ValueError:
        return ""

def is_english_content(page_content):
    return ('lang="en"' in str(page_content))

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title', 'footer', 'img']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    return True

def count(raw_text, word):
    tokens = " ".join("".join([" " if ch in string.punctuation else ch for ch in raw_text]).split()).split()
    return tokens.count(word)

def search_neighbourgs(url_page):
    global to_visit
    global visited_list
    global english_pages
    pagina = get_page(url_page)
    link_list = []
    if not (is_english_content(pagina)):
        print("Not english, to destroy -> " + url_page)
        return []
    english_pages += [url_page]
    soup = BeautifulSoup(pagina, "html5lib")
    for link in soup.find_all('a'):
        current_link = link.get('href')
        if (is_to_be_visited(current_link)):
            to_visit += [site_root + "/" + current_link]
            #print(current_link)
            link_list += [site_root + "/" + current_link]
    return set(link_list)

def is_to_be_visited(link):
    global visited_list
    global to_visit
    if (link != None) and ("http" not in link) and ("/#" not in link) and \
        ("?" not in link) and ("=" not in link) and \
        link not in to_visit and link not in visited_list:
        if not (link.endswith(".css")) and \
                not (link.endswith(".ico")) and \
                not (link.endswith(".jpg")) and \
                not (link.endswith(".jpeg")) and \
                not (link.endswith(".png")) and \
                not (link.endswith(".pdf")) and \
                not (link.endswith("#")):
            return True
    return False

def visit(site_root, level):
    global visited_list
    global to_visit

    #VISIT / GET NEIGH
    print("Visiting (" + str(level) + "): searching neigh ->" + site_root)
    neighbourgs = search_neighbourgs(site_root)
    visited_list += [site_root]
    if (site_root in to_visit):
        to_visit.remove(site_root)

    #CECHK IF STOP
    if (level == 0):
        #print("Last level, stop")
        return

    level = level - 1

    # PROPAGATE
    for n in neighbourgs:
        #print(str(level) + " level) propagating visit to neigh: " + n )
        if n not in visited_list:
            visit(n, level)
        #else:
            #print("Already visited")
    return

def get_page(url, mode = 1, driver = None):
    if (mode == 1):
        try:
            f = urllib.request.urlopen(url)
        except urllib.error.HTTPError:
            return ""
        try:
            return f.read().decode('utf-8').lower()
        except UnicodeDecodeError:
            return f.read().lower()
        except:
            return ""
    if (mode == 2 and driver != None):
        driver.get(url)
        return driver.page_source.lower()


def main():
    global to_visit
    global word

    print("Searching word : " + str(word))
    first_page = 'http://www.deutsches-museum.de/en'
    prefs = {"profile.default_content_setting_values.notifications": 2,
             "profile.managed_default_content_settings.images": 2}  # before 1
    # SET OPTIONS TO NOT SHOW NOTIFICATION FROM FB PAGE
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("prefs", prefs)

    #driver.get(first_page)
    print("################################### Urllib  & BeautifulSoup4 & Selenium ")
    visit(first_page, 2)
    print("################################### VISITED PAGES")
    print(sorted(set(visited_list)))
    print("################################### ENGLISH PAGES")
    print(sorted(set(english_pages)))

    # OPEN CHROME-DRIVER
    driver = webdriver.Chrome('chromedriver.exe', chrome_options=chrome_options)
    driver.set_window_size(400, 500)
    driver.set_window_position(0, 0)
    #maxi_total = 0
    for p in english_pages:
        count_on_this_page(driver, p)
    print(dict)

# PRINT START TIME
start = datetime.datetime.now()
print(start.time())

# EXECUTE
main()

# PRINT END TIME
end = datetime.datetime.now()
print(end.time())

# PRINT DIFFERENCE
elapsed = end - start
#print("Minutes elapsed -> " + str(elapsed.min))