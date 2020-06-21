from rotation_forest import RotationForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn import metrics
from classifier_helpers import print_classfier_results

import pandas as pd
import numpy as np
import matplotlib.pyplot as plot
import seaborn as sns
# %matplotlib inline


data_set = pd.read_csv("../datasets/droid-det.csv")
class_index = len(data_set.iloc[0]) - 1
random_state = 1
test_size = 0.25

# Splitting the dataset into training and test samples
d_train, d_test, c_train, c_test = train_test_split(
    data_set.iloc[:, :-1].values,
    data_set.iloc[:, class_index].values,
    test_size=test_size,
    random_state=random_state
)

# Create a  Classifier
classifier = RotationForestClassifier(n_estimators=100)
fit = classifier.fit(d_train, c_train)
prediction = classifier.predict(d_test)

# Calculating the accuracy of the predictions
conf_matrix = confusion_matrix(c_test, prediction)
df_conf_matrix = pd.DataFrame(
    conf_matrix,
    index=[i for i in np.unique(c_train)],
    columns=[i for i in np.unique(c_train)]
)

# Model Accuracy, how often is the classifier correct?
print_classfier_results(data_set.columns, c_test, prediction, d_test, "Rotation Forest")
print("\n\n__________conf_matrix (Rotation Forest)_________\n", conf_matrix)

print("train_sample_length = ", len(d_train))
print("test_sample_length = ", len(c_test))
print("Accuracy Of RF For The Given Dataset:", metrics.accuracy_score(c_test, prediction))

classification_report = classification_report(c_test, prediction)
print("\n\n__________Classification Report (Rotation Forest)__________\n", classification_report)

# # Finding Important Features
# feature_imp = pd.Series(
#     classifier.feature_importances_,
#     index=data_set.columns[0:class_index]
# ).sort_values(ascending=False)
# print("\n\n__________Feature Importance__________\n", feature_imp)


# Creating a bar plot
# sns.barplot(x=feature_imp, y=feature_imp.index)
# # Add labels to your graph
# plt.xlabel('Feature Importance Score')
# plt.ylabel('Features')
# plt.title("Visualizing Important Features")
# plt.legend()
# plt.show()