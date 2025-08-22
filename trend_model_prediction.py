import pandas as pd
from prophet import Prophet
import joblib  # for saving/loading model


def load_and_prepare_data(file_path: str):
    """Load CSV and aggregate applicant counts per month."""
    df = pd.read_csv(file_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Count applicants per month
    monthly_counts = df.groupby(df["timestamp"].dt.to_period("M")).size()
    monthly_counts = monthly_counts.to_timestamp()

    # Prepare for Prophet
    df_counts = monthly_counts.reset_index()
    df_counts.columns = ["ds", "y"]  # Prophet requires ds (date) and y (value)

    return df_counts


def train_and_forecast(data: pd.DataFrame, months_ahead: int = 3, model_path: str = "applicant_forecast_model.pkl"):
    """Fit Prophet model, save it, and forecast applicants for future months."""
    model = Prophet()
    model.fit(data)

    # Save model
    joblib.dump(model, model_path)
    print(f"✅ Model saved to {model_path}")

    # Make future dataframe
    future = model.make_future_dataframe(periods=months_ahead, freq="M")
    forecast = model.predict(future)

    # Keep only forecast rows (future)
    forecast_result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(months_ahead)
    return forecast_result


if __name__ == "__main__":
    file_path = "prediction_logs.csv"  # Change to your file
    data = load_and_prepare_data(file_path)

    print("📊 Applicant counts (historical):")
    print(data.tail(5))  # show last 5 months

    forecast_result = train_and_forecast(data, months_ahead=3)

    print("\n🔮 Forecasted applicants for next 3 months:")
    print(forecast_result)
