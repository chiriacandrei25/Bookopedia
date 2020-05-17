import surprise
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split


def get_sim_matrix(load_sim_matrix):
    raw = pd.read_csv('books_metadata/ratings.csv')
    if load_sim_matrix is False:
        raw = pd.read_csv('books_metadata/ratings.csv')
        raw = raw[raw['book_id'] <= 1900]
        raw.drop_duplicates(inplace=True)
        print('we have', str(raw.shape[0]), 'ratings')
        print('the number of unique users we have is:', len(raw.user_id.unique()))
        print('the number of unique books we have is:', len(raw.book_id.unique()))

        rawTrain = raw[['user_id', 'book_id', 'rating']]
        rawTrain, rawHoldout = train_test_split(raw, test_size=0.25)
        reader = surprise.Reader(rating_scale=(1, 5))
        data = surprise.Dataset.load_from_df(rawTrain, reader)

        sim_options = {'name': 'cosine', 'user_based': False}
        collabKNN = surprise.KNNWithMeans(k=100, sim_options=sim_options)
        kSplit = surprise.model_selection.split.KFold(n_splits=2, shuffle=False)
        for trainset, testset in kSplit.split(data):
            collabKNN.fit(trainset)
            predictionsKNN = collabKNN.test(testset)
            surprise.accuracy.rmse(predictionsKNN, verbose=True)

        sim_matrix = collabKNN.compute_similarities()
        with open('books_sim_matrix', 'wb') as output:
            pickle.dump(sim_matrix, output, protocol=pickle.HIGHEST_PROTOCOL)
        return sim_matrix

    with open('books_sim_matrix', 'rb') as input:
        sim_matrix = pickle.load(input)
        return sim_matrix
