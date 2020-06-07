# -*- coding: utf-8 -*-
"""
Created on Sun May 10 10:45:34 2020

@author: abcoelho
"""

import pandas as pd
import argparse
  
if __name__ == "__main__":
    # Prepare the script's arguments
    parser = argparse.ArgumentParser(description = 'Print hikes where "swim" is mentioned.')
    
    parser.add_argument('inPickle', help = 'Pickle file to use with a "description" and a \
                        "hike" column')
    parser.add_argument('searchTerm', help = 'term to search for within comments and then ',
                        default = 'swim', type = str)
    parser.add_argument('--resultExcel', help = 'Path for a new excel file with the hike names and \
                        the number of times the search term is mentioned in their comments')
    
    args = parser.parse_args()
    
    # Read the infile
    df = pd.read_pickle(args.inPickle)
    
    # Determine if "swim" is in the description
    df[args.searchTerm] = df['description'].apply(lambda x: args.searchTerm in x.lower())
    
    # Group by the names and count the number of "swim" descriptions
    dfG = df.groupby(args.groupCol)[args.searchTerm].sum().reset_index()
    
    # Only take rows that have at least one swim
    dfG = dfG[dfG[args.searchTerm] != 0]
    
    # Sort by the swim column
    dfG = dfG.sort_values(args.searchTerm, ascending = False).reset_index(drop = True)
    
    # Print the top 10
    print('\n\nTop ten hikes with most comments mentioning "swim:"\n')
    print(dfG[:10])
    
    
    # If told to return, return to the specified path
    if args.resultExcel:
        dfG.to_excel(args.resultExcel, index = False)