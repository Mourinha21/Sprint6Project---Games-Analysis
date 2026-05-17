import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats as st

games = games = pd.read_csv('games.csv')

colunas = games.columns
contador = 0
colunas_min = []
for i in colunas:
    colunas_min.append(colunas[contador].lower())
    contador += 1


games.columns = colunas_min

games['name'] = games['name'].fillna('???')
games['year_of_release'] = games['year_of_release'].fillna(1000.0)
games['year_of_release'] = games['year_of_release'].astype('int')
games['genre'] = games['genre'].fillna('???')
games['rating'] = games['rating'].fillna('???')

games.drop(games[games['year_of_release'] == 1000].index, axis=0, inplace=True)

mean_genres = games.groupby('genre')['critic_score'].mean().to_dict()

games['critic_score'] = games.apply(
    lambda row: mean_genres[row['genre']]
    if pd.isna(row['critic_score'])
    else row['critic_score'],
    axis=1
)

games['user_score'] = games['user_score'].replace('tbd', '6.9')
games['user_score'] = pd.to_numeric(games['user_score'])

mean_genres = games.groupby('genre')['user_score'].mean().to_dict()

games['user_score'] = games.apply(
    lambda row: mean_genres[row['genre']]
    if pd.isna(row['user_score'])
    else row['user_score'],
    axis=1
)

games.drop_duplicates(inplace=True)
games = games.reset_index(drop=True)

games['na_sales'] = pd.to_numeric(games['na_sales'])
games['eu_sales'] = pd.to_numeric(games['eu_sales'])
games['jp_sales'] = pd.to_numeric(games['jp_sales'])
games['other_sales'] = pd.to_numeric(games['other_sales'])

games['total_sales'] = 0.0

for game in range(len(games)):
    games['total_sales'][game] = games['na_sales'][game] + \
        games['eu_sales'][game]
    + games['jp_sales'][game] + games['other_sales'][game]

games_ano = games.groupby('year_of_release')[
    'total_sales'].count().sort_values().reset_index()
ga_rename = {}
games_ano = games_ano.rename(columns={'total_sales': 'number_of_games'})

ga_t = games_ano.T
ga_t.pop(0)

games_ano = ga_t.T
games_ano.sort_values('year_of_release')

plt.figure(figsize=(16, 9))
plt.bar(games_ano['year_of_release'],
        games_ano['number_of_games'], picker=True)
plt.xlabel('Year of Release')
plt.ylabel('Number of Games Sold (Millions)')
plt.title('Number of Games Sold By Year')

sales_plat = games.groupby(['platform', 'year_of_release'])['total_sales'].sum(
).reset_index().sort_values('total_sales', ascending=False)

sales_plat_sorted = sales_plat.sort_values(
    by=['platform', 'year_of_release']
)

plt.figure(figsize=(16, 9))
for platform, df in sales_plat_sorted.groupby('platform'):
    plt.plot(
        df['year_of_release'],
        df['total_sales'],
        marker='o',
        label=platform
    )
plt.xlabel('Year of Release')
plt.ylabel('Total Sales')
plt.title('Total Sales per Platform Over Time')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

first_decade_sales = sales_plat.query(
    'year_of_release >= 2006 & year_of_release < 2010')
first_decade_sales.sort_values(
    by=['year_of_release', 'total_sales'], inplace=True)

f, ax = plt.subplots(figsize=(9,6))


plt.title('Total Sales by Year and Platform - Millions')
ax.set(xlabel='Year of Release', ylabel='Platform')
sns.heatmap(first_decade_sales, annot=True, fmt='.1f', linewidths=.5, ax=ax)

top_plat = games[(games['platform'] == 'Wii') | (games['platform'] == 'DS') | (games['platform'] == 'PS3')
                 | (games['platform'] == 'PS2') | (games['platform'] == 'X360')]

plt.figure(figsize=(12, 5))
sns.boxplot(data=top_plat, x='platform',
            y='total_sales', palette='magma')
