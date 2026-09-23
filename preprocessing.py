import pandas as pd
import numpy as np
import os

np.random.seed(42)

# Define input and output directory paths
ORIGIN_DIR = "./origin_data/"
NEW_DIR = "./new_data/"

# Automatically create the output directory if it does not exist
if not os.path.exists(NEW_DIR):
    os.makedirs(NEW_DIR)

# 1. PROCESS GAMES TABLE
print("Processing games table...")
df_games = pd.read_csv(ORIGIN_DIR + "games.csv")

# Select core columns and rename them to match the SQL schema
df_games_cleaned = df_games[['BGGId', 'Name', 'YearPublished', 'MinPlayers', 'MaxPlayers', 'MfgPlaytime', 'MfgAgeRec', 'GameWeight', 'AvgRating', 'NumUserRatings', 'ImagePath']]
df_games_cleaned = df_games_cleaned.rename(columns={
    'BGGId': 'game_id',
    'Name': 'name',
    'YearPublished': 'year_published',
    'MinPlayers': 'min_players',
    'MaxPlayers': 'max_players',
    'MfgPlaytime': 'play_time',
    'MfgAgeRec': 'min_age',
    'GameWeight': 'complexity_weight',
    'AvgRating': 'avg_rating',
    'NumUserRatings': 'total_votes',
    'ImagePath': 'image_url'
})


# Data Cleaning: Fix logical errors and handle missing values to match SQL constraints
df_games_cleaned.loc[df_games_cleaned['min_players'] < 1, 'min_players'] = 1
df_games_cleaned.loc[df_games_cleaned['max_players'] < df_games_cleaned['min_players'], 'max_players'] = df_games_cleaned['min_players']

df_games_cleaned.loc[df_games_cleaned['play_time'] == 0, 'play_time'] = None
df_games_cleaned.loc[df_games_cleaned['min_age'] == 0, 'min_age'] = None

df_games_cleaned.to_csv(NEW_DIR + "games_cleaned.csv", index=False)
print("Processed: games_cleaned.csv")

# 2. PROCESS MECHANICS & GAME_MECHANIC TABLES
print("Processing mechanics table...")
df_mech = pd.read_csv(ORIGIN_DIR + "mechanics.csv")
mechanic_names = df_mech.columns[1:]

# Create mechanics dictionary table
df_mechanics_cleaned = pd.DataFrame({
    'mechanic_id': range(1, len(mechanic_names) + 1),
    'mechanic_name': mechanic_names
})
df_mechanics_cleaned.to_csv(NEW_DIR + "mechanics_cleaned.csv", index=False)
print("Processed: mechanics_cleaned.csv")

# Create junction table: game_mechanic
df_mech_melt = df_mech.melt(id_vars='BGGId', var_name='mechanic', value_name='has_mechanic')
df_mech_melt = df_mech_melt[df_mech_melt['has_mechanic'] == 1].drop('has_mechanic', axis=1)
df_mech_merge = df_mech_melt.merge(df_mechanics_cleaned, left_on='mechanic', right_on='mechanic_name', how='left')
df_game_mechanic = df_mech_merge[['BGGId', 'mechanic_id']].rename(columns={'BGGId': 'game_id'})

df_game_mechanic.to_csv(NEW_DIR + "game_mechanic.csv", index=False)
print("Processed: game_mechanic.csv")

# 3. PROCESS THEMES & GAME_THEME TABLES
print("Processing themes table...")
df_themes = pd.read_csv(ORIGIN_DIR + "themes.csv")
theme_names = df_themes.columns[1:]

# Create themes dictionary table
df_themes_cleaned = pd.DataFrame({
    'theme_id': range(1, len(theme_names) + 1),
    'theme_name': theme_names
})
df_themes_cleaned.to_csv(NEW_DIR + "themes_cleaned.csv", index=False)
print("Processed: themes_cleaned.csv")

# Create junction table: game_theme
df_themes_melt = df_themes.melt(id_vars='BGGId', var_name='theme', value_name='has_theme')
df_themes_melt = df_themes_melt[df_themes_melt['has_theme'] == 1].drop('has_theme', axis=1)
df_themes_merge = df_themes_melt.merge(df_themes_cleaned, left_on='theme', right_on='theme_name', how='left')
df_game_theme = df_themes_merge[['BGGId', 'theme_id']].rename(columns={'BGGId': 'game_id'})

df_game_theme.to_csv(NEW_DIR + "game_theme.csv", index=False)
print("Processed: game_theme.csv")

# 4. PROCESS USERS & REVIEWS TABLES 
# (Data optimization & new attribute generation)
print("Reading user_ratings.csv (This may take a few moments)...")
df_ratings = pd.read_csv(ORIGIN_DIR + "user_ratings.csv")

# Stratified Sampling: Shuffle data and limit to a maximum of 30 reviews per game
print("Applying stratified sampling to optimize performance...")
df_ratings = df_ratings.sample(frac=1, random_state=42)
df_ratings = df_ratings.groupby('BGGId').head(30).reset_index(drop=True)

# 4A. CREATE USERS TABLE
print("Processing users table...")
unique_users = df_ratings['Username'].dropna().unique()
df_users_cleaned = pd.DataFrame({
    'user_id': range(1, len(unique_users) + 1),
    'username': unique_users
})

# Generate mock data for the users table
countries = ['Vietnam', 'USA', 'UK', 'Germany', 'France', 'Japan', 'Canada', 'Australia', 'Brazil', 'Korea']
df_users_cleaned['country'] = np.random.choice(countries, len(df_users_cleaned))
df_users_cleaned['created_at'] = pd.to_datetime('2018-01-01') + pd.to_timedelta(np.random.randint(0, 1800, len(df_users_cleaned)), unit='D')
df_users_cleaned['created_at'] = df_users_cleaned['created_at'].dt.date

df_users_cleaned.to_csv(NEW_DIR + "users_cleaned.csv", index=False)
print("Processed: users_cleaned.csv")

# 4B. CREATE REVIEWS TABLE
print("Processing reviews table...")
df_reviews = df_ratings.merge(df_users_cleaned, left_on='Username', right_on='username', how='left')

# Rename columns to match the SQL schema
df_reviews_final = df_reviews[['BGGId', 'user_id', 'Rating']].copy()
df_reviews_final = df_reviews_final.rename(columns={
    'BGGId': 'game_id',
    'Rating': 'rating'
})

# Clean data: Remove nulls and duplicates to prevent SQL constraint violations
df_reviews_final = df_reviews_final.dropna(subset=['user_id'])
df_reviews_final['user_id'] = df_reviews_final['user_id'].astype(int)
df_reviews_final = df_reviews_final.drop_duplicates(subset=['game_id', 'user_id'], keep='last')

# Generate mock data for the reviews table
df_reviews_final['review_date'] = pd.to_datetime('2023-01-01') + pd.to_timedelta(np.random.randint(0, 1000, len(df_reviews_final)), unit='D')
df_reviews_final['review_date'] = df_reviews_final['review_date'].dt.date
    
comments = ['Great game!', 'Boring gameplay.', 'Highly recommended', 'Rules are too complex', 'Love the mechanics', 'Not my type', None, None, None, None]
df_reviews_final['comment'] = np.random.choice(comments, len(df_reviews_final))

# Export the final cleaned reviews table
df_reviews_final.to_csv(NEW_DIR + "reviews_cleaned.csv", index=False)
print("Processed: reviews_cleaned.csv")

print("\nETL data preprocessing completed successfully!")