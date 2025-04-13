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
MAX_WORKERS = 15  # threads 
TIMEOUT = 5  # Χρόνος αναμονής για connections
TEST_URL = "http://www.google.com"  # url search
PRINT_LOCK = threading.Lock()  

# banner
def banner():
    print(Fore.RED + r"""
    ██╗   ██╗██╗██████╗ ██╗   ██╗███████╗
    ██║   ██║██║██╔══██╗██║   ██║██╔════╝
    ██║   ██║██║██████╔╝██║   ██║███████╗
    ╚██╗ ██╔╝██║██╔══██╗██║   ██║╚════██║
     ╚████╔╝ ██║██║  ██║╚██████╔╝███████║
      ╚═══╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
    """ + Style.RESET_ALL)
    print(Fore.CYAN + r"""
     ____  ____  ___  ____  ____   __   _  _  ____ 
    (  _ \( ___)/ __)(_  _)(  _ \ / _\ ( \/ )(  __)
     )   / )__) \__ \  )(   )   //    \/ \/ \ ) _) 
    (__\_)(____)(___/ (__) (__\_)\_/\_/\_)(_/(____)
    """ + Style.RESET_ALL)
    print(Fore.YELLOW + "Proxy Generator & Validator Tool By Virus Team" + Style.RESET_ALL)
    print(Fore.GREEN + "Smooth Printing Edition by Realchris" + Style.RESET_ALL)
    print("\n")

# Smooth print function
def smooth_print(message, color=Fore.WHITE, delay=0.01):
    with PRINT_LOCK:
        for char in message:
            print(color + char, end='', flush=True)
            time.sleep(delay)
        print(Style.RESET_ALL)

# Validate proxy with smooth printing
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
        
        return is_valid
    except Exception as e:
        with PRINT_LOCK:
            smooth_print(f"[ERROR] {proxy} - {str(e)}", Fore.RED)
        return False

# [Rest of the functions remain the same as previous version...]

# Main function with improved flow
def main():
    banner()
    
    # Display options with smooth printing
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
    
    # Generate proxies
    proxy_type = ["SOCKS4", "SOCKS5", "HTTP", "HTTPS"][choice-1]
    validate_func = [validate_socks4, validate_socks5, validate_http, validate_https][choice-1]
    
    proxies = generate_proxies(proxy_type, count)
    valid_proxies = []
    
    # Process proxies with controlled threading
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
            time.sleep(0.05)  # Small delay between starting threads
        
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                valid_proxies.append(future.result())

    # Save results
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
