import project0.main
import os
import sqlite3
import requests
import pytest




def test_fetchFromUrl():
    url = "https://www.normanok.gov/sites/default/files/documents/2024-01/2024-01-01_daily_incident_summary.pdf"
    data = project0.main.fetchFromUrl(url)
    assert data != None

    
def test_storing_data():
    # Mock the incident data
    mock_data = {
        'Date/Time': ['09/08/2024 12:00'],
        'Incident Number': ['123456'],
        'Location': ['Main St'],
        'Nature': ['Fire'],
        'Incident ORI': ['NORMAN']
    }
    
    conn = project0.main.createDb()  # Recreate the database
    project0.main.storingData(conn, mock_data)
    
    # Ensure data is stored correctly
    c = conn.cursor()
    c.execute("SELECT * FROM incidents;")
    results = c.fetchall()
    assert len(results) == 1
    assert results[0] == ('09/08/2024 12:00', '123456', 'Main St', 'Fire', 'NORMAN')
    c.execute("DROP TABLE incidents;")
    conn.close()
    
    
# Test database creation
def test_create_db():

    conn = project0.main.createDb()
    assert conn is not None, "Database connection should be established"
    c = conn.cursor()
    # Ensure the table was created
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='incidents';")
    result = c.fetchone()
    assert result is not None, "Table 'incidents' should be created"
    c.execute("DROP TABLE incidents;")
    conn.close()
    

def test_status_print_check():
    mock_data = {
        'Date/Time': ['09/08/2024 12:00','09/08/2024 12:00'],
        'Incident Number': ['123456','123465'],
        'Location': ['Main St','Main SW'],
        'Nature': ['Fire','Accident'],
        'Incident ORI': ['NORMAN','NORMAN']
    }
    conn = project0.main.createDb()
    c = conn.cursor()
    project0.main.storingData(conn, mock_data)
    output = project0.main.status(conn)
    
    assert output == "Accident|1\nFire|1\n", "Output should be 'Accident|1\nFire|1\n'"
   
def test_status_code():
    url = "https://www.normanok.gov/sites/default/files/documents/2024-08/2024-08-09_daily_incident_summary.pdf"
    response = requests.get(url)
    assert response.status_code == 200, "URL should return a 200 status code"