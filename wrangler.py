import os
import pandas as pd


def music_play_data(file_path):
    chunks = pd.read_csv(file_path, chunksize=10000)  # O(n)
    dest_file_path = music_total_day_plays(file_path, chunks) # O(n)2
    return dest_file_path


def music_total_day_plays(file_path, chunks):
    temp_dfs = []
    for chunk_df in chunks: # O(n)2
        result = chunk_df.groupby(['Song', 'Date'], sort=False).sum()  
        temp_dfs.append(result)
    # compute sum on processed dataframes
    df = pd.concat(temp_dfs).groupby(['Song', 'Date'], sort=False).sum()
    df.columns = df.columns.str.replace(" ", "") # remove spaces from column names
    df.rename(columns={"NumberofPlays": "Total Number of Plays for Date"}, inplace=True)
    dest_path = f"./downloads/processed_{os.path.basename(file_path)}"
    df.to_csv(dest_path)
    return dest_path

# Time complexity - 0(n)2

# This module utilises the pandas library a data analysis manipulation tool.
# The data in read in chunks of 10,000 rows. (Note more details needed)
# These chunks are the processed to get the Music number if plays for a Date. 
# This is done by grouping the date and song, and compute the sum of group values, and the resulting dataframe saved to a list
# Given the challenge of working with chunks, 
# there is a compute the sum across the chunks after combining their result of their summation.
# The resulting dataframe columns are renamed, to match the data representes and then written to a csv file for output.
