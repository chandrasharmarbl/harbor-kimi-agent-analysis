import pytest
import socket
import threading
import subprocess

def get_docker_gateway_ip():
    cmd = "ip route | grep default | awk '{print $3}'"
    return subprocess.check_output(cmd, shell=True).decode().strip()

def bridge_data(src, dst):
    try:
        while True:
            data = src.recv(4096)
            if not data:
                break
            dst.sendall(data)
    finally:
        src.close()
        dst.close()

def start_forwarding(local_port, remote_host, remote_port):
    def server_loop():
        local_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        local_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        local_server.bind(('127.0.0.1', local_port))
        local_server.listen(10)
        
        while True:
            client_sock, addr = local_server.accept()
            
            try:
                remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                remote_sock.connect((remote_host, remote_port))
                
                threading.Thread(target=bridge_data, args=(client_sock, remote_sock), daemon=True).start()
                threading.Thread(target=bridge_data, args=(remote_sock, client_sock), daemon=True).start()
            except Exception as e:
                print(f"Failed to connect to remote {remote_host}:{remote_port} - {e}")
                client_sock.close()

    t = threading.Thread(target=server_loop, daemon=True)
    t.start()
    return t

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