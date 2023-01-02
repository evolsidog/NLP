from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import SQLContext
from pyspark.sql.functions import desc

from collections import namedtuple

import time
import matplotlib.pyplot as plt
import seaborn as sns
import pandas

sc = SparkContext()
ssc = StreamingContext(sc, 10) # 10 seconds batch interval
sqlContext = SQLContext(sc)

socket_stream = ssc.socketTextStream("127.0.0.1", 5555) # initiate streaming from a TCP (socket) source
lines = socket_stream.window(60) # batch size 60 seconds

# we will analyzing tweets every minute to identify which are the top 10 #tags

# clean text
fields = ("hashtag", "count")
Tweet = namedtuple('Tweet', fields)
# apply operations on tweets and save them in a temporary sql table
(lines.flatMap(lambda text: text.split(" ")) # Splits tweets to words (list of words)
.filter(lambda word: word.lower().startswith("#")) # check hashtag
.map(lambda word: (word.lower(), 1)) # lowercase word
.reduceByKey(lambda a, b: a+b)
.map(lambda rec: Tweet(rec[0], rec[1])) # stores in a Tweet Object
.foreachRDD(lambda rdd: rdd.toDF().sort(desc("count"))
.limit(10).registerTempTable("tweets"))) # sorts them in a dataframe and register only top 10 hashtags to a table 

# FIXME Temporal table not is created. Must be created out of this context to persist,


ssc.start()
""" 
# visualize top 10 hashtags results 
count = 0
while count < 5:
    time.sleep(20)
    top_10_tags = sqlContext.sql('Select hashtag, count from tweets')
    top_10_df = top_10_tags.toPandas()
    plt.figure(figsize=(10, 8))
    sns.barplot(x="count", y="hashtag", data=top_10_df)
    plt.savefig("top_topics_" + str(count) + ".png")
    count = count + 1
    print(count)
 """

# stop streaming and wait couple of minutes to get enought tweets
ssc.stop()