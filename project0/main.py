# import argparse
# import urllib
# import urllib.request
# import sqlite3
# import fitz  # PyMuPDF
# import os
# from datetime import datetime
# import re



# # Define a function to check if a string can be parsed into a datetime object.
# def checkingDateAndTime(str):
#     try:
#         datetime.strptime(str, "%d/%m/%Y %H:%M")
#         return True
#     except ValueError:
#         return False

# def extractingIncidents():
#     # Open the temporary PDF file.
#     doc = fitz.open("incident_data.pdf")

#     all_text = ""
#     # Iterate through each page in the PDF and extract text.
#     for page in doc:
#         all_text += page.get_text()

#     # Close the PDF document to free resources.
#     doc.close()

#     # Split the extracted text into lines.
#     lines = all_text.split('\n')

#     # Clean up the extracted lines if necessary.
#     for i in range(5):
#         if len(lines) > 0:
#             lines.pop(0)

#     if len(lines) > 0 and lines[-1] == "":
#         lines.pop()
    
#     if len(lines) > 0 and ":" in lines[-1] and "/" in lines[-1]:
#         lines.pop()

#     # Initialize lists to hold the extracted incident data.
#     date_times, incident_numbers, locations, natures, incident_oris = [], [], [], [], []
    
#     # Loop through the lines and extract incident data.
#     for i in range(0, len(lines)):
#         if 'Date / Time' in lines[i]: 
#             continue

#         # Check for the pattern indicating the start of an incident record.
#         if i + 4 < len(lines) and '/' in lines[i] and ':' in lines[i]:
#                 date_times.append(lines[i].strip())
#                 incident_numbers.append(lines[i + 1].strip())
#                 locations.append(lines[i + 2].strip())
#                 if checkingDateAndTime(lines[i + 3].strip()):
#                     natures.append("")
#                 else:
#                     if lines[i + 3].strip() == "RAMP" :
#                         natures.append(lines[i+4].strip())
#                     else:
#                         natures.append(lines[i + 3].strip())
#                 incident_oris.append(lines[i + 4].strip())

#     # Package the extracted data into a dictionary.
#     data = {
#         'Date/Time': date_times,
#         'Incident Number': incident_numbers,
#         'Location': locations,
#         'Nature': natures,
#         'Incident ORI': incident_oris 
#     }
#     return data

# def createDb():
#     # Create a new SQLite database.
#     try :
#         conn = sqlite3.connect('resources/normanpd.db')
#         c = conn.cursor()

#         # Create a new table in the database.
#         c.execute('''CREATE TABLE incidents
#                     (date_time TEXT, incident_number TEXT, incident_location TEXT, nature TEXT, incident_ori TEXT)''')

#         # Commit the changes and close the connection.
#         return conn
#     except Exception as e:
#         return e

# def storingData(db, data):
#     # Insert the extracted data into the database.
#     try:
#         c = db.cursor()
#         c.execute("DELETE FROM incidents")  # Clear the table before inserting new data.
#         for i in range(len(data['Date/Time'])):
#             c.execute("INSERT INTO incidents VALUES (?, ?, ?, ?, ?)",
#                       (data['Date/Time'][i], data['Incident Number'][i], data['Location'][i], data['Nature'][i], data['Incident ORI'][i]))

#         db.commit()
#         os.remove("incident_data.pdf")
#     except Exception as e:
#         return e
    
# def fetchFromUrl(url):
    
#     try :
#         if(url is None):
#             return None
#         url = f"{url}"
#         headers ={}
#         headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
#         data = urllib.request.urlopen(urllib.request.Request(url=url, headers=headers)).read()
        
#         if data is None:
#             return "No Data found"
        
#         with open("incident_data.pdf", "wb") as file:
#             file.write(data)
#         return data 
    

#     except Exception as e:
#         return e
                      

