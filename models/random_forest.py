import numpy as np
import matplotlib.pyplot as plt 
import models.preprocess as preprocess, models.utils as utils
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.inspection import permutation_importance
from sklearn.metrics import plot_confusion_matrix
from sklearn.model_selection import PredefinedSplit
from sklearn.model_selection import RandomizedSearchCV

def random_forest(sampling = False):
    print("="*60)
    print("Running Random Forest...")
    DATA_FILE = utils.get_data_directory()

    # The argument of the function will determine weather we use oversampling or not
    if(sampling):
        process_method = preprocess.oversample(DATA_FILE)
    else:
        process_method = preprocess.preprocess_data(DATA_FILE)

    X, y = process_method
    X_train, X_test, y_train, y_test = utils.split_data(X, y, 0.6)
    X_val, X_test, y_val, y_test = utils.split_data(X_test, y_test, 0.5)

    X_grid = np.concatenate((X_train, X_val))
    y_grid = np.concatenate((y_train, y_val))
    separation_boundary = [-1 for _ in y_train] + [0 for _ in y_val]
    ps = PredefinedSplit(separation_boundary)

    param_grid = {
        'n_estimators': [100, 500, 1000],
        'criterion': ['gini', 'entropy'],
        'min_samples_split': [2, 4, 5, 10, 13],
        'min_samples_leaf': [1, 2, 5, 8, 13]
    }

    clf = RandomizedSearchCV(RandomForestClassifier(), param_grid, cv=ps)

    model = clf.fit(X_grid, y_grid)
    report_dict = classification_report(y_test, model.predict(X_test), output_dict = True, target_names=["No", "Yes"])
    utils.display_metrics(report_dict)

    feature_importances = model.best_estimator_.feature_importances_
    features = utils.get_feature_names()
    top_feature_importances = list(sorted(enumerate(feature_importances), key = lambda x: x[1], reverse = True))

    u'•' == u'\u2022'
    print(f'\nThe top three features are: ')
    print(f'\t\u2022 {features[top_feature_importances[0][0]]} with a mean importance of {round(top_feature_importances[0][1], 4)}')
    print(f'\t\u2022 {features[top_feature_importances[1][0]]} with a mean importance of {round(top_feature_importances[1][1], 4)}')
    print(f'\t\u2022 {features[top_feature_importances[2][0]]} with a mean importance of {round(top_feature_importances[2][1], 4)}') 

    utils.generate_report("Random Forest", "Random Forest", model, X_test, y_test, report_dict)