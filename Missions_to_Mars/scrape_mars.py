# Dependencies
import os
from bs4 import BeautifulSoup as bs
import requests
import time
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import json

def scrape():

    #-------------Scape Source 1 - NASA Mars News---------------------------------#
    # Set up Chrome Driver because the news articles here are generated dynamically
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    # Define the url for NASA Mars News and use the headless browser to visit it
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    # Get the html object
    html = browser.html

    # Parse the html object
    soup = bs(html, 'html.parser')

    # Get all the relevant elements for news
    results = soup.find_all('div', class_='list_text')

    # Declare an empty list to be returned
    posts = []

    # Loop through results and pull title and paragraph
    # Loop through returned results
    for result in results:
        # Error handling
        try:
            # Identify and return title of news post
            title = result.find('div', class_='content_title').text
            # Identify and return paragraph of news post
            paragraph = result.find('div', class_='article_teaser_body').text

            # Run only if title and paragraph are available
            if (title and paragraph):

                # Dictionary to be inserted as a MongoDB document
                post = {
                    "title": title,
                    "paragraph": paragraph,
                }
                posts.append(post)


        except Exception as e:
            print(e)


    #------------- Scape Source 2 - JPL Mars Space Images - Featured Image-------#
    url = 'https://spaceimages-mars.com/'
    browser.visit(url)

    # Get the html object
    html = browser.html

    # Parse the html object
    soup = bs(html, 'html.parser')

    # Find a tag where class is brand_title
    results = soup.find('div', class_='floating_text_area')

    # Get the url from the href attribute
    relimageurl = results.find('a', href=True)
    relimageurl['href']

    # Assign it to a variable and concatenate it with the main url of the site
    featured_image_url = url +relimageurl['href']

    #-------------- Scrape Source 3 - Mars Facts --------------------------------#
    url = 'https://galaxyfacts-mars.com/'

    # Use Pandas to get the table from the url. It is returned as a list so get the first instance to get the dataframe
    facts_list = pd.read_html(url)
    facts_df = facts_list[0]

    # Set the first row as column headers
    facts_df.columns = facts_df.iloc[0]
    facts_df = facts_df[1:]

    # Set the right column as index
    facts_df = facts_df.set_index('Mars - Earth Comparison')

    # Save it to a html string
    facts_html = facts_df.to_html(formatters = {'content': lambda k: k.replace('\n', '')},
   escape = False, classes=["table table-hover", "table-striped", "table-hover"])

    #--------------- Scrape Source 4 - Mars Hemispheres ------------------------#
    # Declare the list of urls to go after
    urllist = ['https://marshemispheres.com/cerberus.html',
                'https://marshemispheres.com/schiaparelli.html',
                'https://marshemispheres.com/syrtis.html',
                'https://marshemispheres.com/valles.html']

    # Declare an empty list to hold the final scrap
    image_list = []

    def getImageInfo(url):
        # Declare an empty dict to be populated and returned
        dict = {}
        # Retrieve page with the requests module
        response = requests.get(url)
        
        # Create bs object; parse with 'html.parser'
        soup = bs(response.text, 'html.parser')
        
        # Find the title and relative url of the image
        imageinfo = soup.find('div', class_='cover')
        title = imageinfo.find('h2', class_='title').text
        relimageurl = imageinfo.find('a', href=True)
        imageurl = url + relimageurl['href']
        
        # Populate the dictionary with the retrieved info
        dict = {"title": title, "img_url": imageurl}
        return dict

    # Invoke the new method on a loop through the list of urls and add the 
    # data to the list to be returned
    for url in urllist:
        image_list.append(getImageInfo(url))
    image_list

    # Close the browser
    browser.quit()

    #---------------------- FINAL STEP: put together the result dictionary-----#
    scrape_results = {"news_articles": posts,
                        "featured_image": featured_image_url,
                        "facts": facts_html,
                        "hemispheres": image_list}
    dict = json.dumps(scrape_results)
    return dict

#-------- Use to check correctly formatted json
# dict = json.dumps(scrape())
# print(dict)