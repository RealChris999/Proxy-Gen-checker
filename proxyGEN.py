import requests
import socket
import concurrent.futures
from colorama import Fore, Style, init
import time
import random
import sys
import threading

# Initialize colorama
init(autoreset=True)

# Global configuration
MAX_WORKERS = 10  # Μειώσαμε τα threads για σταθερότητα
TIMEOUT = 5
TEST_URL = "http://www.google.com"
PRINT_LOCK = threading.Lock()
PROGRESS_INTERVAL = 10  # Εμφάνιση progress κάθε 10 proxies

# Enhanced Banner
def banner():
    print(Fore.RED + r"""
    ███████╗██╗   ██╗██████╗ ███████╗
    ██╔════╝██║   ██║██╔══██╗██╔════╝
    █████╗  ██║   ██║██████╔╝███████╗
    ██╔══╝  ██║   ██║██╔══██╗╚════██║
    ██║     ╚██████╔╝██║  ██║███████║
    ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝
    """ + Style.RESET_ALL)
    print(Fore.CYAN + "Ultimate Proxy Tool" + Style.RESET_ALL)
    print(Fore.YELLOW + "VIP Edition - No Lag" + Style.RESET_ALL)
    print(Fore.WHITE + "Dev: Realchris | Updated: 14/4/25" + Style.RESET_ALL)
    print("\n")

# Enhanced print function με δυνατότητα γρήγορης εκτύπωσης
def smooth_print(message, color=Fore.WHITE, delay=0.005, immediate=False):
    with PRINT_LOCK:
        if immediate:
            print(color + message + Style.RESET_ALL, flush=True)
        else:
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
        
        request = bytearray()
        request.append(0x04)  # SOCKS4
        request.append(0x01)  # CONNECT
        request.append((80 >> 8) & 0xff)
        request.append(80 & 0xff)
        request.extend([127, 0, 0, 1])  # Test IP
        request.append(0x00)  # User ID
        
        s.send(request)
        response = s.recv(8)
        return len(response) >= 2 and response[1] == 0x5a
    except:
        return False
    finally:
        try: s.close()
        except: pass

def validate_socks5(proxy):
    ip, port = proxy.split(':')
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        s.connect((ip, int(port)))
        
        # Handshake
        s.send(bytearray([0x05, 0x01, 0x00]))
        if s.recv(2) != bytearray([0x05, 0x00]):
            return False
            
        # Connect request
        request = bytearray([0x05, 0x01, 0x00, 0x01])  # IPv4
        request.extend([8, 8, 8, 8])  # Google DNS
        request.extend([0x00, 0x35])  # Port 53
        s.send(request)
        return s.recv(10)[1] == 0x00
    except:
        return False
    finally:
        try: s.close()
        except: pass

def validate_http(proxy):
    try:
        proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
        response = requests.get(TEST_URL, proxies=proxies, timeout=TIMEOUT)
        return response.status_code == 200
    except:
        return False

def validate_https(proxy):
    try:
        proxies = {'http': f'https://{proxy}', 'https': f'https://{proxy}'}
        response = requests.get(TEST_URL, proxies=proxies, timeout=TIMEOUT, verify=False)
        return response.status_code == 200
    except:
        return False

def generate_proxies(proxy_type, count):
    ports = {
        'SOCKS4': [1080, 4145, 2525, 8000],
        'SOCKS5': [1080, 9050, 9150, 9999],
        'HTTP': [80, 8080, 3128, 8888],
        'HTTPS': [443, 8443, 4443, 10443]
    }
    return [f"{'.'.join(str(random.randint(1,255)) for _ in range(4))}:{random.choice(ports[proxy_type])}" 
            for _ in range(count)]

def main():
    banner()
    
    options = ["[1] SOCKS4", "[2] SOCKS5", "[3] HTTP", "[4] HTTPS"]
    for opt in options:
        smooth_print(opt, Fore.CYAN)
    
    try:
        choice = int(input("\nSelect proxy type (1-4): "))
        if choice not in [1,2,3,4]:
            raise ValueError
        count = int(input("Enter number of proxies: "))
        if count <= 0:
            raise ValueError
    except:
        smooth_print("Invalid input!", Fore.RED)
        return
    
    proxy_type = ["SOCKS4", "SOCKS5", "HTTP", "HTTPS"][choice-1]
    validate_func = [validate_socks4, validate_socks5, validate_http, validate_https][choice-1]
    
    smooth_print(f"\nGenerating {count} {proxy_type} proxies...", Fore.YELLOW, immediate=True)
    proxies = generate_proxies(proxy_type, count)
    
    smooth_print(f"Validating proxies (0/{count})...", Fore.YELLOW, immediate=True)
    valid_proxies = []
    processed = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(validate_func, proxy): proxy for proxy in proxies}
        
        for future in concurrent.futures.as_completed(futures):
            proxy = futures[future]
            processed += 1
            
            try:
                if future.result():
                    smooth_print(f"[VALID] {proxy}", Fore.GREEN)
                    valid_proxies.append(proxy)
                else:
                    smooth_print(f"[INVALID] {proxy}", Fore.RED)
            except:
                smooth_print(f"[ERROR] {proxy}", Fore.RED)
            
            if processed % PROGRESS_INTERVAL == 0 or processed == count:
                smooth_print(f"\nProgress: {processed}/{count} | Valid: {len(valid_proxies)}", 
                           Fore.YELLOW, immediate=True)
    
    if valid_proxies:
        filename = f"hit_{proxy_type.lower()}_{time.strftime('%Y%m%d-%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write("\n".join(valid_proxies))
        smooth_print(f"\nSuccess! Saved {len(valid_proxies)} proxies to {filename}", Fore.GREEN)
    else:
        smooth_print("\nNo valid proxies found.", Fore.RED)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        smooth_print("\nOperation cancelled", Fore.RED)
        sys.exit(1)
