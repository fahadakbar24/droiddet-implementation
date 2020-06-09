from tabulate import tabulate


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