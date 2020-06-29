from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn import metrics
from classifier_helpers import print_classfier_results, get_classification_results, get_cv_results
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd
import numpy as np


data_set = pd.read_csv("../datasets/droid-det.csv")
class_index = len(data_set.iloc[0]) - 1

# Splitting the dataset into training and test samples
X = data_set.iloc[:, :-1].values  # Feature values
y = data_set.iloc[:, class_index].values  # Class values

# Create a  Classifier
classifier = GaussianNB()

get_classification_results(classifier, X, y, data_set, "Gaussian NB")
get_cv_results(classifier, X, y, "Gaussian NB")