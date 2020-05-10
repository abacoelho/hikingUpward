# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 19:18:26 2019

@author: abcoelho
"""
import pandas as pd
import numpy as np
from datetime import datetime
import requests
import bs4
import re
import argparse
from tqdm import tqdm

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
    
    #tag resulting comments with the hike name and url
    df['hike'] = str(hike).split('<')[1].split('>')[1]
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
    
    #tag resulting comments with the hike name and url
    df['hike'] = str(hike).split('Reviews for the ')[1].split('<')[0]
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
input: text that should be a date from HU
output: datetime object (or nan if not datetime)
Standardizes the date to datetime.
'''
def clean_date(text):
    try:
        return datetime.strptime(text, '%A, %B %d, %Y')
    except:
        return np.nan
        
'''
input: dataframe with a 'commenter' and 'hikeDate' column
output: df with the two columns standardized
Cleans and standardizes the HU dataframe
'''
def clean_df(df):
    df.commenter = df.commenter.apply(lambda x: str(x).replace('By:  ', ''))
    df.hikeDate = df.hikeDate.apply(lambda x: str(x).replace('Date of Hike: ', ''))    
    df.hikeDate = df.hikeDate.apply(clean_date)
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
    print('\nCompleted scraping all of the hike names on HU')
    
    #prepare an empty dataframe
    df = pd.DataFrame(columns = ['hike', 'url', 'commenter', 'hikeDate', 
                                 'rating', 'description'])
    
    #stage a progress bar to show a progress update
    print('Beginning to scrape the comments for each hike')
    
    #scrape comments from all the hike webpages
    for url in tqdm(hikesURL):
        df = df.append(scrape_hikes_comments(url))
    print('Completed scraping all the comments from all the hikes')
    df = df.reset_index(drop = True)
    
    #clean up a bit
    df = clean_df(df)
    
    return df


if __name__ == "__main__":
    #prepare the script's arguments
    parser = argparse.ArgumentParser(description = 'Scrape all hikes and their \
                                     comments from hiking upward.')   
    parser.add_argument('outPickle', help = 'path to pickle file to save hike \
                        comments and associated meta data')
    #TODO: add log file
    args = parser.parse_args()
    
    # Scrape all the reviews
    df = scrape_HU_reviews()
    
    # Save to specified pickle file
    df.to_pickle(args.outPickle)
    

###TODO
#commenter column can contain metadata 
#scraping images?