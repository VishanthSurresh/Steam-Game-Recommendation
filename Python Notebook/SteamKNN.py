# -*- coding: utf-8 -*-
"""
Library Installations
"""

pip install pyspark

from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
import io
import matplotlib.pyplot as plt

from pyspark.rdd import RDD
from pyspark.sql import Row
from pyspark.sql import DataFrame
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit
from pyspark.sql.functions import desc
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.sql.functions import sum,avg,max,min,mean,count,sqrt
from pyspark.sql.functions import col,when
from pyspark.sql import functions as F 
from pyspark.sql.functions import col,isnan, when, count
from pyspark.ml.evaluation import RegressionEvaluator
import seaborn as sns

"""Spark Session Initialization"""

#Initialize a spark session.
def spark_intialization():
    spark = SparkSession \
        .builder \
        .appName("Pyspark Project") \
        .config("spark.some.config.option", "some-value") \
        .getOrCreate()
    return spark

# Initialise spark object
spark = spark_intialization()
spark

"""Data Preprocessing"""

from pyspark.sql import functions as pyspark_functions
from pyspark.sql.types import *
schema = StructType([ \
                     StructField("USER_ID", IntegerType(), True), \
                     StructField("Steam_Game", StringType(), True),\
                     StructField("Behaviour_Name", StringType(), True),\
                    StructField("Hours_played", FloatType(), True)])
dataframes = spark.read.schema(schema).csv("/content/drive/MyDrive/GOOGLE_COLAB/BigData/steam-200k.csv", header=False)
dataframes.show(10)

"""Renaming the columns and Dropping the unnecessary columns"""

dataframes = dataframes.withColumnRenamed("_c0","USER_ID").withColumnRenamed("_c1","Steam_Game").withColumnRenamed("_c2","Behaviour_Name").withColumnRenamed("_c3","Hours_played")
dataframes = dataframes.drop("_c4")
dataframes.show(10)

"""New Feature Generation usnig Lag functions"""

from pyspark.sql.window import Window
from pyspark.sql.functions import col, when, lag, sum

window_spec = Window.orderBy('USER_ID')

data_with_prev_value = dataframes.withColumn('prev_value', lag(col('Behaviour_Name')).over(window_spec))

combined_data = data_with_prev_value.withColumn('new_feature', when((col('prev_value') == 'purchase') & (col('Behaviour_Name') == 'play'), 2).otherwise(1))

grouped1 = combined_data.filter(((col('prev_value') == 'purchase') & (col('Behaviour_Name') == 'play')) | \
                                        ((col('prev_value') == 'purchase') & (col('Behaviour_Name') == 'purchase')) |\
                                        # ((col('prev_value') == 'null') & (col('Behaviour_Name') == 'purchase')) |\
                                  (col('prev_value') == 'play') & (col('Behaviour_Name') == 'play'));


grouped1.show(50)

"""New Feature Generation [Mean_Hourplayed] to derive Ratings"""

average = grouped1.groupBy("Steam_Game") \
            .agg(mean("Hours_played").alias("mean_Hourplayed")) \
             .select("Steam_Game", "mean_Hourplayed")
grouped = grouped1.join(average, on="Steam_Game", how="inner")
grouped.show(20)

"""New Feature Generation - Ratings based on Hours_played and new_feature"""

from pyspark.sql.functions import when
newfeature2 = grouped.withColumn("rating", 
                  when(grouped["Hours_played"] == 1.0 * grouped["mean_Hourplayed"] * grouped["new_feature"], 1)
                  .when(grouped["Hours_played"] >= 0.9 * grouped["mean_Hourplayed"] * grouped["new_feature"], 5)
                   .when((grouped["Hours_played"] >= 0.7 * grouped["mean_Hourplayed"] * grouped["new_feature"]) & (grouped["Hours_played"] < 0.9 * grouped["mean_Hourplayed"]*grouped["new_feature"]), 4)
                   .when((grouped["Hours_played"] >= 0.4 * grouped["mean_Hourplayed"] * grouped["new_feature"]) & (grouped["Hours_played"] < 0.7 * grouped["mean_Hourplayed"]*grouped["new_feature"]), 3)
                   .when((grouped["Hours_played"] >= 0.1 * grouped["mean_Hourplayed"] * grouped["new_feature"]) & (grouped["Hours_played"] < 0.4 * grouped["mean_Hourplayed"]*grouped["new_feature"]), 2)
                   .otherwise(0))
