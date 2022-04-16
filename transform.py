import pandas as pd
from bs4 import BeautifulSoup
import os
from teams import all_teams

def html_to_df(fname):
    with open(f'data/html/{fname}', 'r') as f:
        data = f.read()
    soup = BeautifulSoup(data, 'html.parser')
    data = []
    rows = soup.find('table').find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append(cols)
    df = pd.DataFrame.from_records(data[1:], columns=data[0])
    return df

def transform_team(team):
    print('team:', team)
    files = os.listdir(f'data/html/{team}')
    dfs = [html_to_df(f'{team}/{f}') for f in files]
    final = pd.concat(dfs)
    if team == 'Bobcats':
        # Hornets are treated as the New Hornets,
        # founded as Charlotte Bobcats in 2004 and renamed to Hornets in 2014.
        final['Team'] = 'Hornets'
    if team == 'Pelicans':
        # Pelicans were the Old Hornets (Charlotte-NO-OKC-NO) before 2013.
        # So prior to 2013 the "Team" field is "Hornets."
        # To prevent confusing the Old Hornets and the New Hornets,
        # rename "Hornets" to "Pelicans" for the Old Hornets.
        final['Team'] = 'Pelicans'
    if team == 'Hornets':
        # This includes both the Old Hornets and Old Hornets.
        # Hornets are treated as the New Hornets,
        # so only keep the data of the New Hornets, after 2013 when
        # Charlotte Bobcats are renamed to Hornets.
        final = final[final['Date']>'2014-01-01']
    if team == 'Thunder':
        # Prior to 2009 the "Team" field is "Sonics".
        # For the sake of consistency, rename "Sonics" to "Thunder".
        final['Team'] = 'Thunder'
    return final

def transform_all():
    dfs = [transform_team(team) for team in all_teams]
    final = pd.concat(dfs)
    final['Acquired'] = final['Acquired'].str.replace('•', '.')
    final['Relinquished'] = final['Relinquished'].str.replace('•', '.')
    final.to_csv(f'data/csv/transactions.csv', index=False)


if __name__ == '__main__':
    transform_all()
