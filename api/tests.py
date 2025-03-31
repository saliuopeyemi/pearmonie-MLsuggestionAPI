import pickle

with open("predictor.pkl","rb") as file:
    predictor = pickle.load(file)

pred = predictor.predict(4,7)
print(dir(pred))
print(f"{pred.iid}------{pred.est}")
