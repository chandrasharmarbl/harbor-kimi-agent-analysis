"""
Use this file to define pytest tests that verify the outputs of the task.

This file will be copied to /tests/test_outputs.py and run by the /tests/test.sh file
from the working directory.
"""
import subprocess
import time
import pytest
import requests
import threading
import socket

def get_docker_gateway_ip():
    cmd = "ip route | grep default | awk '{print $3}'"
    return subprocess.check_output(cmd, shell=True).decode().strip()

def bridge_data(src, dst):
    try:
        while True:
            try:
                data = src.recv(4096)
            except (OSError, ConnectionResetError):
                break
                
            if not data:
                break
            dst.sendall(data)
    except Exception:
        pass
    finally:
        try:
            src.close()
        except: pass
        try:
            dst.close()
        except: pass

def start_forwarding(local_port, remote_host, remote_port):
    def server_loop():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('127.0.0.1', local_port))
        server.listen(128) 
        
        while True:
            client_sock, _ = server.accept()
            
            remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_sock.settimeout(2)
            
            try:
                remote_sock.connect((remote_host, remote_port))
                remote_sock.settimeout(None)
                
                threading.Thread(target=bridge_data, args=(client_sock, remote_sock), daemon=True).start()
                threading.Thread(target=bridge_data, args=(remote_sock, client_sock), daemon=True).start()
            except Exception as e:
                client_sock.close()
                remote_sock.close()

    t = threading.Thread(target=server_loop, daemon=True)
    t.start()

@pytest.fixture(scope="session", autouse=True)
def python_network_bridge():
    """Pytest fixture to trigger the forwarding logic."""
    host_ip = get_docker_gateway_ip()
    ports_to_forward = [8080, 5432]
    
    print(f"\n--- Python Socket Bridge: localhost -> {host_ip} ---")
    
    for port in ports_to_forward:
        start_forwarding(port, host_ip, port)
        print(f"Forwarding started: localhost:{port} is now mapped to {host_ip}:{port}")
    
    # No cleanup needed for daemon threads; they die when the main process exits
    yield

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

def test_ports_exposed_external():
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}|{{.Ports}}"],
        capture_output=True,
        text=True,
        check=True
    )
    
    ports_map = {}
    for line in result.stdout.strip().split('\n'):
        if '|' in line:
            name, ports = line.split('|', 1)
            ports_map[name] = ports
            
    assert "app-nestjs" in ports_map, "app-nestjs is not found in ps output"
    assert ":8080->" in ports_map["app-nestjs"], "External port 8080 is not mapped for app-nestjs"
    
    assert "app-postgres" in ports_map, "app-postgres is not found in ps output"
    assert ":5432->" in ports_map["app-postgres"], "External port 5432 is not mapped for app-postgres"


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
