# DorkHound: A DuckDuckGo Dorking Tool

### Description
DorkHound - will return you a list of domains matching your queries from a file.

Installation

Clone the repository:

`git clone https://github.com/Va1b0rt/DorkHound`

Install dependencies: Install required Python libraries (e.g., requests, BeautifulSoup4) using:

```bash

pip install -r requirements.txt
```

Usage

Prepare a dork list: Create a text file (e.g., dorks.txt) with one dork per line.
Run the script:

```bash

python main.py -d ./dorks.txt -o ./results -e ./exclude_domains.txt
```


To remove the previous result use the command:

```bash

python main.py -c
```

To load the result into a file, use the standalone argument -o:

```bash

python main.py -o ./result
```

Speed: Performance may vary based on the number of dorks, internet connection speed, and DuckDuckGo rate limits.
Accuracy: Search results may contain irrelevant or outdated links.
Usage policy: Adhere to DuckDuckGo's terms of service to avoid abuse.