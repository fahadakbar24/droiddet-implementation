from rotation_forest import RotationForestClassifier
from classifier_helpers import print_classfier_results, get_classification_results, get_cv_results

import pandas as pd

model_name = "Rotation Forest"
data_set = pd.read_csv("../datasets/droid-det.csv")
class_index = len(data_set.iloc[0]) - 1

# Splitting the dataset into training and test samples
X = data_set.iloc[:, :-1].values  # Feature values
y = data_set.iloc[:, class_index].values  # Class values

# Create a  Classifier
classifier = RotationForestClassifier(n_estimators=100)

# get_classification_results(classifier, X, y, data_set, model_name)
get_cv_results(classifier, X, y, model_name)