# def status(db):
#     try: 
#         c = db.cursor()
#         query = '''SELECT TRIM(nature), COUNT(*) as count FROM incidents 
#                    GROUP BY TRIM(nature) ORDER BY nature ASC;'''
#         c.execute(query)
#         output = ""
#         for row in c.fetchall():
#             output += row[0] + "|" + str(row[1]) + "\n"
            
#         c.execute('''DROP TABLE incidents''')
        
#         return output
#     except Exception as e:
#         return e


# def main(url):
    
#     # Download data
    
#     fetchFromUrl(url) 
#     incidents = extractingIncidents()
#     db = createDb()
#     storingData(db, incidents)
#     output = status(db)
#     print(output.strip())
    
#     return output.strip()


# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--incidents", type=str, required=True, 
#                          help="Incident summary url.")
     
#     args = parser.parse_args()
#     if args.incidents:
#         main(args.incidents)

import argparse      
import sqlite3
import re
import urllib.request
import os
import fitz 
import pypdf
from pypdf import PdfReader

# This function is used to collect the data from the given URL of the incidents.
def download_incident_report_pdf(pdf_url):
    try:
        request_headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux i686) Chrome/24.0.1312.27 Safari/537.17"
        }
        url_request = urllib.request.Request(pdf_url, headers=request_headers)
    
        output_dir = os.path.join(os.getcwd(), 'output_files')
        os.makedirs(output_dir, exist_ok=True)

        pdf_file_path = os.path.join(output_dir, 'incident_report.pdf')

        with urllib.request.urlopen(url_request) as url_response:
            with open(pdf_file_path, 'wb') as pdf_file:
                pdf_file.write(url_response.read())
                return pdf_file_path
    except urllib.error.URLError as url_error:
        return None
    except Exception as generic_error:
        pass
        #print(f"An unforeseen error occurred: {generic_error}")

# Function to normalize incident descriptions by cleaning up unnecessary parts.
def clean_incident_description(description):
    cleaned_description = description.strip()  # Removes any leading/trailing spaces
    cleaned_description = re.sub(r'\s+', ' ', cleaned_description)  # Collapses multiple spaces into one
    cleaned_description = re.sub(r'\b([A-Za-z\s]+?)(?:\s+[A-Z]+(?:\s+[A-Z]+)\b.|\|\s*\d+)$', r'\1', cleaned_description).strip()
    cleaned_description = re.sub(r'(?<!\d)(\d{7})(?!\d)', '', cleaned_description)  # Removes isolated ORI numbers (7 digits)
    cleaned_description = re.sub(r'\s*\d+$', '', cleaned_description)  # Removes trailing digits that might represent the ORI
    return cleaned_description.strip()

