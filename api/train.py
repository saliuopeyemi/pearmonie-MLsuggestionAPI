from surprise import SVD, Dataset, Reader, accuracy
from surprise.model_selection import train_test_split
#import json
import pandas as pd
import pickle


def train(contents,interactions):
    content_df = pd.DataFrame(contents)
    interaction_df = pd.DataFrame(interactions)

    reader = Reader(rating_scale=(1,5))

    interaction_df["interaction_numeric"] = interaction_df["interaction"].map({"Liked":5,"Viewed":1})

    interaction_data = Dataset.load_from_df(interaction_df[["user_id","content_id","interaction_numeric"]],reader)

    trainset, testset = train_test_split(interaction_data, test_size=0.2)

    svd = SVD()
    svd.fit(trainset)

    with open("predictor.pkl","wb") as file:
        pickle.dump(svd,file)

