CREATE TABLE games (
    game_id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    year_published SMALLINT,
    min_players SMALLINT,
    max_players SMALLINT,
    play_time INT,
    min_age SMALLINT,
    complexity_weight NUMERIC(4,2),
    avg_rating NUMERIC(4,2),
    total_votes INT,
    image_url TEXT

    CONSTRAINT chk_min_players CHECK (min_players >= 1),
    CONSTRAINT chk_max_players CHECK (max_players >= min_players),
    CONSTRAINT chk_play_time CHECK (play_time >= 0),
    CONSTRAINT chk_min_age CHECK (min_age >= 0),
    CONSTRAINT chk_complexity CHECK (complexity_weight >= 0 AND complexity_weight <= 5),
    CONSTRAINT chk_avg_rating CHECK (avg_rating >= 0 AND avg_rating <= 10),
    CONSTRAINT chk_total_votes CHECK (total_votes >= 0)
);

CREATE TABLE mechanics (
    mechanic_id INT PRIMARY KEY,
    mechanic_name VARCHAR(255) NOT NULL
);

CREATE TABLE themes (
    theme_id INT PRIMARY KEY,
    theme_name VARCHAR(255) NOT NULL
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

CREATE TABLE users (
    user_id INT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    country VARCHAR(100),
    created_at DATE NOT NULL
);

CREATE TABLE reviews (
    game_id INT,
    user_id INT,
    rating NUMERIC(4,2),
    review_date DATE NOT NULL,
    comment TEXT,
    PRIMARY KEY (game_id, user_id),
    CONSTRAINT fk_review_game FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE,
    CONSTRAINT fk_review_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT chk_rating CHECK (rating >= 0 AND rating <= 10)
);