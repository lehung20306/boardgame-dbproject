import streamlit as st
import psycopg2
import pandas as pd

# Default Streamlit page configuration (Single Page Mode)
st.set_page_config(page_title="Board Game Dashboard", layout="wide")

# Database connection function with caching
@st.cache_resource
def init_connection():
    return psycopg2.connect(
        host="localhost",
        database="boardgamedb",
        user="postgres",
        password="YOUR_PASSWORD", # <-- ENTER YOUR PGADMIN PASSWORD HERE
        port="5432"
    )

conn = init_connection()

# Function to execute SQL and return a Pandas DataFrame
def run_query(query, params=None):
    with conn.cursor() as cur:
        cur.execute(query, params)
        if cur.description:
            columns = [desc[0] for desc in cur.description]
            data = cur.fetchall()
            return pd.DataFrame(data, columns=columns)
        else:
            conn.commit()
            return pd.DataFrame()

# Helper function to display DataFrame with index starting from 1
def display_df(df):
    if not df.empty:
        df.index = range(1, len(df) + 1)
        st.dataframe(df, width="stretch") # Using "stretch" to fix the InvalidWidthError
    else:
        st.info("No data found.")

# PART 1: OVERVIEW & DEEP ANALYTICS
st.title("Board game analytics dashboard")
st.markdown("---")
st.header("1. Market overview & Analytics")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Top 10 newest games")
    query_new_games = """
        SELECT name AS "Game name", year_published AS "Year"
        FROM games ORDER BY year_published DESC LIMIT 10;
    """
    display_df(run_query(query_new_games))

with col2:
    st.subheader("Top 10 best rated (>5000 votes)")
    query_top_rated = """
        SELECT name AS "Game name", avg_rating AS "Rating"
        FROM games WHERE total_votes > 5000 ORDER BY avg_rating DESC LIMIT 10;
    """
    display_df(run_query(query_top_rated))

with col3:
    st.subheader("Top 3 games each year (From 2020)")
    query_window = """
        WITH RankedGames AS (
            SELECT name, year_published, avg_rating,
                   RANK() OVER(PARTITION BY year_published ORDER BY avg_rating DESC) as rank
            FROM games WHERE year_published >= 2020 AND total_votes > 100
        )
        SELECT name AS "Game name", year_published AS "Year", rank AS "Rank" 
        FROM RankedGames WHERE rank <= 3;
    """
    display_df(run_query(query_window))

# PART 2: ADVANCED MULTI-FACTOR FILTER
st.markdown("---")
st.header("2. Advanced game filter")

# Fetch Mechanics and Themes for the multiselect dropdowns
mechs_df = run_query("SELECT mechanic_name FROM mechanics ORDER BY mechanic_name;")
themes_df = run_query("SELECT theme_name FROM themes ORDER BY theme_name;")
mech_list = mechs_df['mechanic_name'].tolist() if not mechs_df.empty else []
theme_list = themes_df['theme_name'].tolist() if not themes_df.empty else []

with st.form("filter_form"):
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        year_range = st.slider("Year published:", 1980, 2024, (2010, 2024))
        min_rating = st.slider("Min avg rating:", 1.0, 10.0, 7.0, 0.1)
        min_age = st.slider("Max age requirement:", 3, 18, 12)
    with f_col2:
        complexity = st.slider("Complexity (Weight):", 1.0, 5.0, (1.0, 5.0), 0.1)
        min_votes = st.number_input("Min total votes:", min_value=0, value=500, step=100)
        play_time = st.slider("Max play time (mins):", 10, 300, 120, 10)
    with f_col3:
        selected_mechs = st.multiselect("Require mechanics:", mech_list)
        selected_themes = st.multiselect("Require themes:", theme_list)
        
    submitted = st.form_submit_button("Apply filters")

