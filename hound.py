import re
from random import choice
from time import sleep
from typing import Any, Generator

from search_engine_parser.core.engines.duckduckgo import Search as DuckDuckGoSearch
from search_engine_parser.core.exceptions import NoResultsOrTrafficError

from data_controller import DorkDatabase


class DorkHound:
    def __init__(self,
                 delay: int = 30):
        self.link_pattern = re.compile(r'://([A-zА-я.\d]*)/')
        self.dorks_file_path = None
        self.exclude_domains_file_path = None
        self.delay = delay
        self.proxies_file_path = None
        self.proxies = []

        if self.proxies_file_path:
            self.read_proxys_from_file()

        self.database = DorkDatabase()

    @property
    def dorks(self) -> Generator[str, Any, None]:
        with open(self.dorks_file_path, 'r') as f:
            for line in f:
                if not line.strip():
                    continue

                yield line.strip()

    @property
    def dorks_count(self) -> int:
        count = 0
        with open(self.dorks_file_path, 'r') as f:
            for line in f:
                if line.strip():
                    count += 1
        return count

    @property
    def exclude_domains(self) -> Generator[str, Any, None]:
        with open(self.exclude_domains_file_path, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                yield line.strip()

    @property
    def proxy(self) -> str:
        return choice(self.proxies)

    def read_proxys_from_file(self):
        with open(self.proxies_file_path, 'r') as f:
            for line in f:
                self.proxies.append(line.strip())

    def save_domains_to_file(self, file_path: str):
        domains = self.database.get_all_entries()
        try:
            with open(file_path, 'a') as f:
                for domain in domains:
                    f.write(f"{domain.domain}\n")
        except IOError:
            raise

    def get_url(self, search_results):
        print(f'Searching Count: {len(search_results)}')
        for result in search_results:
            try:
                url = result["links"]
                url = url.replace("%3A", ":").replace("%2F", "/").replace("%2D", "-")
                pattern = self.link_pattern.search(url)
                if pattern:
                    url = pattern.group(1)
                else:
                    continue
                # url = f'https://{url.replace("https//", "").replace("http://", "").split("/")[0]}'

                yield url

            except Exception as e:
                print(f"Error: {e}")

    def collect(self):
        dorks_count = self.dorks_count

        for num, dork in enumerate(self.dorks, start=1):
            print(f'{dork=}')

            self.collect_pages(dork)

            print(f'count: {num} / {dorks_count}')
            sleep(self.delay)

    def collect_pages(self, dork):
        search_engine = DuckDuckGoSearch()

        try:
            for page in range(1, 999):
                proxy = self.proxy if self.proxies else None
                search_results = search_engine.search(dork, page=page, proxy=proxy)
                if not search_results.results:
                    break

                for url in self.get_url(search_results):
                    self.database.add_entry(url, dork)

        except NoResultsOrTrafficError:
            sleep(self.delay)
            print(f'No results_3 for {dork}')
            return
        except Exception as e:
            print(f'Error: {e}')
            sleep(self.delay)
            self.collect_pages(dork)