newfeature2.show()

"""Converting to Pandas Dataframe"""

pandasdf = newfeature2.toPandas()

"""Converting String Categorical values to numerical categories using Cat Codes in Pandas Dataframe"""

pandasdf['Steam_Game'] = pandasdf['Steam_Game'].astype('category')
d = dict(enumerate(pandasdf['Steam_Game'].cat.categories))
pandasdf['GAME_ID'] = pandasdf['Steam_Game'].cat.codes
pandasdf

"""Converting Pandas Dataframe to Spark Dataframe"""

newfeature = spark.createDataFrame(pandasdf)

newfeature.show()

"""The Function pairs is used to Generate Spark matrix Item for Model input itemID_1 -> [(userId_1, rating_1), (userId_2, rating_2),...]

The Function interactions is used to Generate Item,(User,Rating) pairs

For users with # interactions > n,to subsample replace their interaction history
with a sample of n items_with_rating
"""

import random

def pairs(line):
    return line[0],(line[1],float(line[7]))

def interactions(item,userRatings,n):
    if len(userRatings) > n:
        return item,random.sample(userRatings,n)
    else:
        return item, userRatings

itemPairs = newfeature2.rdd.map(lambda x : pairs(x)).groupByKey().map(lambda p: interactions(p[0],list(p[1]),100))

def f(x): return x
game_ratings_df_flatten = itemPairs.flatMapValues(f)
game_rating = game_ratings_df_flatten.map(lambda p:(p[0], p[1][0], p[1][1]))

print(" [Item -> [User,Rating]..] RDD is shown below ")
itemPairs.take(1)

"""Installing Numerize function"""

pip install numerize

"""Model Train -Test Split

Generating Item1,Item2 => UserRating1,UserRating2 combinations on train data

Total Count of Item-Item Pair and their rating data by users in Training Data

Item-Item Pair and their rating data by users in Training Data
"""

from numerize import numerize
import time
start_time = time.time()
(training,test) = game_rating.randomSplit([0.8,0.2],2000)

game_ratings  =  training.map(lambda p: Row(userId=int(p[1]), itemId=(p[0]), rating=float(p[2])))
game_ratings_2  =  training.map(lambda p: Row(userId2=int(p[1]), itemId2=(p[0]), rating2=float(p[2])))
game_ratingsdf = spark.createDataFrame(game_ratings)
game_ratingsdf2 = spark.createDataFrame(game_ratings_2)


game_df = game_ratingsdf.join(game_ratingsdf2, ( \
                                                           (game_ratingsdf.itemId != game_ratingsdf2.itemId2) & \
                                                           (game_ratingsdf.userId == game_ratingsdf2.userId2)) \
                                        ,'left') \
                                  .select("itemId","itemId2","rating","rating2")
game_df1 = game_df.na.fill(0)
game_user_ratingrdd = game_df1.rdd
end_time = time.time()
time_taken = end_time - start_time
print("Time taken:", time_taken, "seconds")
ItemPairCount  = game_user_ratingrdd.count()
print("Total Item,item Pair record count in Training Data : ", numerize.numerize(ItemPairCount))
print("Item1-Item2=>Rating1,Rating2 Dataframe input to the model is shown below : ")
game_df1.show(50,truncate=False)

"""Generating Cosine Distance for item-item pair for all user ratings

Cosine Distance calculated for our rating data for each Game-Game combination
"""

import time
start_time = time.time()
pairItems = game_user_ratingrdd.map(lambda p: ((p[0],p[1]),(p[2],p[3])))\
                                     .map(lambda p:(p[0],p[1],p[1][0]*p[1][0],p[1][1]*p[1][1],p[1][0]*p[1][1]))\
                                     .map(lambda p: Row(item_pair=p[0], rating_pair=p[1],cosim_x = p[2],cosim_y = p[3],cosim_xy = p[4] ))
pairItemsDF = spark.createDataFrame(pairItems)

