import pandas as pd
import numpy as np

def retrieve_top_words(text, vectorizer, nb_model, n = 10):
    
    '''Retrieve top n words affecting the prediction of the text from a learned vectorizer and Naive Bayes model'''

    #Store vectorized text as variable
    vector = vectorizer.transform(pd.DataFrame({'col':text}, index=[0])['col']).todense()

    #Get index of non-zero values present in source text and vectorizer (i.e. to find out the words contributing to prediction)
    index_array = (vector).nonzero()[1]

    #Get prediction of text
    pred = nb_model.predict(vector)[0]

    #Get log probabilities of words that account for text in given prediction
    log_proba = nb_model.feature_log_prob_[pred]

    #Build dictionary of index of words and their probabilities
    words_probability = {}

    for index in index_array:
        words_probability[index] = np.exp(log_proba[index])

    #Sort dictionary based on the probabilities, in descending order
    words_probability = dict(sorted(words_probability.items(), key=lambda item: item[1], reverse=True))

    #Build list for index of top n probabilities of words that account for text in given prediction
    word_list = []

    for key, value in words_probability.items():
        word_list.append(vectorizer.get_feature_names()[key])
        if len(word_list)==n:
            break

    return word_list