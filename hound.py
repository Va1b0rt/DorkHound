import re
from random import choice
from time import sleep
from typing import Any, Generator

from search_engine_parser.core.engines.duckduckgo import Search as DuckDuckGoSearch
from search_engine_parser.core.exceptions import NoResultsOrTrafficError, NoResultsFound
from tqdm import tqdm

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
        #print(f'Searching Count: {len(search_results)}')
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
                pass
                #print(f"Error: {e}")

    def collect(self):
        dorks_count = self.dorks_count

        for num, dork in tqdm(enumerate(self.dorks, start=1)):
            tqdm.write(f'{dork=}')

            self.collect_pages(dork)

            tqdm.write(f'count: {num} / {dorks_count}')
            sleep(self.delay)

    def collect_pages(self, dork, start_page=1, ex_count=0):
        search_engine = DuckDuckGoSearch()
        _ex_count = ex_count

        if _ex_count >= 5:
            return

        for page in range(start_page, 999):
            try:
                proxy = self.proxy if self.proxies else None
                search_results = search_engine.search(dork, page=page, proxy=proxy)
                if not search_results.results:
                    break

                for url in self.get_url(search_results):
                    #tqdm.write(f'{url=}')
                    self.database.add_entry(url, dork)

            except NoResultsFound:
                #tqdm.write(f'NoResultsFound for {dork}')
                break
            except NoResultsOrTrafficError as e:
                #print(e)
                sleep(5)
                _ex_count += 1
                self.collect_pages(dork, page, _ex_count)
            except Exception as e:
                #tqdm.write(f'Error: {e}')
                sleep(self.delay)
                _ex_count += 1
                self.collect_pages(dork, page, _ex_count)