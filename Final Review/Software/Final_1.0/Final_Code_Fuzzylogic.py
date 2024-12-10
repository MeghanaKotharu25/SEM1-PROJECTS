import pandas as pd
import numpy as np
import serial
import time
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Loading the predicted angles dataset
data = pd.read_csv('/home/adka/ADKA Files/Projects/CP/Final Review/Predicted_Blade_Angles.csv')

# Checking and clean column names
print("Columns in the dataset before cleaning:", data.columns)
data.rename(columns=lambda x: x.strip(), inplace=True)  #To remove leading/trailing spaces
print("Columns in the dataset after cleaning:", data.columns)

# Ensure necessary columns exist
required_columns = ['Wind Speed', 'Predicted_Blade_Angle', 'Operational Stress']
for col in required_columns:
    if col not in data.columns:
        print(f"Error: '{col}' column is missing in the dataset!")
        data[col] = 0  # Create placeholder columns if missing

# Setup Arduino connection
arduino_port = '/dev/ttyUSB0' 
baud_rate = 9600
arduino = serial.Serial(arduino_port, baud_rate)
time.sleep(2)  # Wait for Arduino to initialize

# Defining fuzzy logic system
wind_speed_fluctuation = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'Wind Speed Fluctuation')
blade_angle_change = ctrl.Antecedent(np.arange(0, 30.1, 0.1), 'Blade Angle Change Rate')
operational_stress = ctrl.Antecedent(np.arange(0, 100.1, 1), 'Operational Stress')
wear_tear_index = ctrl.Consequent(np.arange(0, 10.1, 0.1), 'Wear and Tear Index')

# Define membership functions
wind_speed_fluctuation['Low'] = fuzz.trapmf(wind_speed_fluctuation.universe, [0, 0, 2, 4])
wind_speed_fluctuation['Medium'] = fuzz.trapmf(wind_speed_fluctuation.universe, [2, 4, 6, 8])
wind_speed_fluctuation['High'] = fuzz.trapmf(wind_speed_fluctuation.universe, [6, 8, 10, 10])

blade_angle_change['Low'] = fuzz.trapmf(blade_angle_change.universe, [0, 0, 5, 10])
blade_angle_change['Medium'] = fuzz.trapmf(blade_angle_change.universe, [5, 10, 15, 20])
blade_angle_change['High'] = fuzz.trapmf(blade_angle_change.universe, [15, 20, 30, 30])

operational_stress['Low'] = fuzz.trapmf(operational_stress.universe, [0, 0, 20, 40])
operational_stress['Medium'] = fuzz.trapmf(operational_stress.universe, [20, 40, 60, 80])
operational_stress['High'] = fuzz.trapmf(operational_stress.universe, [60, 80, 100, 100])

wear_tear_index['Low'] = fuzz.trapmf(wear_tear_index.universe, [0, 0, 2, 4])
wear_tear_index['Medium'] = fuzz.trapmf(wear_tear_index.universe, [2, 4, 6, 8])
wear_tear_index['High'] = fuzz.trapmf(wear_tear_index.universe, [6, 8, 10, 10])

# Defining rules for Wear and Tear Index
rule1 = ctrl.Rule(
    wind_speed_fluctuation['High'] & blade_angle_change['High'],
    wear_tear_index['High']
)
rule2 = ctrl.Rule(
    wind_speed_fluctuation['Medium'] & blade_angle_change['Medium'] & operational_stress['Medium'],
    wear_tear_index['Medium']
)
rule3 = ctrl.Rule(
    wind_speed_fluctuation['Low'] & blade_angle_change['Low'],
    wear_tear_index['Low']
)

wear_tear_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
wear_tear_sim = ctrl.ControlSystemSimulation(wear_tear_ctrl)

# Looping through predicted angles and sending to Arduino with WTI adjustment
for i, row in data.iterrows():
    # Get input values
    wind_speed = row['Wind Speed']
    angle_change_rate = abs(row['Predicted_Blade_Angle'] - data['Predicted_Blade_Angle'].shift(1).fillna(0)[i])
    operational_stress = row['Operational Stress']  # Use placeholder value if missing

    # Set inputs for fuzzy logic system
    wear_tear_sim.input['Wind Speed Fluctuation'] = wind_speed
    wear_tear_sim.input['Blade Angle Change Rate'] = angle_change_rate
    wear_tear_sim.input['Operational Stress'] = operational_stress

    # Calculate Wear and Tear Index
    wear_tear_sim.compute()
    wear_tear_index_value = wear_tear_sim.output['Wear and Tear Index']

    # Adjust blade angle based on Wear and Tear Index
    predicted_angle = row['Predicted_Blade_Angle']
    if wear_tear_index_value > 6:  # High wear, reduce angle
        adjusted_angle = max(0, predicted_angle - 5)
    elif wear_tear_index_value < 4:  # Low wear, operate normally
        adjusted_angle = predicted_angle
    else:  # Medium wear, slightly conservative adjustment
        adjusted_angle = max(0, predicted_angle - 2)

    # Send adjusted angle to Arduino
    arduino.write(f"{int(adjusted_angle)}\n".encode())
    
    # Wait for Arduino's response
    response = arduino.readline().decode().strip()
    print(f"Angle: {adjusted_angle}, Wear Index: {wear_tear_index_value:.2f}, Arduino Response: {response}")

    # Pause for servo to adjust
    time.sleep(10)

# Close the serial connection
arduino.close()

