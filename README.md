# cis6930fa24 -- Project 0 -- Incident Report **Process**ing

Name: Archit Mittal 

# Project Description 
This project **process**es incident reports from a PDF file, extracts relevant data such as incident date, time, location, and nature, and stores it in a SQLite database. The project provides a summary of the incidents by categorizing them based on the "Nature" field, sorted alphabetically and case-sensitively, and outputs the result in a specific format.

# How to install
Install the necessary dependencies using `pipenv`:
```bash
pipenv install
```

# How to run
To run the project, use the following command:

```bash
pipenv run python main.py --incidents <URL_to_incident_report>
```

Example:
```bash
pipenv run python main.py --incidents https://www.normanok.gov/sites/default/files/documents/2024-08/2024-08-09_daily_incident_summary.pdf
```

# Video Demo 
[![Watch the video](https://lh3.googleusercontent.com/pw/AP1GczNlNM-FeNkXhuDQLX0aoj6SOHn5hwJVj3ufng5VCG_GyU-2LzzKP2JAE_Pf2T24LMBGYhPYfCO_ELt9aAupGMd8qDqsRVec8_XjsMP1EdWkdfk826RUagm9ac_DssHp79BiBWijyKSrkBKXJbAFGkbR0g=w1163-h653-s-no-gm?authuser=1)](https://drive.google.com/file/d/1sv67F4T72bHF_RxwowXfBpeMEwzntbbJ/view?usp=sharing)
# Functions

1. **`extractingIncidents()`**:
    This function reads a PDF file, extracts relevant incident data, and returns it in the form of a dictionary with fields like Date/Time, Incident Number, Location, Nature, and Incident ORI.

    **Parameters:**
    None.

    **Process**:
    It opens the incident_data.pdf file, extracts the text, cleans the data, and returns it in a structured format.

    **Returns:**
    A dictionary containing lists for each incident detail (Date/Time, Incident Number, Location, Nature, Incident ORI).

2. `fetchFromUrl(url)`:
    This function downloads the PDF file from the given URL and saves it as incident_data.pdf.

   **Parameters:**

    * url: The URL of the PDF file to be downloaded.
    **Process**:
    Sends an HTTP request to the provided URL and downloads the file.

    **Returns:**
    The binary content of the file if successfully fetched, or an error message otherwise.

3. **`createDb():`**
    This function creates an SQLite database with a table named incidents.

    **Returns:**
    A connection to the SQLite database.

    **storingData(db, data):**
    This function takes extracted incident data and stores it into the SQLite database.

    **Parameters**:

    * db: The database connection object.
    * data: A dictionary containing incident details    extracted from the PDF.

    **Process**:
    It inserts the data into the incidents table, clearing any old data.

4. **`status(db):`**
    This function generates a report summarizing the number of occurrences of each type of incident (based on nature), sorted alphabetically and case-sensitively, and prints it in the format Nature|Count.

    **Parameters**:
    * db: The database connection object.

    **Returns**:
    The formatted output string displaying the nature of incidents and their count.

# Database Development
SQLite database named `normanpd.db`.
Table: incidents with columns for `date_time`, `incident_number`, `incident_location`, `nature`, and `incident_ori`.
The table is recreated each time new incident data is fetched and processed.

**Schema:**
```sql
CREATE TABLE incidents (
    date_time TEXT,
    incident_number TEXT,
    incident_location TEXT,
    nature TEXT,
    incident_ori TEXT
);
```
# Bugs and Assumptions
* **Assumptions**:
    The PDF follows a standard format where each incident’s details are consistently placed across pages.
    Incident nature may sometimes be missing; the function attempts to handle such cases.
* **Bugs**:
    If the PDF structure changes significantly, the extraction logic may fail to locate the correct fields.
    Incomplete or malformed data in the PDF could result in misclassified incident types or errors during the data extraction process.