pairs = pairItemsDF.groupBy("item_pair").agg(sum("cosim_x").alias("Cosim_sumx"),\
                                                sum("cosim_y").alias("Cosim_sumy"),\
                                                sum("cosim_xy").alias("Cosim_sumxy"),\
                                               )
pairSqrt = pairs.withColumn("Cosim_sumx_sqrt",sqrt("Cosim_sumx")).withColumn("Cosim_sumy_sqrt",sqrt("Cosim_sumy"))
pairCosine = pairSqrt.withColumn("Cosine_Similarity", (pairSqrt.Cosim_sumxy /((pairSqrt.Cosim_sumx_sqrt * pairSqrt.Cosim_sumy_sqrt))))
pairCosine = pairCosine.na.fill(0)
pairwiseCosineRDD = pairCosine.rdd
end_time = time.time()
time_taken = end_time - start_time
print("Time taken:", time_taken, "seconds")

print("Cosine Distance calculated for our rating data for each Game-Game combination : ")
pairCosine.show(truncate=False)

"""The function keyFirstItem is used For each item-item pair, make the first item's id the key

the function nearNeighbors is used to Sort the predictions list by similarity and select the top-N neighbors

"""

def keyFirstItem(item_pair,item_sim_data):
    (item1_id,item2_id) = item_pair
    return item1_id,(item2_id,item_sim_data)

def nearNeighbors(item_id,items_and_sims,n):
    items_and_sims.sort(key=lambda x: x[1],reverse=True)
    return item_id, items_and_sims[:n]

"""Generate Top K Neighbours based on Cosine Similarity Distance"""

pairNN = pairwiseCosineRDD.map(lambda p:keyFirstItem(p[0],p[6]))\
                  .groupByKey()\
                  .map( lambda p : (p[0], list(p[1])))\
                  .map( lambda p: nearNeighbors(p[0],p[1],5))\
                  .map( lambda p: Row(item=p[0], item_rating_list=p[1]))

def f(x): return x
cosinePairs = pairNN.flatMapValues(f)

cosinePairNN = cosinePairs.map(lambda p:(p[0],p[1][0],p[1][1]))\
                             .map(lambda p: Row(item=p[0], item_nn=p[1], item_cosine = p[2]))

cosinePairNNDF = spark.createDataFrame(cosinePairNN)

topKNN = game_ratingsdf.join(cosinePairNNDF, cosinePairNNDF.item == game_ratingsdf.itemId, 'left')


topknn_cosim = topKNN.withColumn("totalratings",topKNN.rating * topKNN.item_cosine )\
                     .withColumn("CosimTotal", topKNN.item_cosine + topKNN.item_cosine )

topknn_cosine = topknn_cosim.groupBy("itemId","item_nn").agg(sum("totalratings").alias("total_ratings"),\
                                                sum("CosimTotal").alias("CosineTotal"),\
                                               )
topknn_cosimrdd = topknn_cosim.rdd
print("Generate Top 5 Neighbours based on Cosine Similarity Distance for USER_ID - 151603712 : ")
topknn_cosim.where("userId = 151603712").show(5)

"""Evaluation - RMSE Value for Cosine Similarity Model"""

testRatings  =  test.map(lambda p: Row(TestItemID=str(p[0]),testrating=float(p[2])))\
                    .map(lambda p: Row(TestItemID=str(p[0]),testrating=(p[1])))
predRatings  =  topknn_cosimrdd.map(lambda p: Row(PredItemID=str(p[1]),Predictedrating=(p[2])))

testRatingsDF = spark.createDataFrame(testRatings)
predRatingsDF = spark.createDataFrame(predRatings)

prediction =  predRatingsDF.join(testRatingsDF,testRatingsDF.TestItemID ==  predRatingsDF.PredItemID,"inner")

prediction = prediction.na.fill(0)
finalPrediction = prediction.select("Predictedrating","testrating")

evaluator = RegressionEvaluator(metricName="rmse", labelCol="testrating",
                                predictionCol="Predictedrating")
rmse = evaluator.evaluate(finalPrediction)
print("RMSE of KNN Implementation using Cosine Similarity: ",rmse)

