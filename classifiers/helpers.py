from tabulate import tabulate
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score, precision_score, f1_score, recall_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc, roc_auc_score
from matplotlib.colors import ListedColormap
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder
from statistics import mean
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset

import numpy as np
import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plot

class Display:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def print_exception(ex):
        print(f"{Display.FAIL}An error occurred: {ex} {Display.ENDC}")

    @staticmethod
    def print_ok(text, value=""):
        print(f"{Display.OKGREEN}{text}: {value} {Display.ENDC}")

    @staticmethod
    def print_heading(text):
        print(f"{Display.HEADER}{text} {Display.ENDC}")


def print_class_occurrence(set_sample, set_type):
    classes, class_occurrence = np.unique(set_sample, return_counts=True)
    print(f"{set_type}: {dict(zip(classes, class_occurrence))}")


def normalize_dataset(dataset):
    '''
        arranges elements in sequence for each class i.e. 1 type followed by 2nd , so on and then at last repeats
    '''

    # Separate class type objects
    classes = np.unique([apk['category'] for apk in dataset])

    temp = {}
    filtered_dataset = []
    for cls in classes:
        temp[cls] = list(filter(lambda d: d["category"] == cls, dataset))

    # Assuming each class has same elements
    while len(temp[classes[0]]) > 0:
        for cls in classes:
            filtered_dataset.append(temp[cls][0])
            del temp[cls][0]

    return filtered_dataset


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

# Plots roc on the provided plot
def plot_roc(x_cross_fold_run, classifier, y_test, x_test, AUCs, main_plot, inside_plot):
    y_pred_proba = classifier.predict_proba(x_test)[::, 1]
    fpr, tpr, threshold = metrics.roc_curve(y_test, y_pred_proba, pos_label='malicious')

    roc_auc = metrics.auc(fpr, tpr)
    AUCs.append(roc_auc)

    main_plot.plot(fpr, tpr, label= 'Fold '+str(x_cross_fold_run))
    inside_plot.plot(fpr, tpr)
    main_plot.legend(loc='upper right')

def get_cv_results(classifier, X, y, model_name, data_set): # cv - cross validation
    k = 10
    # KFold Cross Validation approach
    kf = KFold(n_splits=10, shuffle=True)
    kf.split(X)

    # Initialize the accuracy of the models to blank list. The accuracy of each model will be appended to this list
    precision_model = []
    recall_model = []
    f1_model = []
    accuracy_model = []
    x_cross_fold_run = 0

    # Initialize ROC Graph setting
    AUCs = []
    fig, main_plot = plot.subplots()
    fig.canvas.manager.set_window_title('ROC_' + model_name)
    plot.title('Receiver Operating Characteristic')
    plot.xlim([0, 1])
    plot.ylim([0, 1])
    plot.ylabel('Sensitivity')
    plot.xlabel('Specificity')
    inside_plot = zoomed_inset_axes(main_plot, 0.7, loc='lower right', borderpad=3)
    inside_plot.set_ylim(0.7, 1)
    inside_plot.set_xlim(0, 0.4) # Limit the region for zoom

    # Iterate over each train-test split
    for train_index, test_index in kf.split(X):
        x_cross_fold_run += 1
        # Split train-test
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

        # Train the model
        model = classifier.fit(X_train, y_train)

        # Append to accuracy_model the accuracy of the model
        prediction = model.predict(X_test)

        precision = precision_score(y_test, prediction, average="macro") * 100
        precision_model.append(precision)

        recall = recall_score(y_test, prediction, average="macro") * 100
        recall_model.append(recall)

        f1 = f1_score(y_test, prediction, average="macro") * 100
        f1_model.append(f1)

        accuracy = accuracy_score(y_test, prediction, normalize=True) * 100
        accuracy_model.append(accuracy)

        # all_score = precision_recall_fscore_support(y_test, prediction, average="macro")

        print(f"#{x_cross_fold_run}, P={precision} , R={recall}, f1={f1}, A={accuracy}")
        # print(f"all={all_score}")

        # Print # of class occurrences
        # print_class_occurrence(y_train, "y_train")
        # print_class_occurrence(y_test, "y_test")
        # print("")

        # Plot this run
        plot_roc(x_cross_fold_run, classifier, y_test, X_test, AUCs,main_plot, inside_plot)

    if "Random Forest" in model_name:
        # Finding Important Features
        feature_imp = pd.Series(
            classifier.feature_importances_,
            index=data_set.columns[0:-1]
        ).sort_values(ascending=False)
        print("\n\n__________Feature Importance (Random Forest)__________\n", feature_imp)

    # Set Inside small plot to show Average AUC
    inside_plot.set_title('Average AUC = %0.2f' % mean(AUCs), {'fontsize': 8})
    mark_inset(main_plot, inside_plot,loc1=1, loc2=3, fc="none", ec="0.5", ls='--')

    # Display both plots
    plot.draw()
    plot.show()

    Display.print_ok(f"Precision(Mean) of {model_name} with {k}-CV: ", np.mean(precision_model))
    Display.print_ok(f"Recall(Mean) of {model_name} with {k}-CV: ", np.mean(recall_model))
    Display.print_ok(f"F1(Mean) of {model_name} with {k}-CV: ", np.mean(f1_model))
    Display.print_ok(f"Accuracy(Mean) of {model_name} with {k}-CV: ", np.mean(accuracy_model))
    Display.print_ok(f"AUCs(Mean) of {model_name} with {k}-CV: ", np.mean(AUCs))

    print(f"Accuracies of {model_name} with {k}-CV: ", accuracy_model)
    Display.print_ok(f"AUCs of {model_name} with {k}-CV: ", AUCs)

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