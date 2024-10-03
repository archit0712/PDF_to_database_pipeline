import argparse
import urllib
import urllib.request
import sqlite3
import fitz  # PyMuPDF
import os
from datetime import datetime


# Define a function to check if a string can be parsed into a datetime object.
def checkingDateAndTime(str):
    try:
        datetime.strptime(str, "%d/%m/%Y %H:%M")
        return True
    except ValueError:
        return False

def extractingIncidents():
    # Open the temporary PDF file.
    doc = fitz.open("incident_data.pdf")

    all_text = ""
    # Iterate through each page in the PDF and extract text.
    for page in doc:
        all_text += page.get_text()

    # Close the PDF document to free resources.
    doc.close()

    # Split the extracted text into lines.
    lines = all_text.split('\n')

    # Clean up the extracted lines if necessary.
    for i in range(5):
        if len(lines) > 0:
            lines.pop(0)

    if len(lines) > 0 and lines[-1] == "":
        lines.pop()
    
    if len(lines) > 0 and ":" in lines[-1] and "/" in lines[-1]:
        lines.pop()

    # Initialize lists to hold the extracted incident data.
    date_times, incident_numbers, locations, natures, incident_oris = [], [], [], [], []
    
    # Loop through the lines and extract incident data.
    for i in range(0, len(lines)):
        if 'Date / Time' in lines[i]: 
            continue

        # Check for the pattern indicating the start of an incident record.
        if i + 4 < len(lines) and '/' in lines[i] and ':' in lines[i]:
                date_times.append(lines[i].strip())
                incident_numbers.append(lines[i + 1].strip())
                locations.append(lines[i + 2].strip())
                if checkingDateAndTime(lines[i + 3].strip()):
                    natures.append("")
                else:
                    if lines[i + 3].strip() == "RAMP" :
                        natures.append(lines[i+4].strip())
                    else:
                        natures.append(lines[i + 3].strip())
                incident_oris.append(lines[i + 4].strip())

    # Package the extracted data into a dictionary.
    data = {
        'Date/Time': date_times,
        'Incident Number': incident_numbers,
        'Location': locations,
        'Nature': natures,
        'Incident ORI': incident_oris 
    }
    return data

def createDb():
    # Create a new SQLite database.
    try :
        conn = sqlite3.connect('resources/normanpd.db')
        c = conn.cursor()

        # Create a new table in the database.
        c.execute('''CREATE TABLE incidents
                    (date_time TEXT, incident_number TEXT, incident_location TEXT, nature TEXT, incident_ori TEXT)''')

        # Commit the changes and close the connection.
        return conn
    except Exception as e:
        return e

def storingData(db, data):
    # Insert the extracted data into the database.
    try:
        c = db.cursor()
        c.execute("DELETE FROM incidents")  # Clear the table before inserting new data.
        for i in range(len(data['Date/Time'])):
            c.execute("INSERT INTO incidents VALUES (?, ?, ?, ?, ?)",
                      (data['Date/Time'][i], data['Incident Number'][i], data['Location'][i], data['Nature'][i], data['Incident ORI'][i]))

        db.commit()
        os.remove("incident_data.pdf")
    except Exception as e:
        return e
    
def fetchFromUrl(url):
    
    try :
        if(url is None):
            return None
        url = f"{url}"
        headers ={}
        headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
        data = urllib.request.urlopen(urllib.request.Request(url=url, headers=headers)).read()
        
        if data is None:
            return "No Data found"
        
        with open("incident_data.pdf", "wb") as file:
            file.write(data)
        return data 
    

    except Exception as e:
        return e
                      

def status(db):
    try: 
        c = db.cursor()
        query = '''SELECT nature, COUNT(*) as count FROM incidents 
                   GROUP BY nature ORDER BY nature ASC;'''
        c.execute(query)
        output = ""
        for row in c.fetchall():
            output += row[0] + "|" + str(row[1]) + "\n"
            
        c.execute('''DROP TABLE incidents''')
        
        return output
    except Exception as e:
        return e


def main(url):
    
    # Download data
    fetchFromUrl(url) 
    incidents = extractingIncidents()
    db = createDb()
    storingData(db, incidents)
    output = status(db)
    print(output.strip())
    
    return output.strip()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--incidents", type=str, required=True, 
                         help="Incident summary url.")
     
    args = parser.parse_args()
    if args.incidents:
        main(args.incidents)

