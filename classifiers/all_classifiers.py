from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from rotation_forest import RotationForestClassifier
from sklearn.naive_bayes import GaussianNB
from helpers import print_classfier_results, get_classification_results, get_cv_results, plot_bar_graph, Display
import pandas as pd

data_set = pd.read_csv("../datasets/droid-det.csv")
class_index = len(data_set.iloc[0]) - 1

# Splitting the dataset into training and test samples
X = data_set.iloc[:, :-1].values  # Feature values
y = data_set.iloc[:, class_index].values  # Class values


def execute_classification(classifier, model_name):
    Display.print_heading(f"------------- Generating Results for {model_name} Classification -------------")

    # get_classification_results(classifier, X, y, data_set, model_name)
    get_cv_results(classifier, X, y, model_name, data_set)

    print("\n\n")


def svm_classification():
    execute_classification(SVC(kernel='rbf', random_state=1, probability=True), "SVM")


def random_forest_classification():
    execute_classification(RandomForestClassifier(n_estimators=100), "Random Forest")
    # plot_bar_graph()


def rotation_forest_classification():
    execute_classification(RotationForestClassifier(n_estimators=100), "Rotation Forest")


def gaussian_naive_bayes_classification():
    execute_classification(GaussianNB(), "Gaussian NB")


svm_classification()
random_forest_classification()
rotation_forest_classification()
gaussian_naive_bayes_classification()
