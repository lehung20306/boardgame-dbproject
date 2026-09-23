import psycopg2
import os

def auto_import_data():
    try:
        # 1. Establish database connection
        # (Replace 'YOUR_PASSWORD' with your actual pgAdmin password)
        connection = psycopg2.connect(
            host="localhost",
            database="boardgamedb",
            user="postgres",
            password="YOUR_PASSWORD", 
            port="5432"
        )
        cursor = connection.cursor()
        
        # 2. Define the list of tables and their corresponding CSV files
        # Order matters: Independent tables first, junction/dependent tables last to avoid Foreign Key violations
        tables_and_files = [
            ('games', './new_data/games_cleaned.csv'),
            ('mechanics', './new_data/mechanics_cleaned.csv'),
            ('themes', './new_data/themes_cleaned.csv'),
            ('users', './new_data/users_cleaned.csv'),
            ('game_mechanic', './new_data/game_mechanic.csv'),
            ('game_theme', './new_data/game_theme.csv'),
            ('reviews', './new_data/reviews_cleaned.csv')
        ]

        print("Starting automated data import process...")
        
        # 3. Iterate through the list and import data into PostgreSQL
        for table_name, file_path in tables_and_files:
            if not os.path.exists(file_path):
                print(f"Warning: Skipping {table_name}. File not found at {file_path}")
                continue
                
            print(f"Importing data into table: {table_name}...")
            
            # Open the CSV file and use copy_expert for high-speed bulk loading
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_copy = f"COPY {table_name} FROM STDIN WITH CSV HEADER DELIMITER ','"
                cursor.copy_expert(sql_copy, f)
                
        # 4. Commit all transactions to the database
        connection.commit()
        print("\nSuccess! All data has been imported into the database.")

    except (Exception, psycopg2.Error) as error:
        print("\nImport failed due to an error:", error)
        # Rollback any changes if an error occurs during the process
        if connection:
            connection.rollback()

    finally:
        # 5. Safely close the database connection
        if connection:
            cursor.close()
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    auto_import_data()