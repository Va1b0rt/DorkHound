import re
from time import sleep

from search_engine_parser.core.engines.duckduckgo import Search as DuckDuckGoSearch
from search_engine_parser.core.exceptions import NoResultsOrTrafficError


link_pattern = re.compile(r'(\w*://[\w.-]*.ru)')


def get_url(search_results):
    print(f'Searching Count: {len(search_results)}')
    for result in search_results:
        print(result["links"])
        try:
            url = result["links"]
            url = url.replace("%3A", ":").replace("%2F", "/").replace("%2D", "-")
            pattern = link_pattern.search(url)
            if pattern:
                url = pattern.group(1)
            else:
                continue
            #url = f'https://{url.replace("https//", "").replace("http://", "").split("/")[0]}'

            yield url

        except Exception as e:
            print(f"Error: {e}")


def collect():
    duckduckgosearch = DuckDuckGoSearch()

    with open('dorks.txt', 'r') as file:
        dorks = file.read().splitlines()

    urls_set = set([])

    for num, dork in enumerate(dorks, start=1):
        print(f'{dork=}')

        try:
            search_results = duckduckgosearch.search(dork)
        except NoResultsOrTrafficError:
            sleep(100)
            print(f'No results_3 for {dork}')
            print(f'count: {num} / {len(dorks)}')
            continue

        for url in get_url(search_results):
            urls_set.add(url)

        with open('results', 'w') as file:
            file.write('\n'.join(urls_set))
        print(f'count: {num} / {len(dorks)}')
        sleep(30)


if __name__ == "__main__":
    collect()