##Pearson Coefficient Implementation for Game Recommender System
import time
start_time = time.time()
#(training,test) = game_rating.randomSplit([0.8,0.2],2000)
pecfGameRatings  =  training.map(lambda p: Row(userId=int(p[1]), itemId=str(p[0]),rating=float(p[2])))
pecfGameRatings2  =  training.map(lambda p: Row(userId2=int(p[1]), itemId2=str(p[0]),rating2=float(p[2])))
pecfGameRatingsDF = spark.createDataFrame(pecfGameRatings)
pecfGameRatingsDF2 = spark.createDataFrame(pecfGameRatings2)

## Subtracting Mean User Game Ratings from the ratings data 
userMean = pecfGameRatingsDF.groupBy("userId").agg({'rating' : 'mean'}).withColumnRenamed("avg(rating)", "user_mean")\
                                                                            .withColumnRenamed("userId", "meanuserId")
pecfGameRatingsDFUmean = pecfGameRatingsDF.join(userMean, ( \
                                                           (pecfGameRatingsDF.userId == userMean.meanuserId)) \
                                        ,'left').select(pecfGameRatingsDF.userId,pecfGameRatingsDF.itemId,pecfGameRatingsDF.rating,userMean.user_mean)

pecfGameRatingsDF2Umean = pecfGameRatingsDF2.join(userMean, ( \
                                                           (pecfGameRatingsDF2.userId2 == userMean.meanuserId)) \
                                        ,'left').select(pecfGameRatingsDF2.userId2,pecfGameRatingsDF2.itemId2,pecfGameRatingsDF2.rating2,userMean.user_mean)                                                    
pecfMeanDeviation= pecfGameRatingsDFUmean.withColumn("UserRatingDeviation",pecfGameRatingsDFUmean.rating - pecfGameRatingsDFUmean.user_mean)

pecfMeanDeviation2= pecfGameRatingsDF2Umean.withColumn("UserRatingDeviation2",pecfGameRatingsDF2Umean.rating2 - pecfGameRatingsDF2Umean.user_mean)


#Generating Item1,Item2 => UserRating1,UserRating2 combinations on train data
pecfGamesDF = pecfMeanDeviation.join(pecfMeanDeviation2, ( \
                                                           (pecfMeanDeviation.itemId != pecfMeanDeviation2.itemId2) & \
                                                           (pecfMeanDeviation.userId == pecfMeanDeviation2.userId2)) \
                                        ,'left') \
                                  .select("itemId","itemId2","UserRatingDeviation","UserRatingDeviation")
pecfGamesDF1 = pecfGamesDF.na.fill(0)
pecfgameuser_ratingrdd = pecfGamesDF1.rdd

# Generating Cosine Distance for item-item pair for all user ratings
pecfpairwiseItems = pecfgameuser_ratingrdd.map(lambda p: ((p[0],p[1]),(p[2],p[3])))\
                                     .map(lambda p:(p[0],p[1],p[1][0]*p[1][0],p[1][1]*p[1][1],p[1][0]*p[1][1]))\
                                     .map(lambda p: Row(item_pair=p[0], rating_pair=p[1],cosim_x = p[2],cosim_y = p[3],cosim_xy = p[4] ))
pecfpairwiseItemsDF = spark.createDataFrame(pecfpairwiseItems)
pecfPairs = pecfpairwiseItemsDF.groupBy("item_pair").agg(sum("cosim_x").alias("Cosim_sumx"),\
                                                sum("cosim_y").alias("Cosim_sumy"),\
                                                sum("cosim_xy").alias("Cosim_sumxy"),\
                                               )
pecfpairSqrt = pecfPairs.withColumn("Cosim_sumx_sqrt",sqrt("Cosim_sumx")).withColumn("Cosim_sumy_sqrt",sqrt("Cosim_sumy"))
pecfPairwiseCosine = pecfpairSqrt.withColumn("Cosine_Similarity", (pecfpairSqrt.Cosim_sumxy /((pecfpairSqrt.Cosim_sumx_sqrt * pecfpairSqrt.Cosim_sumy_sqrt)+0.5))+0)
pecfPairwiseCosine = pecfPairwiseCosine.na.fill(0)
pecfPairwiseCosineRDD = pecfPairwiseCosine.rdd


