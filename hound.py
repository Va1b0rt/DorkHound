import re
from random import choice
from time import sleep
from typing import Any, Generator

from search_engine_parser.core.engines.duckduckgo import Search as DuckDuckGoSearch
from search_engine_parser.core.exceptions import NoResultsOrTrafficError, NoResultsFound
from tqdm import tqdm

from data_controller import DorkDatabase
from CustomSearchResult import CustomDDGSearch


class DorkHound:
    def __init__(self,
                 delay: int = 30):
        self.link_pattern = re.compile(r'://([^/]+)')
        self.dorks_file_path = None
        self.exclude_domains_file_path = None
        self.delay = delay
        self.proxies_file_path = None
        self.proxies = []
        self.verbose = False


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
        if self.verbose:
            print(f"\n[DEBUG] Отримано результатів від парсера: {len(search_results.results)}")

        for result in search_results:
            try:
                url = result.get("links", "")
                if self.verbose:
                    print(f"[DEBUG] Сирий URL: {url}")

                url = url.replace("%3A", ":").replace("%2F", "/").replace("%2D", "-")
                pattern = self.link_pattern.search(url)

                if pattern:
                    extracted_domain = pattern.group(1)
                    if self.verbose:
                        print(f"[DEBUG] Витягнуто домен: {extracted_domain}")
                    yield extracted_domain
                else:
                    if self.verbose:
                        print("[DEBUG] Регексп не знайшов збігів")
                    continue

            except Exception as e:
                if self.verbose:
                    print(f"[DEBUG] Помилка обробки: {e}")

    def collect(self):
        dorks_count = self.dorks_count
        progress = tqdm(enumerate(self.dorks, start=1))

        try:
            for num, dork in progress:
                progress.set_description(desc=f"Processing {num} / {dorks_count}")

                if self.verbose:
                    progress.write(f'{dork=}')

                if self.database.is_dork_processed(dork):
                    continue

                self.collect_pages(dork)
                self.database.add_processed_dork(dork)
                sleep(self.delay)
        except KeyboardInterrupt:
            progress.write("\nОбробка перервана користувачем. Прогрес збережено.")

    def collect_pages(self, dork, start_page=1, ex_count=0):
        search_engine = CustomDDGSearch(verbose=self.verbose)
        _ex_count = ex_count

        if _ex_count >= 5:
            return

        for page in range(start_page, 999):
            proxy = self.proxy if self.proxies else None
            search_results = search_engine.search(dork, page=page, proxy=proxy)

            if not search_results.results:
                break

            for url in self.get_url(search_results):
                self.database.add_entry(url, dork)

            sleep(self.delay)