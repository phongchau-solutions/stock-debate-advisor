import psycopg2
from psycopg2 import sql

def setup_postgresql():
    print("Setting up PostgreSQL database...")
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="password",
            host="localhost",
            port="5432"
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Create database if not exists
        cursor.execute("CREATE DATABASE stock_analysis;")
        print("Database 'stock_analysis' created.")

        # Connect to the new database
        conn.close()
        conn = psycopg2.connect(
            dbname="stock_analysis",
            user="postgres",
            password="password",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()

        # Create tables for fundamental and technical analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fundamental_analysis (
                id SERIAL PRIMARY KEY,
                file_name TEXT,
                analysis_result JSONB
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS technical_analysis (
                id SERIAL PRIMARY KEY,
                file_name TEXT,
                analysis_result JSONB
            );
        ''')
        conn.commit()
        print("Tables for fundamental and technical analysis created.")

    except Exception as e:
        print(f"Error setting up PostgreSQL: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    setup_postgresql()