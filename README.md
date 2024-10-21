# DorkHound: A DuckDuckGo Dorking Tool

### Description
DorkHound is a Python script designed to automate the process of searching for specific information using a list of dorks (search terms) on the DuckDuckGo search engine. It parses the search results and saves the extracted links to a specified file.

Installation

Clone the repository:
`Bash 
git clone https://github.com/Va1b0rt/DorkHound`

Install dependencies: Install required Python libraries (e.g., requests, BeautifulSoup4) using:
`Bash
pip install -r requirements.txt`

Usage

Prepare a dork list: Create a text file (e.g., dorks.txt) with one dork per line.
Run the script:
Bash
python dorkhound.py

dorks.txt - list dorks
 
Project Structure

dorkhound.py: Main script file
dorks.txt: Sample dork list file
requirements.txt: List of required Python libraries
README.md: This file
How it works

Reads the dork list from the specified file.
For each dork:
Performs a DuckDuckGo search.
Parses the results to extract links.
Writes the extracted links to the output file.
Limitations

Speed: Performance may vary based on the number of dorks, internet connection speed, and DuckDuckGo rate limits.
Accuracy: Search results may contain irrelevant or outdated links.
Usage policy: Adhere to DuckDuckGo's terms of service to avoid abuse.