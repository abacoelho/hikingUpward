## pull additional hike data 

import pandas as pd 
import requests 
from bs4 import BeautifulSoup
import csv
import json 
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import time
import argparse

hike_page_url = 'https://www.hikingupward.com/maps/'

def pull_webpage(hike_page_url):

	options = FirefoxOptions()
	options.add_argument("--headless")

	driver = webdriver.Firefox(options = options)
	driver.get(hike_page_url)
	time.sleep(5)
	htmlSource = driver.page_source
	return htmlSource

def clean_stats(cell):
    try:
        split = re.split(r': ', cell)
        return split[1]
    except:
        return 'NA'

def parse_data_table(htmlSource):
    soup = BeautifulSoup(htmlSource)
    table = soup.find('div', id  = 'hikes-list')
    rows = table.find_all('tr')
    cells = [row.find_all('td') for row in rows]
    data = []
    for cell in cells:
        name = cell[0].text.strip()
        url = cell[0].find('a', href = re.compile('www')).attrs['href']
        length = cell[1].text.strip()
        diff = cell[2].img.attrs['title']
        streams = cell[3].img.attrs['title']
        views = cell[3].img.attrs['title']
        sol = cell[4].img.attrs['title']
        try: 
            camp = cell[5].img.attrs['title']
        except:
            camp = 'NA'
        
        content = [name, url, length, diff, streams, views, sol, camp]
        data.append(content)      
    
    df = pd.DataFrame(data, columns = ['name', 'url', 'length', 'difficulty', 'streams', 'views', 'solitude', 'camping'])
    df['difficulty'] = df['difficulty'].apply(clean_stats)
    df['streams'] = df['streams'].apply(clean_stats)
    df['views'] = df['views'].apply(clean_stats)
    df['solitude'] = df['solitude'].apply(clean_stats)
    df['camping'] = df['camping'].apply(clean_stats)
    return df

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description = "Scrape hikes' metadata")   

	parser.add_argument('outPickle', help = 'path to pickle file to save hikes metadata')
	args = parser.parse_args()

	htmlSource = pull_webpage(hike_page_url)
	df = parse_data_table(htmlSource)
	print(df)

	df.to_pickle(args.outPickle)