from tabulate import tabulate
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score

import numpy as np


def print_classfier_results(columns, c_test, prediction, d_test, classifier_name=""):
    print(f"__________Actual Vs Predicted Classes ({classifier_name})__________\n")
    pred_tbl = []
    for sample_index, sample in enumerate(d_test):
        pred_tbl_row = [
            c_test[sample_index],
            prediction[sample_index]
        ]
        pred_tbl_row.extend(sample)
        pred_tbl.append(pred_tbl_row)

    pred_tbl_headers = ["Predicted", "Actual"]
    pred_tbl_headers.extend(columns)
    print(tabulate(pred_tbl, headers=pred_tbl_headers, tablefmt='orgtbl'))


def get_cv_results(classifier, X, y, model_name): # cv - cross validation
    k = 10
    # KFold Cross Validation approach
    kf = KFold(n_splits=10, shuffle=False)
    kf.split(X)

    # Initialize the accuracy of the models to blank list. The accuracy of each model will be appended to this list
    accuracy_model = []

    # Iterate over each train-test split
    for train_index, test_index in kf.split(X):
        # Split train-test
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
        # Train the model
        model = classifier.fit(X_train, y_train)
        # Append to accuracy_model the accuracy of the model
        prediction = model.predict(X_test)
        accuracy_model.append(accuracy_score(y_test, prediction, normalize=True) * 100)

    print(f"Accuracy(Mean) of {model_name} with {k}-CV: ", np.mean(accuracy_model))
    print(f"Accuracies of {model_name} with {k}-CV: ", accuracy_model)

    # return the accuracy
    return accuracy_model
