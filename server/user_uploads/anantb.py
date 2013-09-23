import operator
import os

from twitter_pb2 import *
from json import loads
from collections import defaultdict

tweets = Tweets()
with file('twitter.pb', 'r') as f:
  tweets.ParseFromString(f.read())

count_delete = 0
count_reply_to = 0

uid_count_all = defaultdict(int)
uid_count_not_deleted = defaultdict(int)
place_count = defaultdict(dict)

for tweet in tweets.tweets:
  if(tweet.is_delete):
    count_delete += 1

  if(tweet.insert.reply_to):
    count_reply_to += 1

  if(tweet.is_delete):
    uid_count_all[tweet.delete.uid] += 1
  else:
    uid_count_all[tweet.insert.uid] += 1
    uid_count_not_deleted[tweet.insert.uid] += 1

  if(not tweet.is_delete and tweet.insert.place.url):
    if ('count' in place_count[tweet.insert.place.id]):
      place_count[tweet.insert.place.id]['count'] += 1
      place_count[tweet.insert.place.id]['name'] = tweet.insert.place.name
    else:
      place_count[tweet.insert.place.id]['count'] = 1
      place_count[tweet.insert.place.id]['name'] = tweet.insert.place.name


sorted_uid_count_all = sorted(uid_count_all.iteritems(), key=operator.itemgetter(1), reverse=True)
sorted_uid_count_not_deleted = sorted(uid_count_not_deleted.iteritems(), key=operator.itemgetter(1), reverse=True)
sorted_place_count = sorted(place_count.iteritems(), key=operator.itemgetter(1), reverse=True)

print count_delete
print count_reply_to
print sorted_uid_count_all[:5]
print sorted_uid_count_not_deleted[:5]
print [ (item[0], item[1]['name'], item[1]['count'])  for item in sorted_place_count[:5]]
  
  

