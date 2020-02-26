# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 19:18:26 2019

@author: abcoelho
"""
import pandas as pd
from datetime import datetime
import requests
import bs4
import re

#This script scrapes reviews from Hiking Upward

'''
input: url to hike summary page 
output: df containing commenter, description, and hike date
The function has been customized for the page's html patterns.
'''
def scrape_reviews(url):
    #read the page's html
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.content, 'lxml')        
    
    #parse the hike name and review table out with ratings
    hike = soup.find(name='title')
    table = soup.find(name='table', attrs={'cellpadding':'3'})
    ratings = list(map(lambda x: x['src'][15:16], table.find_all('img')))
    df = pd.read_html(str(table))[0].drop([1, 2], axis = 1).dropna(how = 'all')
    df = pd.DataFrame({'commenter':df[0].iloc[::2], 
                       'description':df[0].iloc[1::2].values,
                       'hikeDate':df[3].iloc[::2], 
                       'rating':ratings})
    
    #cleaning
    df['hike'] = str(hike).split('<')[1].split('>')[1]
    df.commenter = df.commenter.apply(lambda x: x.replace('By:  ', ''))
    df.hikeDate = df.hikeDate.apply(lambda x: x.replace('Date of Hike: ', ''))
    df['url'] = url
    return df

'''
input: url to page showing ONLY reviews
output: df containing commenter, description, and hike date
scrape_all_reviews is different from scrape_reviews which 
scrapes reviews from the hike summary page
'''
def scrape_all_reviews(url):
    #read the page
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.content, 'lxml')        
    
    #parse the hike name and review table
    hike = soup.find(name='title')
    table = soup.find(name='table', attrs={'cellpadding':'3'})
    ratings = list(map(lambda x: x['src'][15:16], table.find_all('img')))    
    df = pd.read_html(str(table))[0].drop([1], axis = 1).dropna(how = 'all')
    df = pd.DataFrame({'commenter':df[0].iloc[::2].values, 
                         'description':df[0].iloc[1::2].values,
                         'hikeDate':df[2].iloc[::2].values, 
                         'rating': ratings})
    
    #cleaning
    df['hike'] = str(hike).split('Reviews for the ')[1].split('<')[0]
    df.commenter = df.commenter.apply(lambda x: x.replace('By: ', ''))
    df.hikeDate = df.hikeDate.apply(lambda x: x.replace('Date of Hike: ', ''))
    df['url'] = url
    return df

'''
input: url to hike summary page
output: df containing commenter, description, and hike date
The function looks for the 'All Reviews' option in the summary
page. If the option is found, then the review page is parsed 
else the summary page is parsed for the comments. If the page 
is not found, then a mostly-empty df is returned for that url and 
hike.
'''
def scrape_hikes_comments(url):
    try:
        #read the page
        page = requests.get(url)
        soup = bs4.BeautifulSoup(page.content, 'lxml')
        
        #determine if there is a like to the 'All Reviews' 
        allReviews = soup.find_all('a', href=True)[-4]['href']
        
        if 'all_reviews' in allReviews:
            url = 'https://www.hikingupward.com' + allReviews
            return scrape_all_reviews(url)
        
        return scrape_reviews(url)
    except:
        df = pd.DataFrame(columns = ['hike', 'url', 'commenter', 'hikeDate', 'description'])
        hike = url.split('/')[-2]
        hike = re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', hike)
        df.hike = hike    
        df.url = url
        return df

'''
input: dataframe with a 'hikeDate' column
output: df with a clean date column
Standardizes the date column to datetime.
'''
def clean_df(df):
    df.hikeDate = df.hikeDate.apply(lambda x: datetime.strptime(x, '%A, %B %d, %Y'))
    return df

'''
output: df of all the reviews on Hiking Upward
The resulting dataframe contains the hike name, url, 
comment, hike date, rating, and description.
'''   
def scrape_HU_reviews():
    #read the page containing the list of all hikes
    url = 'https://www.hikingupward.com/maps/'
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.content, 'lxml')
    
    #parse the hikes' urls
    hikesURL = list(map(lambda x: x.split('"')[3],str(soup).split('new hike')[2:-1]))

    #prepare an empty dataframe
    df = pd.DataFrame(columns = ['hike', 'url', 'commenter', 'hikeDate', 
                                 'rating', 'description'])
    
    #scrape comments from all the hike webpages
    for url in hikesURL:
        df = df.append(scrape_hikes_comments(url))
    df = df.reset_index(drop = True)
    
    #clean up a bit
    df = clean_df(df)
    
    return df


df = scrape_HU_reviews()
df.to_pickle("HU_reviews.pkl")


###Testing
summaryTest = 'https://www.hikingupward.com/NCSP/PilotMountain/'
t1 = scrape_reviews(summaryTest)

allReviewsTest = 'https://www.hikingupward.com/all_reviews.asp?HN=Billy%20Goat%20Trail&RID=135&URL=/OMH/BillyGoatTrail/index.asp'
t2 = scrape_all_reviews(allReviewsTest)
#NOTE: commenter column can contain metadata 

###Future updates
#adding pauses in the scraping to not get booted off the website
#additional cleaning to the data
#scraping images?