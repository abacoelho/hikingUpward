# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 18:33:57 2019

@author: abcoelho
"""
import pandas as pd
import seaborn as sns
import numpy as np
#import nltk
#nltk.download()
from nltk.corpus import stopwords
stop = set(stopwords.words('english'))
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
from datetime import datetime, date

df = pd.read_pickle(r"C:\Users\abcoelho\Documents\Personal\Hiking Upward\comments.pkl")

'''
input: corpus (series), desired number of top words
output: top words from series and their count
The function removes stops words and then identifies 
and return the top words and their count.
'''
def top_n_words_count(corpus, n = 10):
    corpusClean = corpus.apply(lambda x: 
        [item for item in x.lower().split(' ') if item not in stop])
    corpusClean = corpusClean.apply(lambda x: ' '.join(x))
    top = pd.Series(' '.join(corpusClean).lower().split()).value_counts()[:n]
    return top.index.tolist()

'''
input: corpus (series), desired number of top words
output: top words
Instead of count, tf-idf if used to identify the words
that are deamed "most important" to the corpus.
'''
def top_n_words_tfidf(corpus, n = 10):
    vectorizer = TfidfVectorizer(min_df = 3)
    X = vectorizer.fit_transform(df.description)
    
    feature_array = np.array(vectorizer.get_feature_names())
    tfidf_sorting = np.argsort(X.toarray()).flatten()[::-1]  
    
    top = feature_array[tfidf_sorting][:n]
    return list(top)

'''
input: datetime day
output: datetime day with a standard year of 2000
'''
def scrub_year(day):
    Y = 2000
    if isinstance(day, datetime):
        day = day.date()
    day = day.replace(year=Y)
    return day

'''
input: datetime day
output: name of season for that day
'''
def get_season(day):
    Y = 2000 #ensures leap day is included
    seasons = [('winter', (date(Y,  1,  1),  date(Y,  3, 20))),
               ('spring', (date(Y,  3, 21),  date(Y,  6, 20))),
               ('summer', (date(Y,  6, 21),  date(Y,  9, 22))),
               ('autumn', (date(Y,  9, 23),  date(Y, 12, 20))),
               ('winter', (date(Y, 12, 21),  date(Y, 12, 31)))]
    
    if isinstance(day, datetime):
        day = day.date()
    day = day.replace(year=Y)
    season = next(season for season, (start, end) in seasons if start <= day <= end)    
    return season

print('Number of Reviews: ', df.shape[0])
print('Top words by count: ', top_n_words_count(df.description), '\n')
print('Top words by tf-idf: ', top_n_words_tfidf(df.description))

#viewing how many hikes have been reviewed over all time
time_series = pd.DataFrame(df['hikeDate'].value_counts().reset_index())[:-1]
time_series.columns = ['date', 'count']
time_series = time_series[time_series['date'] > datetime(2004, 1, 1)]
time = sns.lineplot(data=time_series, x='date', y='count')
time.set(xlabel='Date', ylabel='Number of Reviews', 
         title='Number of Reviews by Exact Date')
plt.show()

#ploting the number of reviews from each day of the year
dfTemp = df
dfTemp['hikeDate'] =  dfTemp['hikeDate'].apply(scrub_year)
dates = pd.DataFrame(dfTemp['hikeDate'].value_counts().reset_index())[:-1]
dates.columns = ['date', 'count']
dates = sns.lineplot(data=dates, x='date', y='count')
dates.set(xlabel='Day', ylabel='Number of Reviews', 
          xticklabels = ['Jan', 'Mar', 'May', 'Jul', 'Sept', 'Nov'],
          title='Numbe of Reviews by Day of Year')
plt.show()

#exploring what season has more reviews
df['season'] = df['hikeDate'].apply(get_season)
season = sns.countplot(x = "season", data = df, palette="deep")
season.set(xlabel='Season', ylabel='Number of Reviews', 
           title='Number of Reviews by Season')
plt.show()



###Next steps
#popular weekdays to post (posts typically on the weekend or days following)
#try to predict the season from the description, using Bert and LR