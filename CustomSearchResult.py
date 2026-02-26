import random

import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote

class CustomSearchResult:
    def __init__(self, results_list):
        self.results = results_list

    def __iter__(self):
        return iter(self.results)


class CustomDDGSearch:
    def __init__(self, verbose: bool = False):
        self.url = "https://html.duckduckgo.com/html/"
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
        ]
        self.base_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        self.verbose = verbose
        self.next_payload = None

    def search(self, query: str, page: int = 1, proxy: str = None):
        proxies = {"http": proxy, "https": proxy} if proxy else None

        headers = self.base_headers.copy()
        headers["User-Agent"] = random.choice(self.user_agents)

        if page == 1:
            data = {"q": query}
        elif self.next_payload:
            data = self.next_payload
        else:
            return CustomSearchResult([])

        try:
            response = requests.post(self.url, headers=headers, data=data, proxies=proxies, timeout=10)

            with open("last_page.html", "w", encoding="utf-8") as f:
                f.write(response.text)

            if response.status_code != 200:
                return CustomSearchResult([])
        except Exception as e:
            if self.verbose:
                print(f"[DEBUG] Мережева помилка під час запиту: {e}")
            return CustomSearchResult([])

        soup = BeautifulSoup(response.text, 'html.parser')
        results = []

        for a_tag in soup.find_all('a', class_='result__url'):
            href = a_tag.get('href', '')
            if not href:
                continue

            if 'uddg=' in href:
                from urllib.parse import unquote
                clean_url = unquote(href.split('uddg=')[1].split('&')[0])
            else:
                clean_url = href

            results.append({"links": clean_url})

        self.next_payload = None
        for form in soup.find_all('form', action='/html/'):
            if form.find('input', value='Next'):
                self.next_payload = {
                    inp.get('name'): inp.get('value')
                    for inp in form.find_all('input', type='hidden')
                    if inp.get('name')
                }
                break

        return CustomSearchResult(results)