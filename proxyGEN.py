import requests
import socket
import concurrent.futures
from colorama import Fore, Style, init
import os
import time
import random
import sys
import threading

# Initialize colorama
init(autoreset=True)

# Global configuration
MAX_WORKERS = 15
TIMEOUT = 5
TEST_URL = "http://www.google.com"
PRINT_LOCK = threading.Lock()

# Enhanced Banner
def banner():
    print(Fore.RED + r"""
    ██╗   ██╗██╗██████╗ ██╗   ██╗███████╗
    ██║   ██║██║██╔══██╗██║   ██║██╔════╝
    ██║   ██║██║██████╔╝██║   ██║███████╗
    ╚██╗ ██╔╝██║██╔══██╗██║   ██║╚════██║
     ╚████╔╝ ██║██║  ██║╚██████╔╝███████║
      ╚═══╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
    """ + Style.RESET_ALL)
    print(Fore.CYAN + "Proxy Generator & Validator Tool By Virus Team" + Style.RESET_ALL)
    print(Fore.GREEN + "Updated version 14/4/25" + Style.RESET_ALL)
    print(Fore.WHITE + "Dev: Realchris" + Style.RESET_ALL)
    print("\n")

# Smooth print function
def smooth_print(message, color=Fore.WHITE, delay=0.01):
    with PRINT_LOCK:
        for char in message:
            print(color + char, end='', flush=True)
            time.sleep(delay)
        print(Style.RESET_ALL)

# Validation functions
def validate_socks4(proxy):
    ip, port = proxy.split(':')
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        s.connect((ip, int(port)))
        
        # SOCKS4 connect request
        request = bytearray()
        request.append(0x04)  # SOCKS version 4
        request.append(0x01)  # CONNECT command
        request.append((80 >> 8) & 0xff)
        request.append(80 & 0xff)
        request.extend([127, 0, 0, 1])  # IP for test
        request.append(0x00)  # User ID
        
        s.send(request)
        response = s.recv(8)
        
        if len(response) >= 2 and response[1] == 0x5a:
            return True
    except:
        return False
    finally:
        try:
            s.close()
        except:
            pass
    return False

def validate_socks5(proxy):
    ip, port = proxy.split(':')
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        s.connect((ip, int(port)))
        
        # SOCKS5 handshake
        s.send(bytearray([0x05, 0x01, 0x00]))
        response = s.recv(2)
        
        if response[0] != 0x05 or response[1] != 0x00:
            return False
            
        # SOCKS5 connect request
        request = bytearray()
        request.append(0x05)  # SOCKS version 5
        request.append(0x01)  # CONNECT command
        request.append(0x00)  # Reserved
        request.append(0x01)  # IPv4 address
        request.extend([8, 8, 8, 8])  # Google DNS
        request.append((53 >> 8) & 0xff)  # DNS port
        request.append(53 & 0xff)
        
        s.send(request)
        response = s.recv(10)
        
        if response[1] == 0x00:
            return True
    except:
        return False
    finally:
        try:
            s.close()
        except:
            pass
    return False

def validate_http(proxy):
    try:
        proxies = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        response = requests.get(TEST_URL, proxies=proxies, timeout=TIMEOUT)
        if response.status_code == 200:
            return True
    except:
        return False
    return False

def validate_https(proxy):
    try:
        proxies = {
            'http': f'https://{proxy}',
            'https': f'https://{proxy}'
        }
        response = requests.get(TEST_URL.replace("http://", "https://"), 
                             proxies=proxies, 
                             timeout=TIMEOUT, 
                             verify=False)
        if response.status_code == 200:
            return True
    except:
        return False
    return False

def generate_proxies(proxy_type, count):
    common_ports = {
        'SOCKS4': [1080, 4145, 2525, 8000],
        'SOCKS5': [1080, 9050, 9150, 9999],
        'HTTP': [80, 8080, 3128, 8888],
        'HTTPS': [443, 8443, 4443, 10443]
    }
    proxies = []
    for _ in range(count):
        ip = ".".join(str(random.randint(1, 255)) for _ in range(4))
        port = random.choice(common_ports.get(proxy_type, [8080, 8888]))
        proxies.append(f"{ip}:{port}")
    return proxies

def validate_and_print(proxy, validate_func, proxy_type):
    try:
        start_time = time.time()
        is_valid = validate_func(proxy)
        elapsed = time.time() - start_time
        
        status = f"[VALID] {proxy}" if is_valid else f"[INVALID] {proxy}"
        color = Fore.GREEN if is_valid else Fore.RED
        details = f" ({elapsed:.2f}s)"
        
        with PRINT_LOCK:
            smooth_print(status + details, color)
        
        return proxy if is_valid else None
    except Exception as e:
        with PRINT_LOCK:
            smooth_print(f"[ERROR] {proxy} - {str(e)}", Fore.RED)
        return None

def main():
    banner()
    
    options = [
        "[1] SOCKS4",
        "[2] SOCKS5", 
        "[3] HTTP",
        "[4] HTTPS"
    ]
    
    for option in options:
        smooth_print(option, Fore.CYAN)
    
    try:
        choice = int(input("\nSelect proxy type (1-4): "))
        if choice not in [1, 2, 3, 4]:
            raise ValueError
    except:
        smooth_print("Invalid choice! Please select between 1-4.", Fore.RED)
        return
    
    try:
        count = int(input("Enter number of proxies to generate and validate: "))
        if count <= 0:
            raise ValueError
    except:
        smooth_print("Invalid number! Please enter a positive integer.", Fore.RED)
        return
    
    smooth_print(f"\nGenerating and validating {count} proxies...\n", Fore.YELLOW)
    
    proxy_type = ["SOCKS4", "SOCKS5", "HTTP", "HTTPS"][choice-1]
    validate_func = [validate_socks4, validate_socks5, validate_http, validate_https][choice-1]
    
    proxies = generate_proxies(proxy_type, count)
    valid_proxies = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for proxy in proxies:
            futures.append(
                executor.submit(
                    validate_and_print, 
                    proxy, 
                    validate_func, 
                    proxy_type
                )
            )
            time.sleep(0.05)
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                valid_proxies.append(result)

    if valid_proxies:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"hit_{proxy_type.lower()}_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            for proxy in valid_proxies:
                f.write(f"{proxy}\n")
        
        smooth_print(f"\nValidation complete! Found {len(valid_proxies)} valid {proxy_type} proxies.", Fore.GREEN)
        smooth_print(f"Valid proxies saved to {filename}", Fore.GREEN)
    else:
        smooth_print("\nNo valid proxies found.", Fore.RED)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        smooth_print("\nOperation cancelled by user.", Fore.RED)
        sys.exit(1)
