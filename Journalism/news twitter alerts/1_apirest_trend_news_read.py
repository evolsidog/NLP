import tweepy
import yaml
import json
from datetime import datetime as dt, timedelta

TOP_TRENDING_TOPICS = 10

# Credentials and connectors
with open('credentials.yaml') as f:
    twitter_credentials = yaml.load(f, Loader=yaml.loader.SafeLoader)

api_key = twitter_credentials['API Key']
api_key_secret = twitter_credentials['Api Key Secret']
bearer_token = twitter_credentials['Bearer Token']

# v1.1 API
auth = tweepy.OAuth2BearerHandler(bearer_token)
api = tweepy.API(auth)

# v2.0 API
client = tweepy.Client(bearer_token=bearer_token)

# 1) Get trending topics (10 for this example)
# https://developer.twitter.com/en/docs/twitter-api/v1/trends/locations-with-trending-topics/api-reference/get-trends-available
public_tweets = api.get_place_trends(id=23424950) # spain
print(f"Number of trending topics: {len(public_tweets[0]['trends'])}")

for trend in public_tweets[0]['trends']:
    if not isinstance(trend['tweet_volume'], int):
        trend['tweet_volume'] = 0

sorted_trends = sorted(public_tweets[0]['trends'], key=lambda d: d['tweet_volume'], reverse=True)

top_trends = sorted_trends[:TOP_TRENDING_TOPICS]
# remove last and add "pechotes" social new
top_trends = top_trends[:-1]
top_trends.append(sorted_trends[36])

# 2) Get relevant tweets for top trending topics sorted by 'relevancy'
trend_tweets = {}
for trend in top_trends:
    query = trend['name'] + ' is:verified -is:retweet lang:es' # min_faves, min_retweets or place_country
    print(query)
    max_results = 10

    dtformat = '%Y-%m-%dT%H:%M:%SZ'
    start_time = (dt.utcnow() - timedelta(hours=24)).strftime(dtformat)
    print(start_time)

    # min_faves, min_retweets or place_country are not availables in my current subscription

    tweets = client.search_recent_tweets(query=query,
                                        tweet_fields=['created_at', 'public_metrics', 'entities', 'context_annotations'],
                                        user_fields=['username', 'name'],
                                        expansions=['entities.mentions.username', 'author_id'],
                                        max_results=max_results,
                                        sort_order='relevancy',
                                        start_time=start_time)
    trend_tweets[trend['name']] = tweets

# 3) Get tweet information
trends_info = {}
for trend_name, tweets in trend_tweets.items():
    tweets_trend_info = []
    for i in range(len(tweets.data)):
        tweet_info = {}
        
        tweet_data = tweets.data[i]
        # sometimes we don't have information about user. We associate data and user infomration by author_id
        tweet_user_info = [user for user in tweets.includes['users'] if user.id == tweet_data.author_id][0]

        tweet_info['text'] = tweet_data.text
        tweet_info['creation_date'] = tweet_data.created_at.strftime(dtformat)
        tweet_info['url'] = f'https://twitter.com/twitter/statuses/{tweet_data.id}'
        tweet_info['metrics'] = tweet_data.public_metrics
        tweet_info['username'] = tweet_user_info.username
        tweet_info['name'] = tweet_user_info.name
        tweet_info['ner_entities'] = [entity['normalized_text'] for entity in tweet_data.entities['annotations']] if tweet_data.entities and len(tweet_data.entities) > 0 and 'annotations' in tweet_data.entities else []
        tweet_info['context_annotations'] = [annotation['entity']['name'] for annotation in tweet_data.context_annotations] if tweet_data.context_annotations and len(tweet_data.context_annotations) > 0 else []

        tweets_trend_info.append(tweet_info)
    
    # TODO generate word cloud based in 'ner_entities' and 'context_annotations'
    trends_info[trend_name] = tweets_trend_info

    with open('tweets_info.json', 'w') as f:
        json.dump(trends_info, f)

print("FIN")



