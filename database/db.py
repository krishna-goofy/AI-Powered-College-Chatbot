import sqlite3

# Create tables for storing website and PDF data, as well as processed URLs/PDFs
def create_database():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS web_data (id INTEGER PRIMARY KEY, url TEXT, text_data TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS pdf_data (id INTEGER PRIMARY KEY, pdf_path TEXT, text_data TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS processed_urls (url TEXT PRIMARY KEY)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS processed_pdfs (pdf_url TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()

# Insert web data into the database
def insert_web_data(url, text_data):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO web_data (url, text_data) VALUES (?, ?)", (url, text_data))
    conn.commit()
    conn.close()

# Insert PDF data into the database
def insert_pdf_data(pdf_path, text_data):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pdf_data (pdf_path, text_data) VALUES (?, ?)", (pdf_path, text_data))
    conn.commit()
    conn.close()

# Fetch processed URLs to avoid duplicate processing
def get_processed_urls():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM processed_urls")
    urls = [row[0] for row in cursor.fetchall()]
    conn.close()
    return urls

# Add processed URL after scraping
def add_processed_url(url):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO processed_urls (url) VALUES (?)", (url,))
    conn.commit()
    conn.close()

# Fetch processed PDFs to avoid duplicate processing
def get_processed_pdfs():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT pdf_url FROM processed_pdfs")
    pdfs = [row[0] for row in cursor.fetchall()]
    conn.close()
    return pdfs

# Add processed PDF after scraping, only if it's not already in the database
def add_processed_pdf(pdf_url):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # Check if the PDF URL is already in the database
    cursor.execute("SELECT pdf_url FROM processed_pdfs WHERE pdf_url = ?", (pdf_url,))
    result = cursor.fetchone()

    # If the result is None, it means the PDF hasn't been processed yet
    if result is None:
        cursor.execute("INSERT INTO processed_pdfs (pdf_url) VALUES (?)", (pdf_url,))
        conn.commit()
    else:
        print(f"PDF {pdf_url} has already been processed.")

    conn.close()

