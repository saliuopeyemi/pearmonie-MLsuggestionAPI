from celery import shared_task
import time
from . import models
from surprise import SVD, Dataset, Reader, accuracy
from surprise.model_selection import train_test_split
#import json
import pandas as pd
import pickle
import os

from datetime import datetime


def train(interactions):
    #content_df = pd.DataFrame(contents)
    interaction_df = pd.DataFrame(interactions)

    reader = Reader(rating_scale=(1,5))

    interaction_df["interaction_numeric"] = interaction_df["interaction"].map({"Liked":5,"Viewed":1})

    interaction_data = Dataset.load_from_df(interaction_df[["user_id","content_id","interaction_numeric"]],reader)

    trainset, testset = train_test_split(interaction_data, test_size=0.2)

    svd = SVD()
    svd.fit(trainset)
    
    try:
        #Ensure model update
        os.remove("predictor.pkl")
    except:
        pass

    with open("predictor.pkl","wb") as file:
        pickle.dump(svd,file)

    #Logging
    print(f"Last Training at:{datetime.now()}")





@shared_task
def train_predictor():
    interactions = models.UserInteraction.objects.all().values("user","content","interaction")
    #contents = models.Content.objects.all().values("title","description","category","tags","ai_score")
    interaction_data = [{"user_id":item["user"],"content_id":item["content"],"interaction":item["interaction"]} for item in interactions]
    #content_data = [{"title":item["title"],"description":item["description"],"category":item["category"],"tags":item["tags"],"ai_score":item["ai_score"]} for item in contents]
    train(interaction_data)

