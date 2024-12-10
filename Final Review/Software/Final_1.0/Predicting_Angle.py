import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Load the dataset
data = pd.read_csv('/home/adka/ADKA Files/Projects/CP/Final Review/Wind_Speed_Updated.csv')

# Define features (X) and target (y)
X = data.drop(columns=["Date/Time", "Proxy_Blade_Angle"])
y = data["Proxy_Blade_Angle"]

# Split data into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train a Random Forest Regressor
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = rf_model.predict(X_test)

# Evaluate the model's performance
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

# Print evaluation metrics
print(f"MAE: {mae}")
print(f"MSE: {mse}")
print(f"R² Score: {r2}")

# Save predictions with actual values
test_results = X_test.copy()
test_results["Actual_Blade_Angle"] = y_test.values
test_results["Predicted_Blade_Angle"] = y_pred
test_results.to_csv("Predicted_Blade_Angles.csv", index=False)