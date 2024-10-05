import project0.main  # Assuming the new code is saved as `project0/main.py`
import os
import sqlite3
import requests
import pytest

# Test for downloading PDF from the URL
def test_download_incident_pdf():
    url = "https://www.normanok.gov/sites/default/files/documents/2024-08/2024-08-01_daily_incident_summary.pdf"
    pdf_path = project0.main.download_incident_pdf(url)
    assert pdf_path is not None, "PDF should be downloaded successfully"
    assert os.path.exists(pdf_path), "The PDF file should exist in the resources folder"

# Test for inserting data into the database
def test_insert_incident_data():
    # Mock the incident data
    mock_incident = {
        'date_time': '09/08/2024 12:00',
        'incident_number': '123456',
        'location': 'Main St',
        'nature': 'Fire',
        'incident_ori': 'NORMAN'
    }
    
    conn = project0.main.create_database('test_incidents.db')  # Create test database
    project0.main.insert_incident_data(conn, mock_incident)
    
    # Verify that the data has been inserted correctly
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incidents;")
    result = cursor.fetchall()
    
    assert len(result) == 1, "One incident should be inserted"
    assert result[0][1:] == ('09/08/2024 12:00', '123456', 'Main St', 'Fire', 'NORMAN'), "The inserted data should match the mock incident"
    
    cursor.execute("DROP TABLE incidents;")
    conn.close()
    
# Test for database creation
def test_create_database():
    conn = project0.main.create_database('test_incidents.db')
    assert conn is not None, "Database connection should be established"
    
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='incidents';")
    result = cursor.fetchone()
    assert result is not None, "The 'incidents' table should be created"
    
    cursor.execute("DROP TABLE incidents;")
    conn.close()

# Test for extracting PDF data and verifying correct format
def test_extract_incident_pdf_data():
    url = "https://www.normanok.gov/sites/default/files/documents/2024-08/2024-08-01_daily_incident_summary.pdf"
    pdf_path = project0.main.download_incident_pdf(url)
    
    incidents = project0.main.extract_incident_pdf_data(pdf_path)
    assert len(incidents) > 0, "There should be incidents extracted from the PDF"
    assert 'date_time' in incidents[0], "Incident data should contain 'date_time'"
    assert 'incident_number' in incidents[0], "Incident data should contain 'incident_number'"


# Test for HTTP status code
def test_status_code():
    url = "https://www.normanok.gov/sites/default/files/documents/2024-08/2024-08-09_daily_incident_summary.pdf"
    response = requests.get(url)
    assert response.status_code == 200, "The URL should return a 200 status code"
