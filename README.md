# cis6930fa24 -- Project 0 -- Incident Report Processing

Name: Archit Mittal 

# Project Description 
This project processes incident reports from a PDF file, extracts relevant data such as incident date, time, location, and nature, and stores it in a SQLite database. The project provides a summary of the incidents by categorizing them based on the "Nature" field, sorted alphabetically and case-sensitively, and outputs the result in a specific format.

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

 1. **`Fetching_Incidents_PDF(url):`**
   This function downloads a PDF file from the provided URL and saves it to the `resources` directory.

    **Parameters:**
    - `url`: The URL of the PDF file to be downloaded.

    **Returns:**
    - The file path of the downloaded PDF if successful, or `None` otherwise.

2. **`Extracting_the_IncidentsPDF_Contents(pdf_path):`**
   This function reads a PDF file, extracts relevant incident data, and returns it as a list of dictionaries with fields such as `date_time`, `incident_number`, `location`, `nature`, and `incident_ori`.

    **Parameters:**
    - `pdf_path`: The path to the downloaded PDF file.

    **Returns:**
    - A list of dictionaries where each dictionary represents one incident.


 3. **`create_database(db_name='normanpd.db'):`**
   This function creates an SQLite database with a table named `incidents`.

    **Parameters:**
    - `db_name`: (Optional) The name of the SQLite database. Defaults to 'normanpd.db'.

    **Returns:**
    - A connection to the SQLite database.

 5. **`insert_incident_data(conn, incident):`**
   This function inserts a single incident's data into the `incidents` table in the database.

    **Parameters:**
    - `conn`: The database connection object.
    - `incident`: A dictionary containing a single incident's data.

 6. **`print_nature_counts(conn):`**
   This function generates a report summarizing the number of occurrences of each type of incident (based on nature), sorted alphabetically and case-sensitively, and prints it in the format `Nature|Count`.

    **Parameters:**
    - `conn`: The database connection object.

    **Returns:**
    - Prints the nature count summary directly to the console.

### 7. **`main(url, db_name='normanpd.db'):`**
   This is the main function that orchestrates downloading, extracting, storing, and printing incident data.

    **Parameters:**
    - `url`: The URL of the PDF to download.
    - `db_name`: (Optional) The name of the SQLite database. Defaults to 'normanpd.db'.

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
