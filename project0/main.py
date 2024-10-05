# Importing the Necessary libraries
import argparse      
import sqlite3
import re
import urllib.request
import os
import fitz 
import pypdf
from pypdf import PdfReader

# This function is used to download the data from the given URL of the incidents.
def download_incident_pdf(url):
    try:
        headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux i686) Chrome/24.0.1312.27 Safari/537.17"
        }
        req = urllib.request.Request(url, headers=headers)
    
        resources_folder = os.path.join(os.getcwd(), 'resources')
        os.makedirs(resources_folder, exist_ok=True)

        pdf_file_path = os.path.join(resources_folder, 'Incident.PDF')

        with urllib.request.urlopen(req) as response:
            with open(pdf_file_path, 'wb') as file:
                file.write(response.read())
                return pdf_file_path
    except urllib.error.URLError as e:
        return None
    except Exception as e:
        pass




# Function to extract the contents from the given incidents PDF
def extract_incident_pdf_data(pdf_path):
    column_coordinates = [52.56, 150.86, 229.82, 423.19, 623.86]
    column_values = ["", "", "", "", ""]
    ORI_pattern = re.compile(r'[A-Z]{2}\d{7}')  # This is how Incident ORI looks like

    HEADER_TITLES = {"Date/Time", "Incident Number", "Location", "Nature", "Incident ORI"}
    pdf_document = fitz.open(pdf_path)  # Opens the PDF
    incident_records = []

    # Goes through every page in the PDF
    for page in pdf_document:
        previous_line = 0
        previous_block = 1
        word_items = page.get_text("Words")

        current_line = ""
        current_x = 0
        for word in word_items:
            if previous_line == word[6]:  # Checks if the line has the previous word in it
                current_line = current_line + " " + word[4] if word[7] > 0 else word[4]
                current_x = word[0]
            else:  # If the word is in a new line, extract and handle multiple lines
                for index, column_coordinate in enumerate(column_coordinates):
                    if index < len(column_coordinates) - 1:
                        if column_coordinate <= current_x < column_coordinates[index + 1]:
                            if column_values[index]:
                                column_values[index] += " " + current_line.strip()
                            else:
                                column_values[index] = current_line.strip()
                    elif index == len(column_coordinates) - 1 and current_x >= column_coordinate:
                            if column_values[index]:
                                column_values[index] += " " + current_line.strip()
                            else:
                                column_values[index] = current_line.strip()

                current_line = word[4]
                current_x = word[0]
                previous_line = word[6]

            if word[5] != previous_block:
                incident_nature = column_values[3].strip()

                # Handle ORI detection with "EMSSTAT"
                if "EMSSTAT" in incident_nature:
                    column_values[4] = "EMSSTAT"  # Set "EMSSTAT" as ORI
                    incident_nature = incident_nature.replace("EMSSTAT", "").strip()

                nature_parts = incident_nature.rsplit(' ', 1)
                if len(nature_parts) > 1 and ORI_pattern.match(nature_parts[1]):
                    column_values[3] = nature_parts[0]  # Check if the split string's second part is the Incident ORI
                    column_values[4] = nature_parts[1]
                else:
                    column_values[3] = incident_nature

                
                column_values[3] = column_values[3].strip()  # Removes any leading/trailing spaces
                column_values[3] = re.sub(r'\s+', ' ', column_values[3])  # Collapses multiple spaces into one
                column_values[3] = re.sub(r'\bEMSSTAT\b', '', column_values[3], flags=re.IGNORECASE)  # Removes 'EMSSTAT' if present
                column_values[3] = re.sub(r'\b([A-Za-z\s]+?)(?:\s+[A-Z]+(?:\s+[A-Z]+)\b.|\|\s*\d+)$', r'\1', column_values[3]).strip()
                column_values[3] = re.sub(r'(?<!\d)(\d{7})(?!\d)', '', column_values[3])  # Removes isolated ORI numbers (7 digits)
                column_values[3] = re.sub(r'\s*\d+$', '', column_values[3])  # Removes trailing digits that might represent the ORI
                

                # Check if the current row contains any header and skip it
                if (column_values[0] not in HEADER_TITLES and 
                    column_values[1] not in HEADER_TITLES and 
                    column_values[2] not in HEADER_TITLES and 
                    column_values[3] not in HEADER_TITLES and 
                    column_values[4] not in HEADER_TITLES):

                    incident_record = {
                        "date_time": column_values[0],
                        "incident_number": column_values[1],
                        "location": column_values[2],
                        "nature": column_values[3],
                        "incident_ori": column_values[4]
                    }

                    # Modify validity check: require only some fields to be non-empty
                    if all(incident_record[field] for field in ['date_time', 'incident_number', 'location', 'nature']):
                        incident_records.append(incident_record)

                # Reset column_values after processing
                column_values = ["", "", "", "", ""]
                previous_block = word[5]

    pdf_document.close()

    # Returns the valid incidents which contain at least the necessary fields
    return incident_records



# Function to create a database, we can either enter the database name in the command line or use the default database name.
def create_database(db_name):
    # Create resources directory if it doesn't exist
    resources_folder = os.path.join(os.getcwd(), 'resources')
    os.makedirs(resources_folder, exist_ok=True)  

    database_path = os.path.join(resources_folder, db_name) 
     # Save to resources directory
    if os.path.exists(database_path):
        os.remove(database_path)
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    # Table Creation
    cursor.execute('''         
        CREATE TABLE IF NOT EXISTS incidents (          
            id INTEGER PRIMARY KEY,
            date_time TEXT,
            incident_number TEXT,
            location TEXT,
            nature TEXT,
            incident_ori TEXT
        )
    ''')
    conn.commit()         # saving the changes
    return conn


# Function to insert an incident into the database.
def insert_incident_data(conn, incident):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO incidents (date_time, incident_number, location, nature, incident_ori)
        VALUES (?, ?, ?, ?, ?)
    ''', (incident['date_time'], incident['incident_number'], incident['location'], incident['nature'], incident['incident_ori']))
    conn.commit()


# Function to print the nature and the counts
def print_nature_counts_data(conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT TRIM(nature), COUNT(*)    
        FROM incidents 
        GROUP BY TRIM(nature)
        ORDER BY nature ASC
    ''')
    rows = cursor.fetchall()

    for nature, count in rows:
        if nature:
            print(f"{nature}|{count}")    # prints nature and count using separator |


# Main function
def main(url, db_name='normanpd.db'):       # default database name 
    pdf_data = download_incident_pdf(url)        # download the PDF
    incident_records = extract_incident_pdf_data(pdf_data)     # Extract the contents
    conn = create_database(db_name)           # Create the database
    for incident in incident_records:                  # Insert the data into the database
        insert_incident_data(conn, incident)

    # Print nature counts
    print_nature_counts_data(conn)

    conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--incidents", type=str, required=True, help="incidents PDF URL")

    args = parser.parse_args()
    print(args.incidents)
    main(args.incidents)
