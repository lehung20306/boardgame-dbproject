import pandas as pd

# Define input and output directory paths
ORIGIN_DIR = "./origin_data/"
NEW_DIR = "./new_data/"

# 1. PROCESS GAMES TABLE
df_games = pd.read_csv(ORIGIN_DIR + "games.csv")

# Select core columns and rename them
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

df_games_cleaned.to_csv(NEW_DIR + "games_cleaned.csv", index=False)
print("Processed: games_cleaned.csv")

# 2. PROCESS MECHANICS & GAME_MECHANIC TABLES
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
df_ratings = pd.read_csv(ORIGIN_DIR + "user_ratings.csv")

# Extract unique users from the 'Username' column to create the users table
unique_users = df_ratings['Username'].dropna().unique()
df_users_cleaned = pd.DataFrame({
    'user_id': range(1, len(unique_users) + 1),
    'username': unique_users
})
df_users_cleaned.to_csv(NEW_DIR + "users_cleaned.csv", index=False)
print("Processed: users_cleaned.csv")

df_reviews = df_ratings.merge(df_users_cleaned, left_on='Username', right_on='username', how='left')

# Keep only necessary columns: BGGId, user_id, Rating 
df_reviews_final = df_reviews[['BGGId', 'user_id', 'Rating']]
df_reviews_final = df_reviews_final.rename(columns={
    'BGGId': 'game_id',
    'Rating': 'rating'
})

df_reviews_final = df_reviews_final.dropna(subset=['user_id'])
df_reviews_final['user_id'] = df_reviews_final['user_id'].astype(int)
df_reviews_final = df_reviews_final.drop_duplicates(subset=['game_id', 'user_id'], keep='last')

df_reviews_final.to_csv(NEW_DIR + "reviews.csv", index=False)
print("Processed: reviews.csv")