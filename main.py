import pandas as pd
import json
import requests
import requests.auth
from bs4 import BeautifulSoup

#######################
# Get API credentials #
#######################

keys = pd.read_csv('keys.csv')
auth = requests.auth.HTTPBasicAuth(keys['PUBLIC_KEY'][0], keys['SECRET_KEY'][0])
data = {
    'grant_type': 'password',
    'username': keys['UserName'],
    'password': keys['RedditPW'][0]
}
headers = {'User-Agent': 'MyAPI/0.0.1'}
auth_response = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=data, headers=headers)
headers['Authorization'] = f"bearer {auth_response.json()['access_token']}"

##################################
# Gather most popular subreddits #
##################################

top_subreddits_url = 'https://www.reddit.com/best/communities/{}/'

# Each page is 250 subreddits
pages = 20

# Gets subreddit names
subreddits = [
    subreddit.text.strip()
    for i
    in range(pages)
    for subreddit
    in BeautifulSoup(
        requests.get(
            top_subreddits_url.format(i+1)).content,
        'html.parser'
    ).find_all(
        name='a',
        class_='m-0 font-bold text-12 text-current truncate max-w-[11rem]'
    )]

#####################
# Search Reddit API #
#####################

website = 'https://oauth.reddit.com/'

fields = ['data.subreddit_name_prefixed', 'data.id', 'data.title', 'data.ups', 'data.score', 'data.created_utc']
dtypes = ['object', 'object', 'object', 'int64', 'int64', 'int64']

posts = pd.DataFrame(columns=fields).astype(dict(zip(fields, dtypes)))

for subreddit in subreddits:
    subreddit_top = requests.get(website+subreddit+"/top/?t=all", params={'limit': 100}, headers=headers).json()
    top_100_posts = pd.json_normalize(data=subreddit_top['data'], record_path='children')[fields]
    posts = pd.concat([posts, top_100_posts])
