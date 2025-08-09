# visualization_agent.py

import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import pandas as pd


class VisualizationAgent:
    def __init__(self, df):
        self.df = df

    def visualize_data(self, save_path="visualizations.pkl"):
        if self.df is None:
            print("Visualization Agent: No data available to visualize.")
            return

        print("\nAgent 2: Generating data visualizations...")
        plt.style.use('seaborn-v0_8-whitegrid')
        fig, axes = plt.subplots(2, 2, figsize=(18, 12))
        fig.suptitle('Credit Risk Dataset Visualizations', fontsize=20, y=1.02)

        sns.histplot(self.df['person_age'], bins=30, kde=True, ax=axes[0, 0], color='skyblue')
        axes[0, 0].set_title('Distribution of Person Age')

        sns.countplot(x='loan_status', data=self.df, ax=axes[0, 1], palette='viridis')
        axes[0, 1].set_title('Loan Status (0=Approved, 1=Rejected)')

        sns.scatterplot(
            x='person_income', y='loan_amnt',
            hue='loan_status', data=self.df, ax=axes[1, 0], palette='magma'
        )
        axes[1, 0].set_title('Loan Amount vs. Income by Loan Status')

        sns.countplot(x='loan_grade', hue='loan_status', data=self.df, ax=axes[1, 1], palette='plasma')
        axes[1, 1].set_title('Loan Grade by Loan Status')

        plt.tight_layout()
        plt.show()

        joblib.dump(fig, save_path)
        print(f"✅ Visualizations saved to {save_path}")


if __name__ == "__main__":
    # === Change dataset_path to your CSV file ===
    dataset_path = "credit_risk_dataset.csv"

    try:
        df = pd.read_csv(dataset_path)
    except FileNotFoundError:
        print(f"❌ Dataset file not found: {dataset_path}")
        exit(1)

    agent = VisualizationAgent(df)
    agent.visualize_data("visualizations.pkl")