plt.xlabel('Plataforms')
plt.ylabel('Average Sales - Millions')
plt.title('Average Sales on main Platforms')
plt.yscale('log')
ticks = [0.01, 0.1, 1, 10, 100]
plt.yticks(ticks, [str(t) for t in ticks])
plt.show()

media_plat = games.groupby('platform')['total_sales'].mean(
).reset_index().sort_values(by='total_sales', ascending=False)

plt.figure(figsize=(12, 6))
plt.scatter(data=games, x='user_score', y='total_sales')
plt.title(
    'Total Sales Distribution By User Scores', fontsize=16)
plt.ylabel('Global Sales (in millions)', fontsize=12)
plt.xlabel('User Score', fontsize=12)
plt.tight_layout()
plt.show()

re2_sales = games.query('name == "Resident Evil 2"')

plt.figure(figsize=(16, 9))
plt.bar(x='platform', height='total_sales', data=re2_sales)
plt.title('Comparison Between Platforms on Resident Evil 2  Sales', fontsize=16)
plt.ylabel('Total Sales (in millions)', fontsize=12)
plt.xlabel('Platform', fontsize=12)
plt.show()

profit_genre = games.groupby('genre')['total_sales'].sum(
).reset_index().sort_values(by='total_sales', ascending=False)

na_sales = games.groupby('genre')['na_sales'].sum(
).reset_index().sort_values(by='na_sales', ascending=False)
na_sales.head()

eu_sales = games.groupby('genre')['eu_sales'].sum(
).reset_index().sort_values(by='eu_sales', ascending=False)
eu_sales.head()

jp_sales = games.groupby('genre')['jp_sales'].sum(
).reset_index().sort_values(by='jp_sales', ascending=False)
jp_sales.head()

esrb_na = games.groupby('rating')['na_sales'].sum(
).reset_index().sort_values(by='na_sales', ascending=False)
esrb_na

esrb_eu = games.groupby('rating')['eu_sales'].sum(
).reset_index().sort_values(by='eu_sales', ascending=False)
esrb_eu

esrb_jp = games.groupby('rating')['jp_sales'].sum(
).reset_index().sort_values(by='jp_sales', ascending=False)
esrb_jp

xone_users_score = games.query('platform == "XOne"')
pc_users_score = games.query('platform == "PC"')

alpha = 0.05
results = st.ttest_ind(
    xone_users_score['user_score'], pc_users_score['user_score'])
print('p-value: ', results.pvalue)

if results.pvalue < alpha: 
    print("We reject the null hypothesis")
else:
    print("We can't reject the null hypothesis")

print("The p-value here tells that there is a difference between users'"
      " rating the same game on different platforms (XONE and PC)")

consoles_means = [xone_users_score['user_score'].mean(), pc_users_score['user_score'].mean()]

fig, ax = plt.subplots(figsize=(8,8))

bars = ax.bar(
    ['Xbox One', 'PC'],
    consoles_means,
    color=['green', 'blue']
)

ax.bar_label(bars, fmt='%.2f', padding=3)

ax.set_title("Average User Scores for Xbox One and PC Games")
ax.set_ylim(6.5, 7.10)

plt.show()

user_score_action = games.query('genre == "Action"')
user_score_sports = games.query('genre == "Sports"')

alpha = 0.05
results = st.ttest_ind(
    user_score_action['user_score'], user_score_sports['user_score'])
print('p-value: ', results.pvalue)

if results.pvalue < alpha:
    print("We reject the null hypothesis")
else:
    print("We can't reject the null hypothesis")

print('The p-value tells that')

act_sports_means = [user_score_action['user_score'].mean(), user_score_sports['user_score'].mean()]

fig, ax = plt.subplots(figsize=(8,8))

bars = ax.bar(
    ['Action', 'Sports'],
    act_sports_means,
    color=['orange', 'turquoise']
)

ax.bar_label(bars, fmt='%.2f', padding=3)

ax.set_title("Average User Scores for Action and Sports Games")
ax.set_ylim(6.85, 7.05)

plt.show()