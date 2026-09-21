COPY games(game_id, name, year_published, min_players, max_players, play_time, min_age, complexity_weight, avg_rating, total_votes, image_url) 
FROM 'D:/Hung Le/Subject/Database lab/Project/new_data/games_cleaned.csv' DELIMITER ',' CSV HEADER;

COPY mechanics(mechanic_id, mechanic_name) 
FROM 'D:/Hung Le/Subject/Database lab/Project/new_data/mechanics_cleaned.csv' DELIMITER ',' CSV HEADER;

COPY themes(theme_id, theme_name) 
FROM 'D:/Hung Le/Subject/Database lab/Project/new_data/themes_cleaned.csv' DELIMITER ',' CSV HEADER;

COPY users(user_id, username) 
FROM 'D:/Hung Le/Subject/Database lab/Project/new_data/users_cleaned.csv' DELIMITER ',' CSV HEADER;

COPY game_mechanic(game_id, mechanic_id) 
FROM 'D:/Hung Le/Subject/Database lab/Project/new_data/game_mechanic.csv' DELIMITER ',' CSV HEADER;

COPY game_theme(game_id, theme_id) 
FROM 'D:/Hung Le/Subject/Database lab/Project/new_data/game_theme.csv' DELIMITER ',' CSV HEADER;

COPY reviews(game_id, user_id, rating) 
FROM 'D:/Hung Le/Subject/Database lab/Project/new_data/reviews.csv' DELIMITER ',' CSV HEADER;