import pandas as pd
import sqlite3
import re

trades = pd.read_csv('data/csv/transactions.csv')
trades['Date'] = pd.to_datetime(trades['Date'])

seasons = pd.read_csv('data/csv/seasons.csv')
seasons['Season_Start'] = pd.to_datetime(seasons['Season_Start'])
seasons['End'] = pd.to_datetime(seasons['End'])
seasons['Offseason_Start'] = pd.to_datetime(seasons['Offseason_Start'])

wins = pd.read_csv('data/csv/regular_season_wins.csv')
wins['Win_Pct'] = wins['W'] / (wins['W'] + wins['L'])
wins = wins[['Season', 'Team', 'Win_Pct']]

# cross join
trades['_'] = 0
seasons['_'] = 0
final = trades.merge(seasons, how='outer', on='_')
final = final[(final['Date']>=final['Offseason_Start'])&(final['Date']<=final['End'])]
final = final[['Date', 'Season', 'Team', 'Acquired', 'Relinquished', 'Notes']]

# cleaning and tagging
final = final.fillna('')
final['Notes'] = final['Notes'].str.replace('wtih', 'with')
final['Notes'] = final['Notes'].str.replace('treade', 'trade')
final['Notes'] = final['Notes'].str.replace('tradee', 'trade')
tagged = (final['Notes'].str.contains('trade with', flags=re.IGNORECASE, regex=True, na=False))&(~final['Notes'].str.contains('rescinded|voided', flags=re.IGNORECASE, regex=True, na=False))
tagged &= ~((final['Date']=='2009-09-29')&(final['Notes'].str.contains('restructuring'))) # these 2 rows are restructuring of a previous trade, so remove the dup
tagged &= ~((final['Date']=='2001-08-17')&(final['Notes'].str.contains('ammended 8/12/01 trade'))) # ammend are dupes
tagged &= ~((final['Date']=='2001-06-28')&(final['Notes'].str.contains('announced trade with Suns to be done 2001-07-18|announced trade with Pistons to be done 2001-07-18', regex=True)))
tagged &= ~((final['Date']=='2019-02-07')&(final['Notes'].str.contains('3-team trade with Bucks, Cavaliers', regex=True)&(final['Team']=='Wizards')))
tagged &= ~((final['Date']=='2016-07-12')&(final['Notes'].str.contains('trade with Grizzlies', regex=True)&(final['Team']=='Pelicans')))
tagged &= ~((final['Date']=='2012-11-13')&(final['Notes'].str.contains('trade with Hornets', regex=True)&(final['Team']=='Pelicans')))
tagged &= ~((final['Date']=='2012-06-20')&(final['Notes'].str.contains('trade with Hornets', regex=True)&(final['Team']=='Pelicans')))
tagged &= ~((final['Date']=='2003-08-05')&(final['Notes'].str.contains('trade with Jazz', regex=True)&(final['Team']=='Kings')&(final['Relinquished'].str.contains('Tom Gugliotta', regex=True))))

final['Tag'] = tagged

multi_team_trades = (final['Notes'].str.contains('-team'))&(final['Tag'])
final['TeamsInvolved'] = 2
final.loc[~final['Tag'], 'TeamsInvolved'] = 0
final.loc[multi_team_trades, 'TeamsInvolved'] = final.loc[multi_team_trades, 'Notes'].str.slice(0, 1)

conn = sqlite3.connect('data/sql/transactions.db')

final.to_sql('trade', conn, index=False)
wins.to_sql('regular_season', conn, index=False)

conn.commit()
conn.close()



# TODO trade partners
# def extract(r):
#     match = re.search('trade with ([A-Za-z0-9]+)(, [A-Za-z0-9]+){2}', r['Notes'])
#     if match:
#             return [m.replace(', ', '') if m is not None else None for m in match.groups()]
#     else:
#             return []

# all_teams = pd.read_sql('SELECT DISTINCT TEAM FROM TRADE', conn)['Team'].tolist()
# all_teams.append('Bobcats')
# all_teams.append('Sonics')

# def extract(r):
#     teams_present = [t for t in all_teams if t in r['Notes']]
#     return teams_present

# df['extracted'] = df.apply(extract, axis=1)
# df = df.explode('extracted')