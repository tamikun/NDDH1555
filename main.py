import pandas as pd
import matplotlib.pyplot as plt

pressure_column = 'Pressure (MPa)'
temperature_column = 'Temperature (°C)' 
entropy_column = 'Specific Entropy [kJ/(kg K)]'

# Try reading the CSV with a different encoding
df = pd.read_csv('Steam Table Data Plot.csv', encoding='ISO-8859-1')
df_pressure_line = pd.read_csv('compressed_liquid_and_superheated_steam_V1.3_edit.csv', encoding='utf-8')
# print(df_pressure_line.columns)

# Create the plot
plt.figure(figsize=(8, 6))

# Create a list of pressure values for the line
pressure_values = [0.01, 1, 5, 10, 25, 100]
available_pressures = sorted(df_pressure_line[pressure_column].unique())

# Loop through each pressure value and plot the corresponding line
for pressure in pressure_values:
    # Filter the DataFrame for the current pressure value
    df_pressure = df_pressure_line[df_pressure_line[pressure_column] == pressure]
    
    if df_pressure.empty:
        df_upper_preessure = df_pressure_line[df_pressure_line[pressure_column] ==  min([p for p in available_pressures if p > pressure], default=None)]
        df_lower_preessure = df_pressure_line[df_pressure_line[pressure_column] == max([p for p in available_pressures if p < pressure], default=None)]
        print(f"No data available for pressure {pressure} MPa. Try with upper pressure {df_upper_preessure[pressure_column].values[0]} MPa and lower pressure {df_lower_preessure[pressure_column].values[0]} MPa.")        
        continue
    
    # df_pressure = df_pressure[df_pressure['Phase'].str.strip() != 'liquid']
    df_pressure = df_pressure[df_pressure[temperature_column] < 500]
    
    # # Plot the line for the current pressure value
    # plt.plot(df_pressure[entropy_column], df_pressure[temperature_column], label=f'{pressure} MPa')
    
    # Plot the line for the current pressure value
    line = plt.plot(df_pressure[entropy_column], df_pressure[temperature_column])

    # Add text to the plot at the first data point of the line
    # You can adjust the position of the text as needed (here we add some offset)
    plt.text(df_pressure[entropy_column].iloc[-1],
            df_pressure[temperature_column].iloc[-1] + 5,
            f'{pressure} MPa', color=line[0].get_color(), fontsize=6, ha='left')
   

# Extract Temperature and Entropy columns
T = df['T (°C)']
S_L = df['SL [kJ/(kg K)]']
S_V = df['SV [kJ/(kg K)]']

T_critical = 373.9
S_critical = 4.407


plt.plot(S_L, T, label="Saturated Liquid", color="b")
plt.plot(S_V, T, label="Saturated Steam", color="r")

# plt.plot(S_line, T_line, label="0.01 MPa", color="pink")

# Adding the point to the plot
plt.scatter(S_critical, T_critical, color='green', label='Critical Point', zorder=5)

# Add a dotted horizontal line at a specific y-axis value, e.g., T = 200°C
plt.axhline(y=T_critical, color='black', linestyle='--', linewidth=0.5)


# Adding labels and title
plt.title("Temperature-Entropy (T-s) Diagram")
plt.xlabel("Specific Entropy (kJ/(kg K))")
plt.ylabel("Temperature (°C)")

# Displaying the grid
plt.grid(True)

# Adding the legend to the plot
plt.legend()

# Show the plot
plt.show()
