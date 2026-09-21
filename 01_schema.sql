CREATE TABLE games (
    game_id INT PRIMARY KEY,
    name VARCHAR(255),
    year_published SMALLINT,
    min_players SMALLINT,
    max_players SMALLINT,
    play_time INT,
    min_age SMALLINT,
    complexity_weight NUMERIC(4,2),
    avg_rating NUMERIC(4,2),
    total_votes INT,
    image_url TEXT
);

CREATE TABLE mechanics (
    mechanic_id INT PRIMARY KEY,
    mechanic_name VARCHAR(255)
);

CREATE TABLE themes (
    theme_id INT PRIMARY KEY,
    theme_name VARCHAR(255)
);

CREATE TABLE users (
    user_id INT PRIMARY KEY,
    username VARCHAR(255)
);

CREATE TABLE game_mechanic (
    game_id INT,
    mechanic_id INT,
    PRIMARY KEY (game_id, mechanic_id),
    CONSTRAINT fk_gm_game FOREIGN KEY (game_id) REFERENCES games(game_id),
    CONSTRAINT fk_gm_mechanic FOREIGN KEY (mechanic_id) REFERENCES mechanics(mechanic_id)
);

CREATE TABLE game_theme (
    game_id INT,
    theme_id INT,
    PRIMARY KEY (game_id, theme_id),
    CONSTRAINT fk_gt_game FOREIGN KEY (game_id) REFERENCES games(game_id),
    CONSTRAINT fk_gt_theme FOREIGN KEY (theme_id) REFERENCES themes(theme_id)
);

CREATE TABLE reviews (
    game_id INT,
    user_id INT,
    rating NUMERIC(4,2),
    PRIMARY KEY (game_id, user_id),
    CONSTRAINT fk_review_game FOREIGN KEY (game_id) REFERENCES games(game_id),
    CONSTRAINT fk_review_user FOREIGN KEY (user_id) REFERENCES users(user_id)
);