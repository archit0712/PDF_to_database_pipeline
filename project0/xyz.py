# Importing the Necessary libraries
import argparse      
import sqlite3
import re
import urllib.request
import os
import fitz 
import pypdf
from pypdf import PdfReader



# This function is used to collect the data from the given URL of the incidents.
def Fetching_Incidents_PDF(url):
    try:
        headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux i686) Chrome/24.0.1312.27 Safari/537.17"
        }
        req = urllib.request.Request(url, headers=headers)
    
        resources_dir = os.path.join(os.getcwd(), 'resources')
        os.makedirs(resources_dir, exist_ok=True)

        file_name = os.path.join(resources_dir, 'Incident.PDF')

        with urllib.request.urlopen(req) as response:
            with open(file_name, 'wb') as file:
                file.write(response.read())
                return file_name
    except urllib.error.URLError as e:
        return None
    except Exception as e:
        pass
        #print(f"An unforeseen error occurred: {e}")
       





# Function to normlaize unnecessary word
# This function will be responsible for clearling the out the unnecessary incident ORI Words. Some nature have different ORI, But we need the count for nature irrespective of ori then this is used.        
# def Normalizing_the_nature(nature):
#     N=nature
#     # N = N.lower().strip()
#     N = re.sub(r'\s+', ' ', N)        # Removes spaces, digits and unnecessary word that are not in the format of incident ORI
#     N = re.sub(r'\b\d+\b', '', N)    
#     N = re.sub(r'\bemsstat\b', '', N)  
#     return N.strip()

def Normalizing_the_nature(nature):
    N = nature.strip()  # Removes any leading/trailing spaces
    N = re.sub(r'\s+', ' ', N)  # Collapses multiple spaces into one
    # N = re.sub(r'\bemsstat\b', '', N, flags=re.IGNORECASE)  # Removes specific unwanted words like 'emsstat', case-insensitive
    N = re.sub(r'\b([A-Za-z\s]+?)(?:\s+[A-Z]+(?:\s+[A-Z]+)\b.|\|\s*\d+)$', r'\1', N).strip()
    N = re.sub(r'(?<!\d)(\d{7})(?!\d)', '', N)  # Removes isolated ORI numbers (7 digits)
    N = re.sub(r'\s*\d+$', '', N)  # Removes trailing digits that might represent the ORI
    return N.strip()


# Function to extract the contents from the given incidents PDF
# Function to extract the contents from the given incidents PDF
def Extracting_the_IncidentsPDF_Contents(pdf_path):
    Column_Coor = [52.56, 150.86, 229.82, 423.19, 623.86]
    ColumnData = ["", "", "", "", ""]
    ORI = re.compile(r'[A-Z]{2}\d{7}')  # This is how Incident ORI looks like

    HEADERS = {"Date/Time", "Incident Number", "Location", "Nature", "Incident ORI"}
    PDF = fitz.open(pdf_path)  # Opens the PDF
    incidents = []

    # Goes through every page in the PDF
    for page in PDF:
        Pre_line = 0
        Pre_block = 1
        Words = page.get_text("Words")

        line = ""
        x = 0
        for word in Words:
            if Pre_line == word[6]:  # Checks if the line has the previous word in it
                line = line + " " + word[4] if word[7] > 0 else word[4]
                x = word[0]
            else:  # If the word is in a new line, extract and handle multiple lines
                for index, Column_coor in enumerate(Column_Coor):
                    if index < len(Column_Coor) - 1:
                        if Column_coor <= x < Column_Coor[index + 1]:
                            Multiple_Lines_handler(ColumnData, index, line)
                    elif index == len(Column_Coor) - 1 and x >= Column_coor:
                        Multiple_Lines_handler(ColumnData, index, line)

                line = word[4]
                x = word[0]
                Pre_line = word[6]

            if word[5] != Pre_block:
                nature = ColumnData[3].strip()
                NatureParts = nature.rsplit(' ', 1)

                if len(NatureParts) > 1 and ORI.match(NatureParts[1]):
                    ColumnData[3] = NatureParts[0]  # Check if the split string's second part is the Incident ORI
                    ColumnData[4] = NatureParts[1]
                else:
                    ColumnData[3] = nature

                ColumnData[3] = Normalizing_the_nature(ColumnData[3])

                # Check if the current row contains any header and skip it
                if (ColumnData[0] not in HEADERS and 
                    ColumnData[1] not in HEADERS and 
                    ColumnData[2] not in HEADERS and 
                    ColumnData[3] not in HEADERS and 
                    ColumnData[4] not in HEADERS):

                    incident = {
                        "date_time": ColumnData[0],
                        "incident_number": ColumnData[1],
                        "location": ColumnData[2],
                        "nature": ColumnData[3],
                        "incident_ori": ColumnData[4]
                    }

                    # Modify validity check: require only some fields to be non-empty
                    if all(incident[field] for field in ['date_time', 'incident_number', 'location', 'nature']):
                        incidents.append(incident)

                # Reset ColumnData after processing
                ColumnData = ["", "", "", "", ""]
                Pre_block = word[5]

    PDF.close()

    # Returns the valid incidents which contain at least the necessary fields
    return incidents


# Function to handle if there are multiple lines in the same column.
def Multiple_Lines_handler(ColumnData, index, line):
    if ColumnData[index]:
        ColumnData[index] += " " + line.strip()
    else:
        ColumnData[index] = line.strip()



# Function to create a database , we can either enter the database name in the command line or default database name.
# Function to create a database, we can either enter the database name in the command line or default database name.
def create_database(db_name):
    # Create resources directory if it doesn't exist
    resources_dir = os.path.join(os.getcwd(), 'resources')
    os.makedirs(resources_dir, exist_ok=True)  

    db_path = os.path.join(resources_dir, db_name) 
     # Save to resources directory
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
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



# Fucntion to insert an incident into the database.
def insert_incident(conn, incident):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO incidents (date_time, incident_number, location, nature, incident_ori)
        VALUES (?, ?, ?, ?, ?)
    ''', (incident['date_time'], incident['incident_number'], incident['location'], incident['nature'], incident['incident_ori']))
    conn.commit()


# Function to print the nature and the counts
def print_nature_counts(conn):
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
            print(f"{nature}|{count}")    # prints nature and count using seperator |


# Main Fucntion
def main(url,db_name='normanpd.db'):       # default database name 
    incident_data = Fetching_Incidents_PDF(url)        # fetch the data
    incidents = Extracting_the_IncidentsPDF_Contents(incident_data)     # Extracting the contents
    conn = create_database(db_name)           # Database creation
    for incident in incidents:                  # Insertion 
        insert_incident(conn, incident)

    # Print nature counts
    print_nature_counts(conn)

    conn.close()

if _name_ == '_main_':
    parser = argparse.ArgumentParser()
    parser.add_argument("--incidents", type=str, required=True, help="incidents PDF URL")
    parser.add_argument("--db", type=str, default='normanpd.db', help=" SQLite Database name. Defaults to 'normanpd.db'.")

    args = parser.parse_args()

    main(args.incidents, args.db)