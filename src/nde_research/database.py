import sqlite3
import logging

__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2024, Sören Gebbert"
__maintainer__ = "Soeren Gebbert"
__email__ = "soerengebbert@holistech.de"

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
                      url TEXT,
                      nde_analysis TEXT,
                      nde_report TEXT,
                      summary TEXT,
                      assessment TEXT,
                      state_of_consciousness TEXT,
                      experience_type TEXT,
                      past_life_memories BOOLEAN,
                      life_review BOOLEAN,
                      higher_knowledge BOOLEAN,
                      future_events BOOLEAN,
                      jesus_christ BOOLEAN,
                      buddha BOOLEAN,
                      mohammed BOOLEAN,
                      profound_experience BOOLEAN,
                      return_to_body TEXT,
                      religion TEXT,
                      gender TEXT,
                      date TEXT)''')
    except sqlite3.Error as e:
        logger.error(f"Error creating table: {e}")


def insert_data(conn, file_name, url, nde_analysis, nde_report, json_data):
    """Insert a new row into the nde_reports table"""
    sql = '''INSERT INTO nde_reports
             (file_name, url, nde_analysis, nde_report, summary, assessment, state_of_consciousness, 
             experience_type, past_life_memories, life_review, higher_knowledge, future_events, 
             jesus_christ, buddha, mohammed,  profound_experience,  return_to_body, religion, gender, date)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    try:
        c = conn.cursor()
        c.execute(sql, (file_name,
                        url,
                        nde_analysis,
                        nde_report,
                        json_data['summary'],
                        json_data['assessment'],
                        json_data['state_of_consciousness'],
                        json_data['experience_type'],
                        json_data['past_life_memories'],
                        json_data['life_review'],
                        json_data['higher_knowledge'],
                        json_data['future_events'],
                        json_data['jesus_christ'],
                        json_data['buddha'],
                        json_data['mohammed'],
                        json_data['profound_experience'],
                        json_data['return_to_body'],
                        json_data['religion'],
                        json_data['gender'],
                        json_data['date']))
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Error inserting data: {e}")
