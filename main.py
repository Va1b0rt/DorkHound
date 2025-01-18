import argparse
import os
import sys

from search_engine_parser.core.engines.duckduckgo import Search as DuckDuckGoSearch

from hound import DorkHound


def parse_args():
    parser = argparse.ArgumentParser(description='Dork Hound.')
    parser.add_argument("-d", "--dorks", help="path to dork file")
    parser.add_argument("-e", "--exclude", help="path to exclude domains file")
    parser.add_argument( "-t", "--delay", help="delay in seconds")
    parser.add_argument("-o", "--output", help="path to output file")
    parser.add_argument("-c", "--clear", help="clear database", action="store_true")
    parser.add_argument("-p", "--proxys", help="path to proxy file")
    parser.parse_args()
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    if args.clear:
        os.remove("dorks.db")
        sys.exit(0)

    hound = DorkHound()

    if args.output and not args.dorks:
        hound.save_domains_to_file(args.output)
        sys.exit(0)

    if not args.dorks:
        print("specify the path to the file with dorks")
        sys.exit(1)

    hound.dorks_file_path = args.dorks

    if args.exclude:
        hound.exclude_domains_file_path = args.exclude

    if args.delay:
        hound.delay = int(args.delay)

    if args.proxys:
        hound.proxies_file_path = args.proxys
        hound.read_proxys_from_file()

    hound.collect()

    if args.output:
        hound.save_domains_to_file(args.output)
        sys.exit(0)