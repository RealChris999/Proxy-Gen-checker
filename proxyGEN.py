import requests
import socket
import concurrent.futures
from colorama import Fore, Style, init
import os
import time
import random
import sys

# Initialize colorama
init(autoreset=True)

# Banner
def banner():
    print(Fore.CYAN + r"""
     ____  ____  ___  ____  ____   __   _  _  ____ 
    (  _ \( ___)/ __)(_  _)(  _ \ / _\ ( \/ )(  __)
     )   / )__) \__ \  )(   )   //    \/ \/ \ ) _) 
    (__\_)(____)(___/ (__) (__\_)\_/\_/\_)(_/(____)
    """ + Style.RESET_ALL)
    print(Fore.YELLOW + "Proxy Generator & Validator Tool" + Style.RESET_ALL)
    print(Fore.YELLOW + "Created by: RealChris" + Style.RESET_ALL)
    print("\n")

# Validate SOCKS4 proxy
def validate_socks4(proxy):
    ip, port = proxy.split(':')
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((ip, int(port)))
        
        # SOCKS4 connect request
        request = bytearray()
        request.append(0x04)  # SOCKS version 4
        request.append(0x01)  # CONNECT command
        
        # Port in network byte order
        request.append((int(port) >> 8) & 0xff)
        request.append(int(port) & 0xff)
        
        # IP address
        for part in ip.split('.'):
            request.append(int(part))
            
        # User ID (empty)
        request.append(0x00)
        
        s.send(request)
        response = s.recv(8)
        
        if len(response) >= 8 and response[1] == 0x5a:
            return True
    except:
        pass
    finally:
        s.close()
    return False

# Validate SOCKS5 proxy
def validate_socks5(proxy):
    ip, port = proxy.split(':')
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
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
        
        # Destination address (dummy address for testing)
        request.append(0x03)  # Domain name
        request.append(len("example.com"))
        request.extend("example.com".encode())
        request.append((80 >> 8) & 0xff)
        request.append(80 & 0xff)
        
        s.send(request)
        response = s.recv(10)
        
        if response[1] == 0x00:
            return True
    except:
        pass
    finally:
        s.close()
    return False

# Validate HTTP proxy
def validate_http(proxy):
    try:
        proxies = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

# Validate HTTPS proxy
def validate_https(proxy):
    try:
        proxies = {
            'http': f'https://{proxy}',
            'https': f'https://{proxy}'
        }
        response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=10, verify=False)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

# Generate random proxies
def generate_proxies(proxy_type, count):
    proxies = []
    for _ in range(count):
        ip = ".".join(str(random.randint(1, 255)) for _ in range(4))
        port = random.randint(1000, 9999)
        proxies.append(f"{ip}:{port}")
    return proxies

# Main function
def main():
    banner()
    
    print(Fore.GREEN + "[1] SOCKS4")
    print(Fore.GREEN + "[2] SOCKS5")
    print(Fore.GREEN + "[3] HTTP")
    print(Fore.GREEN + "[4] HTTPS" + Style.RESET_ALL)
    
    try:
        choice = int(input("\nSelect proxy type (1-4): "))
        if choice not in [1, 2, 3, 4]:
            raise ValueError
    except:
        print(Fore.RED + "Invalid choice! Please select between 1-4." + Style.RESET_ALL)
        return
    
    try:
        count = int(input("Enter number of proxies to generate and validate: "))
        if count <= 0:
            raise ValueError
    except:
        print(Fore.RED + "Invalid number! Please enter a positive integer." + Style.RESET_ALL)
        return
    
    print("\n" + Fore.YELLOW + f"Generating and validating {count} proxies..." + Style.RESET_ALL)
    
    # Generate proxies
    proxy_type = ""
    if choice == 1:
        proxy_type = "SOCKS4"
        proxies = generate_proxies(proxy_type, count)
        validate_func = validate_socks4
    elif choice == 2:
        proxy_type = "SOCKS5"
        proxies = generate_proxies(proxy_type, count)
        validate_func = validate_socks5
    elif choice == 3:
        proxy_type = "HTTP"
        proxies = generate_proxies(proxy_type, count)
        validate_func = validate_http
    elif choice == 4:
        proxy_type = "HTTPS"
        proxies = generate_proxies(proxy_type, count)
        validate_func = validate_https
    
    # Validate proxies
    valid_proxies = []
    invalid_proxies = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        future_to_proxy = {executor.submit(validate_func, proxy): proxy for proxy in proxies}
        for future in concurrent.futures.as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            try:
                is_valid = future.result()
                if is_valid:
                    print(Fore.GREEN + f"[VALID] {proxy}" + Style.RESET_ALL)
                    valid_proxies.append(proxy)
                else:
                    print(Fore.RED + f"[INVALID] {proxy}" + Style.RESET_ALL)
                    invalid_proxies.append(proxy)
            except Exception as e:
                print(Fore.RED + f"[ERROR] {proxy} - {str(e)}" + Style.RESET_ALL)
                invalid_proxies.append(proxy)
    
    # Save results
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"hit_{proxy_type.lower()}_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        for proxy in valid_proxies:
            f.write(f"{proxy}\n")
    
    print("\n" + Fore.GREEN + f"Validation complete! Found {len(valid_proxies)} valid {proxy_type} proxies." + Style.RESET_ALL)
    print(Fore.GREEN + f"Valid proxies saved to {filename}" + Style.RESET_ALL)
    
    # Option to show stats
    show_stats = input("\nShow statistics? (y/n): ").lower()
    if show_stats == 'y':
        print("\n" + Fore.CYAN + "=== STATISTICS ===" + Style.RESET_ALL)
        print(Fore.GREEN + f"Valid proxies: {len(valid_proxies)}" + Style.RESET_ALL)
        print(Fore.RED + f"Invalid proxies: {len(invalid_proxies)}" + Style.RESET_ALL)
        print(Fore.YELLOW + f"Success rate: {len(valid_proxies)/count*100:.2f}%" + Style.RESET_ALL)
    
    # Option to retry
    retry = input("\nDo you want to run again? (y/n): ").lower()
    if retry == 'y':
        main()
    else:
        print(Fore.CYAN + "\nThank you for using the Proxy Generator & Validator Tool!" + Style.RESET_ALL)
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\nOperation cancelled by user." + Style.RESET_ALL)
        sys.exit(1)
