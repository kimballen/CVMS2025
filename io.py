"""IO operations for CVMS2025 camera."""
import base64
import logging
import socket
import time
from urllib.parse import quote

_LOGGER = logging.getLogger(__name__)

def send_direct_request(ip, username, password, command):
    """Send direct request to camera."""
    try:
        auth = base64.b64encode(f"{username}:{password}".encode()).decode()
        request = (
            f"GET {command} HTTP/1.0\r\n"
            f"Host: {ip}\r\n"
            f"Authorization: Basic {auth}\r\n"
            "Connection: close\r\n\r\n"
        )
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            sock.connect((ip, 80))
            sock.send(request.encode())
            
            response = b""
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                response += data
                
        return response.decode('utf-8', errors='ignore')
    except Exception as e:
        _LOGGER.error("Connection error: %s", str(e))
        return None

def read_io_status(ip_address, username, password):
    """Read alarm input/output status."""
    try:
        rnd = int(time.time() * 1000)
        response = send_direct_request(
            ip_address,
            username,
            password,
            f"/cgi-bin/readfile.cgi?query=ALARM&rnd={rnd}"
        )
        
        if not response:
            return None
            
        # Parse response
        data = {'ports': []}
        js_vars = parse_js_response(response)
        
        # Parse inputs
        for i in range(1, 4):
            alarm_state = js_vars.get(f'AlarmOut_Use{i}')
            input_type = js_vars.get(f'Alm_InputType{i}')
            if alarm_state:
                state = 'Active' if alarm_state == "2" else 'Inactive'
                config = 'NO' if input_type == "1" else 'NC'
                data['ports'].append({
                    'port': str(i),
                    'state': state,
                    'type': 'Input',
                    'config': config
                })
                
        # Parse output
        output_state = js_vars.get('Alm_OutUse')
        if output_state:
            state = 'Active' if output_state == "4" else 'Inactive'
            data['ports'].append({
                'port': '1',
                'state': state,
                'type': 'Output'
            })
            
        return data
        
    except Exception as e:
        _LOGGER.error("Error reading IO status: %s", str(e))
        return None

def read_temperature(ip_address, username, password):
    """Read temperature from camera."""
    try:
        rnd = int(time.time() * 1000)
        response = send_direct_request(
            ip_address,
            username,
            password,
            f"/cgi-bin/gettemp.cgi?rnd={rnd}"
        )
        
        if not response:
            return None
            
        if 'var temp="' in response:
            temp_str = response.split('var temp="')[1].split('";')[0]
            return float(temp_str)
            
        return None
        
    except Exception as e:
        _LOGGER.error("Error reading temperature: %s", str(e))
        return None

def set_output_state(ip_address, username, password, output_number, state):
    """Set alarm output state."""
    try:
        state_value = "4" if state.lower() == "on" else "1"
        
        params = {
            'Alm_OutUse': state_value,
            'Output_Time': '0',
            'UpSectionName': 'ALARM'
        }
        
        auth = base64.b64encode(f"{username}:{password}".encode()).decode()
        data = '&'.join(f"{k}={quote(str(v))}" for k, v in params.items())
        
        request = (
            f"POST /cgi-bin/writefile.cgi HTTP/1.1\r\n"
            f"Host: {ip_address}\r\n"
            f"Authorization: Basic {auth}\r\n"
            "Content-Type: application/x-www-form-urlencoded\r\n"
            f"Content-Length: {len(data)}\r\n"
            "Connection: close\r\n"
            "\r\n"
            f"{data}"
        )
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            sock.connect((ip_address, 80))
            sock.send(request.encode())
            
            response = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
                
        return "200 OK" in response.decode()
        
    except Exception as e:
        _LOGGER.error("Error setting output state: %s", str(e))
        return False

def parse_js_response(text):
    """Parse JavaScript response from camera."""
    data = {}
    if not text:
        return data
        
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('var ') and '=' in line:
            line = line[4:]
            parts = line.split('=', 1)
            if len(parts) == 2:
                name = parts[0].strip()
                value = parts[1].strip(' ";\'')
                data[name] = value
                
    return data
