from sklearn.metrics import (precision_recall_curve,average_precision_score,precision_score,recall_score,classification_report,f1_score,roc_auc_score)
import numpy as np
def evaluation_model(y_true,probs):
    preds=(probs>0.5).astype(int)
    print("\n=== Model Evaluation ===")
    print("ROC-AUC:", roc_auc_score(y_true, probs))
    print("Average Precision:", average_precision_score(y_true, probs))
    print("\nPrecision:", precision_score(y_true, preds))
    print("Recall:", recall_score(y_true, preds))
    print("F1 Score:", f1_score(y_true, preds))
    print("\nClassification Report:\n", classification_report(y_true, preds))
def evaluate_multiple_thresholds(y_true, probs):
    thresholds = [0.3, 0.5, 0.7, 0.9,0.95]
    print("\n=== Threshold Analysis ===")
    for t in thresholds:
        preds = (probs > t).astype(int)
        print(f"\nThreshold: {t}")
        print("Precision:", precision_score(y_true, preds))
        print("Recall:", recall_score(y_true, preds))
        print("F1:", f1_score(y_true, preds))
def best_f1_threshold(y_true, probs):
    from sklearn.metrics import precision_recall_curve
    precision, recall, thresholds = precision_recall_curve(y_true, probs)
    f1 = 2 * (precision * recall) / (precision + recall + 1e-6)
    best_idx = np.argmax(f1)
    best_threshold = thresholds[best_idx]
    print("\n=== Best Threshold (F1) ===")
    print("Threshold:", best_threshold)
    print("Precision:", precision[best_idx])
    print("Recall:", recall[best_idx])
    print("F1 Score:", f1[best_idx])
    return best_threshold