import pandas as pd
from sklearn.svm import SVC
from classifier_helpers import print_classfier_results, get_classification_results, get_cv_results


data_set = pd.read_csv("../datasets/droid-det.csv")
class_index = len(data_set.iloc[0]) - 1

# Splitting the dataset into training and test samples
X = data_set.iloc[:, :-1].values  # Feature values
y = data_set.iloc[:, class_index].values  # Class values

classifier = SVC(kernel='rbf', random_state=1)
get_classification_results(classifier, X, y, data_set, "SVM")
get_cv_results(classifier, X, y, "SVM")
