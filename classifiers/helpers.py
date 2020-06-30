from tabulate import tabulate
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.metrics import confusion_matrix, classification_report
from matplotlib.colors import ListedColormap
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder

import numpy as np
import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plot


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


def get_classification_results(classifier, X, y, data_set, model_name):
    test_size = 0.25  # Paper: 0.44
    random_state = 1
    class_index = len(data_set.iloc[0]) - 1

    d_train, d_test, c_train, c_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state
    )

    # Initializing Support Vector Machine and fitting the training data

    classifier.fit(d_train, c_train)

    # Predicting the classes for test set
    prediction = classifier.predict(d_test)

    # Model Accuracy, how often is the classifier correct?
    print_classfier_results(data_set.columns, c_test, prediction, d_test, model_name)

    # Calculating the accuracy of the predictions
    conf_matrix = confusion_matrix(c_test, prediction)
    df_conf_matrix = pd.DataFrame(
        conf_matrix,
        index=[i for i in np.unique(c_train)],
        columns=[i for i in np.unique(c_train)]
    )

    print(f"\n__________conf_matrix {model_name}_________\n", conf_matrix)
    print("train_sample_length = ", len(d_train))
    print("test_sample_length = ", len(c_test))

    accuracy = metrics.accuracy_score(c_test, prediction) * 100
    print(f"Accuracy Of {model_name} For The Given Dataset : ", accuracy)

    classify_report = classification_report(c_test, prediction)
    print(f"\n__________Classification Report {model_name}__________\n", classify_report)

    if "Random Forest" in model_name:
        # Finding Important Features
        feature_imp = pd.Series(
            classifier.feature_importances_,
            index=data_set.columns[0:class_index]
        ).sort_values(ascending=False)
        print("\n\n__________Feature Importance (Random Forest)__________\n", feature_imp)


def get_cv_results(classifier, X, y, model_name): # cv - cross validation
    k = 10
    # KFold Cross Validation approach
    kf = KFold(n_splits=10, shuffle=True)
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


def plotter(classifier, x_set, y_set, title, pos):
    plot.subplot(1, 3, pos)
    plot.title(title)
    plot.xlabel("Weight in Grams")
    plot.ylabel("Size in cm")
    markers = ["+", "o", "*"]

    x1, x2 = np.meshgrid(
        np.arange(
            start=x_set[:, 0].min() - 1,
            stop=x_set[:, 0].max() + 1,
            step=0.01
        ),
        np.arange(
            start=x_set[:, 1].min() - 1,
            stop=x_set[:, 1].max() + 1,
            step=0.01
        )
    )

    plot.contourf(
        x1,
        x2,
        classifier.predict(
            np.array([x1.ravel(), x2.ravel()]).T
        ).reshape(x1.shape),
        alpha=0.75,
        cmap=ListedColormap(("black", "white", "cyan"))
    )
    plot.xlim(x1.min(), x1.max())
    plot.ylim(x2.min(), x2.max())

    for i, j in enumerate(np.unique(y_set)):
        plot.scatter(
            x_set[y_set == j, 0],
            x_set[y_set == j, 1],
            c=ListedColormap(("red", "blue", "green"))(i),
            s=50,
            marker=markers[i],
            label=j
        )
    plot.legend()


def visualize(classifier, x1_set, y1_set, title1, x2_set, y2_set, title2):
    # Visualizing the classifier & predictions
    # lbl_enc = LabelEncoder()
    # c_train = lbl_enc.fit_transform(c_train)
    # # c_test = lbl_enc.fit_transform(c_test)
    #
    # d_train_pca_2d = PCA(n_components=2).fit(d_train).transform(d_train)
    # d_test_pca_2d = PCA(n_components=2).fit(d_test).transform(d_test)
    #
    # classifier.fit(d_train_pca_2d, c_train)
    # c_train = lbl_enc.inverse_transform(c_train)
    #
    # visualize(
    #     d_train_pca_2d, c_train, "Classes",
    #     d_test_pca_2d, c_test, "Classes predictions"
    # )

    plot.figure(figsize=(10, 5))
    # plot.figtext(0, 0.3, classification_report)

    plot.subplot(1, 3, 1)
    sn.heatmap(df_conf_matrix, annot=True)

    plotter(classifier, x1_set, y1_set, title1, 2)
    plotter(classifier, x2_set, y2_set, title2, 3)

    plot.show()


def plot_bar_graph():
    # Creating a bar plot
    sns.barplot(x=feature_imp, y=feature_imp.index)
    # Add labels to your graph
    plt.xlabel('Feature Importance Score')
    plt.ylabel('Features')
    plt.title("Visualizing Important Features")
    plt.legend()
    plt.show()