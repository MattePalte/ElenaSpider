from selenium import *
from selenium import webdriver
from time import sleep
import re
import selenium.common.exceptions


site_root = 'http://www.deutsches-museum.de'
visited_list = []


def count_on_this_page(driver, page, word):
    driver.get(page)
    #pagina = driver.page_source.lower()
    # body_visible = driver.find_element_by_tag_name("body").get_attribute("text")
    body_visible = driver.find_element_by_xpath("/html/body").text.lower()
    #print(pagina)
    total = body_visible.count(word)
    #print(total)
    try:
        footer = driver.find_element_by_id("footer").text.lower()
        # print(footer)
        infooter = footer.count(word)
        #print(infooter)
    except selenium.common.exceptions.NoSuchElementException:
        infooter = 0
    result = total - infooter
    print("Result on page ->" + page + "<- : " + str(result))
    return result

def find_between( s, start, first, last ):
    try:
        start = s.index( first, start ) + len( first )
        end = s.index( last, start )
        return ( s[start:end], end)
    except ValueError:
        return ""

def search_neibourgh(driver, current_site):
    global site_root
    pagina = driver.page_source.lower()
    print("searching neig of current site: " + current_site)
    start = 1
    end = 0
    i = 0
    max_link = 16
    first = 'href="'
    last = '"'
    link = "null"
    data_link = (link, 0)
    link_list = []
    while(data_link != ""):
        data_link = find_between(pagina, data_link[1], first, last)
        #print(data_link)
        if (data_link != "") and ("http" not in data_link[0]) and ("/#" not in data_link[0]):
            new_link = data_link[0]
            if not (new_link.endswith(".css")) and \
                not (new_link.endswith(".ico")) and \
                not (new_link.endswith(".jpg")) and \
                not (new_link.endswith(".jpeg")) and \
                not (new_link.endswith(".pdf")) and \
                not (new_link.endswith("#")):
                link_list += [site_root + "/" + data_link[0]]
    #print(set(link_list))
    return set(link_list)

def visit(driver, site_root, level):
    global visited_list
    # START VISIT
    driver.get(site_root)
    print("currently visiting: " + site_root)

    #VISIT / GET NEIGH
    print("searching/visiting neigh of : " + site_root)
    neighbourgs = search_neibourgh(driver, site_root)
    visited_list += [site_root]

    #CECHK IF STOP
    if (level == 0):
        print("last level, stop")
        return

    level = level - 1

    # PROPAGATE
    for n in neighbourgs:
        print(str(level) + " level) propagating visit to neigh: " + n )
        if n not in visited_list:
            visit(driver, n, level)
        else:
            print("Already visited")
    return

def rec_count(driver, site_root, word):
    result = count_on_this_page(driver, site_root, word)
    neighbourgs = search_neibourgh(driver, site_root)
    for n_page in neighbourgs:
        result += count_on_this_page(driver, n_page, word)
    return result

word = "museum "
print("Searching word : " + str(word))
frist_page = 'http://www.deutsches-museum.de/en'
prefs = {"profile.default_content_setting_values.notifications": 2,
         "profile.managed_default_content_settings.images": 2}  # before 1
# SET OPTIONS TO NOT SHOW NOTIFICATION FROM FB PAGE
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("prefs", prefs)

# OPEN CHROME-DRIVER
driver = webdriver.Chrome('chromedriver.exe', chrome_options=chrome_options)
driver.set_window_size(430,500)
driver.set_window_position(0,0)
visit(driver, frist_page, 2)
print(sorted(set(visited_list)))
maxi_total = 0
for v in visited_list:
    maxi_total += count_on_this_page(driver, v, word)
#maxi_total = rec_count(driver, site_root, word)
print("maxi_total: " + str(maxi_total))
sleep(10)
driver.quit()

