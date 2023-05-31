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
    df.to_csv(dest_path, chunksize=10000)
    return dest_path
