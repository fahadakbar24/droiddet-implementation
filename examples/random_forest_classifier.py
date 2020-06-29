from sklearn.ensemble import RandomForestClassifier

from classifier_helpers import print_classfier_results, get_classification_results, get_cv_results
import pandas as pd
import numpy as np
import matplotlib.pyplot as plot
import seaborn as sn
from matplotlib.colors import ListedColormap

data_set = pd.read_csv("../datasets/droid-det.csv")
class_index = len(data_set.iloc[0]) - 1

# Splitting the dataset into training and test samples
X = data_set.iloc[:, :-1].values  # Feature values
y = data_set.iloc[:, class_index].values  # Class values

classifier = RandomForestClassifier(n_estimators=100)

get_classification_results(classifier, X, y, data_set, "Random Forest")
get_cv_results(classifier, X, y, "Random Forest")


# Creating a bar plot
# sns.barplot(x=feature_imp, y=feature_imp.index)
# # Add labels to your graph
# plt.xlabel('Feature Importance Score')
# plt.ylabel('Features')
# plt.title("Visualizing Important Features")
# plt.legend()
# plt.show()


def plotter(x_set, y_set, title, pos):
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


def visualize(x1_set, y1_set, title1, x2_set, y2_set, title2):
    plot.figure(figsize=(10, 5))
    # plot.figtext(0, 0.3, classification_report)

    plot.subplot(1, 3, 1)
    sn.heatmap(df_conf_matrix, annot=True)

    plotter(x1_set, y1_set, title1, 2)
    plotter(x2_set, y2_set, title2, 3)

    plot.show()


# # Visualizing the classifier & predictions
# lbl_enc = LabelEncoder()
# c_train = lbl_enc.fit_transform(c_train)
# # c_test = lbl_enc.fit_transform(c_test)
#
# d_train_pca_2d = PCA(n_components=2).fit(d_train).transform(d_train)
# d_test_pca_2d = PCA(n_components=2).fit(d_test).transform(d_test)
#
# classifier.fit(d_train_pca_2d, c_train)
# c_train = lbl_enc.inverse_transform(c_train)

# visualize(
#     d_train_pca_2d, c_train, "Classes",
#     d_test_pca_2d, c_test, "Classes predictions"
# )