# Generate Top K Neighbours based on Cosine Similarity Distance
pecfPairwiseNN = pecfPairwiseCosineRDD.map(lambda p:keyFirstItem(p[0],p[6]))\
                  .groupByKey()\
                  .map( lambda p : (p[0], list(p[1])))\
                  .map( lambda p: nearNeighbors(p[0],p[1],5))\
                  .map(lambda p: Row(item=p[0], item_rating_list=p[1]))

def f(x): return x
pecfCos = pecfPairwiseNN.flatMapValues(f)
pecfCosNN = pecfCos.map(lambda p:(p[0],p[1][0],p[1][1]))\
                             .map(lambda p: Row(item=p[0], item_nn=p[1], item_cosine = p[2]))
pecfCosNNDF = spark.createDataFrame(pecfCosNN)

pecfTopKNN = pecfGameRatingsDF.join(pecfCosNNDF, pecfCosNNDF.item == pecfGameRatingsDF.itemId, 'left')
pecfTopKNNCos = pecfTopKNN.withColumn("totalratings",pecfTopKNN.rating * pecfTopKNN.item_cosine*2 )\
                     .withColumn("CosimTotal",pecfTopKNN.item_cosine + pecfTopKNN.item_cosine )
pecfTopKNNCosine = pecfTopKNNCos.groupBy("itemId","item_nn").agg(sum("totalratings").alias("total_ratings"),\
                                                sum("CosimTotal").alias("CosineTotal"),\
                                               )
pecfTopKNNCosineSim = pecfTopKNNCosine.withColumn("PearsonDistance",(pecfTopKNNCosine.total_ratings / pecfTopKNNCosine.CosineTotal) )\
                .select("itemId","item_nn","PearsonDistance")
pe_cf_topknn_cosimrdd = pecfTopKNNCosineSim.rdd
end_time = time.time()
time_taken = end_time - start_time
print("Time taken:", time_taken, "seconds")

"""Pearson Coefficient Implementation Evaluation - RMSE Value"""

testRatings  =  test.map(lambda p: Row(TestItemID=str(p[0]),testrating=float(p[2])))\
                    .map(lambda p: Row(TestItemID=str(p[0]),testrating=(p[1])))
testRatingsDF = spark.createDataFrame(testRatings)
pecfPredRatings  =  pe_cf_topknn_cosimrdd.map(lambda p: Row(PredItemID=str(p[1]),Predictedrating=(p[2])))
pecfPredRatingsDF = spark.createDataFrame(pecfPredRatings)

pecfPred =  pecfPredRatingsDF.join(testRatingsDF,testRatingsDF.TestItemID ==  pecfPredRatingsDF.PredItemID,"inner")
pecfPred = pecfPred.na.fill(0)
pecfPreds = pecfPred.select("Predictedrating","testrating")

pecfPredsEvaluator = RegressionEvaluator(metricName="rmse", labelCol="testrating",
                                predictionCol="Predictedrating")
pecfRMSE = pecfPredsEvaluator.evaluate(pecfPreds)
print("RMSE of KNN Implementation using Pearson Coefficient Distance ",pecfRMSE)

"""Recommend Top K nearest Games for a input itemId"""

def gamRecommender(itemId):
    overallAvgRating = game_ratingsdf.filter(game_ratingsdf['userId'] == itemId).agg({'rating' : 'mean'}).collect()[0][0]
    print("Steam Games Details shown below")
    newfeature2.filter(newfeature2['USER_ID']==itemId)
    print("\n")
    print("Overall Avg Rating by user for games",itemId,"is",overallAvgRating)
    print("\n")
    print("Top N Recommended games similar to user -",itemId, "is shown below" )
    recommender = topknn_cosim.filter(topknn_cosim['userId'] == itemId )

    gameRecommender = recommender.join(newfeature2, recommender.userId == newfeature2.USER_ID,'left')\
                                   .select("USER_ID","Steam_Game")

    gameRecommender =gameRecommender.na.drop(subset=["USER_ID"])
    return gameRecommender

topNRecommender = gamRecommender(151603712)

nw = newfeature2.filter(newfeature2['USER_ID']== 151603712)
nw.show(5)

topNRecommender.show(5)

