import requests
from bs4 import BeautifulSoup
from pathlib import Path
from teams import all_teams

def download_team_htmls(team):
    print('team:', team)
    prefix = 'https://www.prosportstransactions.com/basketball/Search/'
    begin_url = f'SearchResults.php?Player=&Team={team}&BeginDate=2000-01-01&EndDate=&PlayerMovementChkBx=yes&Submit=Search'
    res = requests.get(prefix+begin_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    urls = [prefix+begin_url]
    urls.extend([prefix+a['href'] for a in soup.find_all('a') if 'SearchResults.php' in a['href']])
    urls.pop()
    idx = 0
    Path(f'data/html/{team}').mkdir(parents=True, exist_ok=True)
    for url in urls:
        download_html(url, team, idx)
        idx += 1
        

def download_html(url, team, idx):
    res = requests.get(url)
    fname = f'data/html/{team}/{idx}.html'
    if not Path(fname).is_file():
        with open(fname, 'w') as f:
            f.write(res.text)

def download_htmls(all_teams):
    for team in all_teams:
        download_team_htmls(team)

if __name__ == '__main__':
    download_htmls(all_teams)