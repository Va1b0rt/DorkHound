import re
from time import sleep

#import requests
#from search_engine_parser.core.engines.bing import Search as BingSearch
#from search_engine_parser.core.engines.google import Search as GoogleSearch
#from search_engine_parser.core.engines.yahoo import Search as YahooSearch
from search_engine_parser.core.engines.duckduckgo import Search as DuckDuckGoSearch

from search_engine_parser.core.exceptions import NoResultsOrTrafficError


#link_pattern = re.compile(r'uddg=(.*\.ru)')
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
    #gsearch = GoogleSearch()
    #yahoo_search = YahooSearch()
    #bsearch = BingSearch()
    duckduckgosearch = DuckDuckGoSearch()
    #yandex_search = YandexSearch()

    with open('wordpress_dorks.txt', 'r') as file:
        dorks = file.read().splitlines()

    urls_set = set([])

    for num, dork in enumerate(dorks, start=1):
        print(f'{dork=}')


        #google_results = gsearch.search(dork)
        #yahoo_search = yahoo_search.search(dork)
        #bsearch = bsearch.search(dork)
        try:
            search_results = duckduckgosearch.search(dork)
        except NoResultsOrTrafficError:
            sleep(100)
            print(f'No results_3 for {dork}')
            print(f'count: {num} / {len(dorks)}')
            continue
        #yandex_search = yandex_search.search(dork, page=999)
        #urls_set.union(get_urls(google_results))
        #urls_set.union(get_urls(yahoo_search))
        #urls_set.union(get_urls(bsearch))
        for url in get_url(search_results):
            urls_set.add(url)

        with open('results1', 'w') as file:
            file.write('\n'.join(urls_set))
        print(f'count: {num} / {len(dorks)}')
        sleep(30)


if __name__ == "__main__":
    collect()
