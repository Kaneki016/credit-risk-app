# evaluation_agent.py

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split


class EvaluationAgent:
    def evaluate_model(self, model, X_test, y_test, save_path="evaluation_results.pkl"):
        print("\nAgent 4: Evaluating model performance...")

        # Predictions
        y_pred = model.predict(X_test)

        # Classification report
        classification_rep = classification_report(y_test, y_pred, output_dict=True)
        print("\n--- Classification Report ---")
        print(classification_report(y_test, y_pred))

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=['Approved', 'Rejected'],
                    yticklabels=['Approved', 'Rejected'])
        plt.title('Confusion Matrix')
        plt.ylabel('Actual Label')
        plt.xlabel('Predicted Label')
        plt.show()

        # ROC curve & AUC
        y_prob = model.predict_proba(X_test)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        roc_auc = auc(fpr, tpr)
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curve')
        plt.legend(loc="lower right")
        plt.show()

        # Save all results
        evaluation_results = {
            "classification_report": classification_rep,
            "confusion_matrix": cm,
            "roc_curve": {
                "fpr": fpr,
                "tpr": tpr
            },
            "auc_score": roc_auc
        }
        joblib.dump(evaluation_results, save_path)
        print(f"\n✅ Evaluation results saved to {save_path}")


if __name__ == "__main__":
    # === Change these paths as needed ===
    dataset_path = "credit_risk_dataset.csv"
    model_paths = [
        "trained_model_1.pkl",
        "trained_model_2.pkl"
    ]

    try:
        df = pd.read_csv(dataset_path)
    except FileNotFoundError:
        print(f"❌ Dataset file not found: {dataset_path}")
        exit(1)

    # Prepare features & target
    target_col = "loan_status"
    X = df.drop(columns=[target_col])
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    agent = EvaluationAgent()

    # Loop through both models
    for i, model_path in enumerate(model_paths, start=1):
        try:
            model = joblib.load(model_path)
        except FileNotFoundError:
            print(f"❌ Model file not found: {model_path}")
            continue

        save_path = f"evaluation_results_model_{i}.pkl"
        print(f"\n🔍 Evaluating model {i} from {model_path}...")
        agent.evaluate_model(model, X_test, y_test, save_path)