if submitted:
    base_query = """
        SELECT g.name AS "Game name", g.year_published AS "Year", 
               g.min_age AS "Age+", g.play_time AS "Time(m)",
               g.complexity_weight AS "Complexity", g.avg_rating AS "Rating", g.total_votes AS "Votes"
        FROM games g
        WHERE g.year_published >= %s AND g.year_published <= %s
          AND g.avg_rating >= %s
          AND g.total_votes >= %s
          AND g.complexity_weight >= %s AND g.complexity_weight <= %s
          AND (g.min_age <= %s OR g.min_age IS NULL)
          AND (g.play_time <= %s OR g.play_time IS NULL)
    """
    params = [year_range[0], year_range[1], min_rating, min_votes, complexity[0], complexity[1], min_age, play_time]

    if selected_mechs:
        base_query += " AND g.game_id IN (SELECT gm.game_id FROM game_mechanic gm JOIN mechanics m ON gm.mechanic_id = m.mechanic_id WHERE m.mechanic_name = ANY(%s))"
        params.append(selected_mechs)
    
    if selected_themes:
        base_query += " AND g.game_id IN (SELECT gt.game_id FROM game_theme gt JOIN themes t ON gt.theme_id = t.theme_id WHERE t.theme_name = ANY(%s))"
        params.append(selected_themes)

    base_query += " ORDER BY g.avg_rating DESC LIMIT 1000;"
    
    filtered_df = run_query(base_query, params)
    st.success(f"Found {len(filtered_df)} games matching criteria.")
    display_df(filtered_df)

# PART 3: INTERACTIVE ENCYCLOPEDIA (Drill-down)
st.markdown("---")
st.header("3. Search encyclopedia (Game & User details)")
st.info("Copy a game name or Username from the tables above and paste below to view full details and cross-references.")

s_col1, s_col2 = st.columns(2)

# ----- GAME DETAILS SECTION -----
with s_col1:
    search_game = st.text_input("Search game details:", placeholder="Enter game name...")
    if search_game:
        query_game = "SELECT * FROM games WHERE name ILIKE %s ORDER BY total_votes DESC LIMIT 1;"
        game_info = run_query(query_game, (f"%{search_game}%",))
        
        if not game_info.empty:
            game = game_info.iloc[0]
            st.subheader(f"{game['name']}")

            if pd.notna(game.get('image_url')):
                try:
                    st.image(game['image_url'], width=350)
                except:
                    pass
            st.markdown("---")
            
            # Show Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Rating", f"{game['avg_rating']}/10")
            m2.metric("Complexity", f"{game['complexity_weight']}/5")
            m3.metric("Published", int(game['year_published']) if pd.notna(game['year_published']) else "N/A")
            
            # Show User Reviews for this Game
            st.markdown(f"**Recent User reviews for {game['name']}**")
            query_game_reviews = """
                SELECT u.username AS "Username", r.rating AS "Rating", r.comment AS "Comment", r.review_date AS "Date"
                FROM reviews r
                JOIN users u ON r.user_id = u.user_id
                WHERE r.game_id = %s
                ORDER BY r.review_date DESC LIMIT 20;
            """
            game_reviews_df = run_query(query_game_reviews, (int(game['game_id']),))
            display_df(game_reviews_df)
        else:
            st.warning("Game not found.")

# ----- USER DETAILS SECTION -----
with s_col2:
    search_user = st.text_input("Search User profile:", placeholder="Enter Username...")
    if search_user:
        query_user = "SELECT * FROM users WHERE username ILIKE %s LIMIT 1;"
        user_info = run_query(query_user, (search_user,))
        
        if not user_info.empty:
            user = user_info.iloc[0]
            st.subheader(f"{user['username']}")
            
            # Show User Info
            u1, u2 = st.columns(2)
            u1.metric("Country", user['country'] if pd.notna(user['country']) else "Unknown")
            u2.metric("Joined date", str(user['created_at']))
            
            # Show Game Reviews by this User
            st.markdown(f"**Games reviewed by {user['username']}**")
            query_user_history = """
                SELECT g.name AS "Game name", r.rating AS "Rating", r.comment AS "Comment", r.review_date AS "Date"
                FROM reviews r
                JOIN games g ON r.game_id = g.game_id
                WHERE r.user_id = %s
                ORDER BY r.review_date DESC;
            """
            user_history_df = run_query(query_user_history, (int(user['user_id']),))
            display_df(user_history_df)
        else:
            st.warning("User not found.")