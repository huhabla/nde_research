import sqlite3
import logging

logger = logging.getLogger(__name__)


def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file"""
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {e}")
        return None


def create_table(conn):
    """Create nde_reports table if it doesn't exist"""
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS nde_reports
                     (id INTEGER PRIMARY KEY,
                      file_name TEXT,
                      summary TEXT,
                      conversations TEXT,
                      spirit_leaders TEXT,
                      state_of_consciousness TEXT,
                      reinkarnation TEXT,
                      experience_type TEXT,
                      assessment TEXT,
                      experienced_god BOOLEAN,
                      experienced_jesus BOOLEAN,
                      compressed_content BLOB)''')
    except sqlite3.Error as e:
        logger.error(f"Error creating table: {e}")


def insert_data(conn, file_name, json_data, compressed_content):
    """Insert a new row into the nde_reports table"""
    sql = '''INSERT INTO nde_reports
             (file_name, summary, conversations, spirit_leaders, state_of_consciousness,
              reinkarnation, experience_type, assessment, experienced_god, experienced_jesus,
              compressed_content)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    try:
        c = conn.cursor()
        c.execute(sql, (file_name,
                        json_data['summary'],
                        json_data['conversations'],
                        ','.join(json_data['spirit_leaders']),
                        json_data['state_of_consciousness'],
                        json_data['reinkarnation'],
                        json_data['experience_type'],
                        json_data['assessment'],
                        json_data['experienced_good'],
                        json_data['experienced_jesus'],
                        compressed_content))
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Error inserting data: {e}")