# Function to extract the contents from the given incidents PDF
def extract_incident_data_from_pdf(pdf_path):
    column_positions = [52.56, 150.86, 229.82, 423.19, 623.86]
    extracted_row_data = ["", "", "", "", ""]
    ori_pattern = re.compile(r'[A-Z]{2}\d{7}')  # This is how Incident ORI looks like

    pdf_headers = {"Date/Time", "Incident Number", "Location", "Nature", "Incident ORI"}
    pdf_document = fitz.open(pdf_path)  # Opens the PDF
    extracted_incidents = []

    # Goes through every page in the PDF
    for pdf_page in pdf_document:
        previous_line_number = 0
        previous_block_number = 1
        page_words = pdf_page.get_text("Words")

        current_line_text = ""
        current_x_coord = 0
        for word in page_words:
            if previous_line_number == word[6]:  # Checks if the line has the previous word in it
                current_line_text = current_line_text + " " + word[4] if word[7] > 0 else word[4]
                current_x_coord = word[0]
            else:  # If the word is in a new line, extract and handle multiple lines
                for index, column_start in enumerate(column_positions):
                    if index < len(column_positions) - 1:
                        if column_start <= current_x_coord < column_positions[index + 1]:
                            handle_multi_line_data(extracted_row_data, index, current_line_text)
                    elif index == len(column_positions) - 1 and current_x_coord >= column_start:
                        handle_multi_line_data(extracted_row_data, index, current_line_text)

                current_line_text = word[4]
                current_x_coord = word[0]
                previous_line_number = word[6]

            if word[5] != previous_block_number:
                nature_field = extracted_row_data[3].strip()
                nature_parts = nature_field.rsplit(' ', 1)

                if len(nature_parts) > 1 and ori_pattern.match(nature_parts[1]):
                    extracted_row_data[3] = nature_parts[0]  # Check if the split string's second part is the Incident ORI
                    extracted_row_data[4] = nature_parts[1]
                else:
                    extracted_row_data[3] = nature_field

                extracted_row_data[3] = clean_incident_description(extracted_row_data[3])

                # Check if the current row contains any header and skip it
                if (extracted_row_data[0] not in pdf_headers and 
                    extracted_row_data[1] not in pdf_headers and 
                    extracted_row_data[2] not in pdf_headers and 
                    extracted_row_data[3] not in pdf_headers and 
                    extracted_row_data[4] not in pdf_headers):

                    incident_record = {
                        "date_time": extracted_row_data[0],
                        "incident_number": extracted_row_data[1],
                        "location": extracted_row_data[2],
                        "nature": extracted_row_data[3],
                        "incident_ori": extracted_row_data[4]
                    }

                    # Modify validity check: require only some fields to be non-empty
                    if all(incident_record[field] for field in ['date_time', 'incident_number', 'location', 'nature']):
                        extracted_incidents.append(incident_record)

                # Reset ColumnData after processing
                extracted_row_data = ["", "", "", "", ""]
                previous_block_number = word[5]

    pdf_document.close()

    # Returns the valid incidents which contain at least the necessary fields
    return extracted_incidents

# Function to handle if there are multiple lines in the same column.
def handle_multi_line_data(extracted_row_data, index, line_text):
    if extracted_row_data[index]:
        extracted_row_data[index] += " " + line_text.strip()
    else:
        extracted_row_data[index] = line_text.strip()

# Function to create a database, we can either enter the database name in the command line or default database name.
def initialize_database(db_name):
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.getcwd(), 'output_files')
    os.makedirs(output_dir, exist_ok=True)  

    db_file_path = os.path.join(output_dir, db_name) 
     # Save to output directory
    if os.path.exists(db_file_path):
        os.remove(db_file_path)
    connection = sqlite3.connect(db_file_path)
    cursor = connection.cursor()
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
    connection.commit()         # saving the changes
    return connection

# Function to insert an incident into the database.
def insert_incident_into_db(connection, incident_record):
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO incidents (date_time, incident_number, location, nature, incident_ori)
        VALUES (?, ?, ?, ?, ?)
    ''', (incident_record['date_time'], incident_record['incident_number'], incident_record['location'], incident_record['nature'], incident_record['incident_ori']))
    connection.commit()

# Function to print the nature and the counts
def print_nature_occurrences(connection):
    cursor = connection.cursor()
    cursor.execute('''
        SELECT TRIM(nature), COUNT(*)    
        FROM incidents 
        GROUP BY TRIM(nature)
        ORDER BY nature ASC
    ''')
    results = cursor.fetchall()

    for nature, count in results:
        if nature:
            print(f"{nature}|{count}")    # prints nature and count using separator |

# Main Function
def main(pdf_url, database_name='incident_report.db'):  # default database name 
    pdf_file_path = download_incident_report_pdf(pdf_url)  # download the PDF
    extracted_incidents = extract_incident_data_from_pdf(pdf_file_path)  # extract data from the PDF
    db_connection = initialize_database(database_name)  # create the database
    for incident in extracted_incidents:  # insert incidents into the database
        insert_incident_into_db(db_connection, incident)

    # Print nature counts
    print_nature_occurrences(db_connection)

    db_connection.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--incidents", type=str, required=True, help="Incidents PDF URL")
    parser.add_argument("--db", type=str, default='incident_report.db', help="SQLite Database name. Defaults to 'incident_report.db'.")

    args = parser.parse_args()

    main(args.incidents, args.db)
