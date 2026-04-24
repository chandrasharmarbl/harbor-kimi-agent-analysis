"""
Use this file to define pytest tests that verify the outputs of the task.

This file will be copied to /tests/test_outputs.py and run by the /tests/test.sh file
from the working directory.
"""
import subprocess
import time
import pytest
import requests
from network_bridge import python_network_bridge

def test_containers_running():
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
        check=True
    )
    running_containers = result.stdout.strip().split('\n')
    assert "app-postgres" in running_containers, "app-postgres container is not running"
    assert "app-nestjs" in running_containers, "app-nestjs container is not running"

def test_ports_exposed():
    result_8080 = subprocess.run(
        ["docker", "port", "app-nestjs", "8080/tcp"],
        capture_output=True,
        text=True
    )
    assert result_8080.returncode == 0 and result_8080.stdout.strip() != "", "Port 8080 is not exposed/mapped on app-nestjs"

    result_5432 = subprocess.run(
        ["docker", "port", "app-postgres", "5432/tcp"],
        capture_output=True,
        text=True
    )
    assert result_5432.returncode == 0 and result_5432.stdout.strip() != "", "Port 5432 is not exposed/mapped on app-postgres"

def test_checkdb_endpoint(python_network_bridge):
    url = "http://localhost:8080/checkdb"
    max_retries = 10
    success = False
    error_msg = ""
    
    for _ in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                assert len(response.text) > 0, "Response body was empty"
                success = True
                break
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
        time.sleep(2)
            
    if not success:
        pytest.fail(f"Failed to get a 200 OK from {url} after {max_retries} retries. Last error: {error_msg}")
