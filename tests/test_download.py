import project0.main
import os
import requests
import pytest

def test_fetchFromUrl():
    url = "https://www.normanok.gov/sites/default/files/documents/2024-01/2024-01-01_daily_incident_summary.pdf"
    data = project0.main.fetchFromUrl(url)
    assert data != None
