from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn import metrics
from classifier_helpers import print_classfier_results, get_cv_results
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd
import numpy as np


data_set = pd.read_csv("../datasets/droid-det.csv")
class_index = len(data_set.iloc[0]) - 1
random_state = 1
test_size = 0.25

# Splitting the dataset into training and test samples
X = data_set.iloc[:, :-1].values  # Feature values
y = data_set.iloc[:, class_index].values  # Class values
d_train, d_test, c_train, c_test = train_test_split(
    X,
    y,
    test_size=test_size,
    random_state=random_state
)

# Create a  Classifier
classifier = GaussianNB()
classifier.fit(d_train, c_train)
pred = classifier.predict(d_test)

# Calculating the accuracy of the predictions
conf_matrix = confusion_matrix(c_test, pred)
df_conf_matrix = pd.DataFrame(
    conf_matrix,
    index=[i for i in np.unique(c_train)],
    columns=[i for i in np.unique(c_train)]
)

# Model Accuracy, how often is the classifier correct?
print_classfier_results(data_set.columns, c_test, pred, d_test, "Gaussian NB")

print("\n\n__________conf_matrix (Gaussian NB)_________\n", conf_matrix)

print("train_sample_length = ", len(d_train))
print("test_sample_length = ", len(c_test))
print("Accuracy Of Gaussian NB For The Given Dataset:", metrics.accuracy_score(c_test, pred) * 100)
get_cv_results(classifier, X, y, "Gaussian NB")

classification_report = classification_report(c_test, pred)
print("\n\n__________Classification Report (Gaussian NB)__________\n", classification_report)
