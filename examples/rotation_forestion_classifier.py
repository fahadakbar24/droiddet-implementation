from rotation_forest import RotationForestClassifier
from classifier_helpers import print_classfier_results, get_classification_results, get_cv_results

import pandas as pd
import matplotlib.pyplot as plot
import seaborn as sns
# %matplotlib inline


data_set = pd.read_csv("../datasets/droid-det.csv")
class_index = len(data_set.iloc[0]) - 1

# Splitting the dataset into training and test samples
X = data_set.iloc[:, :-1].values  # Feature values
y = data_set.iloc[:, class_index].values  # Class values

# Create a  Classifier
classifier = RotationForestClassifier(n_estimators=100)

get_classification_results(classifier, X, y, data_set, "Rotation Forest")
get_cv_results(classifier, X, y, "Rotation Forest")


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
