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

sites = [('https://www.studio-orta.com', 'https://www.studio-orta.com/en/'),
         ('https://www.gemeentemuseum.nl', 'https://www.gemeentemuseum.nl/en/'),
         ('https://www.hkw.de', 'https://www.hkw.de/en/'),
         ('http://www.deutsches-museum.de/', 'http://www.deutsches-museum.de/en/')]

#site_root = 'https://www.studio-orta.com'
#first_page = 'https://www.studio-orta.com/en/'
#site_root = 'https://www.anthropocene-curriculum.org'
#first_page = 'https://www.anthropocene-curriculum.org/'
#site_root = 'https://www.gemeentemuseum.nl'
#first_page = 'https://www.gemeentemuseum.nl/en/'
#site_root = 'https://www.hkw.de'
#first_page = 'https://www.hkw.de/en/'
#site_root = 'http://www.deutsches-museum.de'
#first_page = 'http://www.deutsches-museum.de/en/'

deepness = 6
visited_list = []
to_visit = []
english_pages = []

def count_on_this_page(driver, page, f):
    driver.get(page)
    global words
    #pagina = driver.page_source.lower()
    # body_visible = driver.find_element_by_tag_name("body").get_attribute("text")
    body_visible = driver.find_element_by_xpath("/html/body").text.lower()
    #print(pagina)
    print("Result on page ->" + page + "<- ", file=f)
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
        try:
            sidebar = driver.find_element_by_xpath('//*[@id="teaser-container-desktop"]/div').text.lower()
            print(sidebar)
            insidebar = count(sidebar, word)
            print(insidebar)
        except selenium.common.exceptions.NoSuchElementException:
            insidebar = 0
        if ("page not found" in body_visible):
            result = 0
        else:
            result = total - (infooter + insidebar)
        print("(" + word + "): " + str(result), end='\t', file=f)
        dict[word] = dict[word] + result
    print("", file=f)

def find_between( s, start, first, last ):
    try:
        start = s.index( first, start ) + len( first )
        end = s.index( last, start )
        return ( s[start:end], end)
    except ValueError:
        return ""

def is_english_content(page_content):
    return ('lang="en"' in str(page_content)[:50])

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title', 'footer', 'img']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    return True

def count(raw_text, word):
    tokens = " ".join("".join([" " if ch in string.punctuation else ch for ch in raw_text]).split()).split()
    return tokens.count(word)

def search_neighbourgs(url_page, site_root, f):
    global to_visit
    global visited_list
    global english_pages
    link_list = []
    #if not ("/en" in url_page) and not (is_english_content(pagina)) :
    if not ("/en/" in url_page):
        print("Not english, to destroy -> " + url_page, file=f)
        return []
    pagina = get_page(url_page)
    english_pages += [url_page]
    soup = BeautifulSoup(pagina, "html5lib")
    for link in soup.find_all('a'):
        current_link = link.get('href')
        if (is_to_be_visited(current_link)):
            if (current_link[0] == "/"):
                to_visit += [site_root + current_link]
                link_list += [site_root + current_link]
            else:
                to_visit += [site_root + current_link]
                link_list += [site_root + current_link]
            #print(current_link, file=f)
    return set(link_list)

def is_to_be_visited(link):
    global visited_list
    global to_visit
    if (link != None) and ("http" not in link) and ("/#" not in link) and \
        ("?" not in link) and ("=" not in link) and (":" not in link) and ("/.." not in link) and \
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

def visit(page, site_root, level, f):
    global visited_list
    global to_visit

    #VISIT / GET NEIGH
    print("Visiting (" + str(level) + "): searching neigh ->" + page, file=f)
    neighbourgs = search_neighbourgs(page, site_root, f)
    visited_list += [page]
    if (page in to_visit):
        to_visit.remove(page)

    #CECHK IF STOP
    if (level == 0):
        #print("Last level, stop")
        return

    level = level - 1

    # PROPAGATE
    for n in neighbourgs:
        #print(str(level) + " level) propagating visit to neigh: " + n )
        if n not in visited_list:
            visit(n, site_root, level, f)
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


def spider(site_root, first_page, f):
    global to_visit
    global deepness

    prefs = {"profile.default_content_setting_values.notifications": 2,
             "profile.managed_default_content_settings.images": 2}  # before 1
    # SET OPTIONS TO NOT SHOW NOTIFICATION FROM FB PAGE
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("prefs", prefs)

    #driver.get(first_page)
    print("################################### Urllib  & BeautifulSoup4 & Selenium ", file=f)
    visit(first_page, site_root, deepness, f)
    print("################################### VISITED PAGES", file=f)
    print(sorted(set(visited_list)), file=f)
    print("################################### ENGLISH PAGES", file=f)
    print(sorted(set(english_pages)), file=f)

    # OPEN CHROME-DRIVER
    driver = webdriver.Chrome('chromedriver.exe', chrome_options=chrome_options)
    driver.set_window_size(1200, 500)
    driver.set_window_position(0, 0)
    #maxi_total = 0
    for p in english_pages:
        count_on_this_page(driver, p, f)
    print(dict, file=f)
    driver.quit()


def main():
    global deepness
    global visited_list
    global to_visit
    global english_pages

    for site in sites[2:]:

        visited_list = []
        to_visit = []
        english_pages = []

        site_root = site[0]
        first_page = site[1]
        domain_name = site_root.split(".")[1]
        with open(domain_name + "-" + str(deepness) + ".txt", "w") as f:
            # PRINT START TIME
            start = datetime.datetime.now()
            print(start.time(), file=f)

            # EXECUTE
            spider(site_root, first_page, f)

            # PRINT END TIME
            end = datetime.datetime.now()
            print(end.time(), file=f)
        f.close()

    return

main()