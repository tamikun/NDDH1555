import numpy as np
import matplotlib.pyplot as plt
from pyXSteam.XSteam import XSteam
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)
    
steam = XSteam(XSteam.UNIT_SYSTEM_MKS)  # SI units
plt.figure(figsize=(10, 7))

def find_pressure_for_st(steam, s_target, t, p_min=0.01, p_max=400, tol=1e-3, n_samples=100):
    # Sample entropy over a range of pressures at the given temperature
    pressures = np.linspace(p_min, p_max, n_samples)
    entropies = []
    valid_pressures = []
    for p in pressures:
        try:
            s = steam.s_pt(p, t)
            entropies.append(s)
            valid_pressures.append(p)
        except Exception:
            continue
    if not entropies:
        return None # No valid pressures found
    s_min = min(entropies)
    idx_min = entropies.index(s_min)
    p_min_entropy = valid_pressures[idx_min]
    # print(f"Minimum entropy: {s_min} kJ/(kg K) at pressure: {p_min_entropy} bar")
    s_max = max(entropies)
    idx_max = entropies.index(s_max)
    # p_max_entropy = valid_pressures[idx_max]
    # print(f"Maximum entropy: {s_max} kJ/(kg K) at pressure: {p_max_entropy} bar")
    
    if not (s_min <= s_target <= s_max):
        return None  # No solution possible
        
    for _ in range(n_samples):
        p_mid = (p_min + p_max) / 2
        # print(f"Trying pressure: {p_mid} bar")
        try:
            s_mid = steam.s_pt(p_mid, t)
            # print(f"Entropy at {p_mid} bar and {t} °C: {s_mid} kJ/kg")
        except Exception:
            p_max = p_mid
            continue
        if abs(s_mid - s_target) < tol:
            return p_mid
        if s_mid < s_target:
            p_max = p_mid
        else:
            p_min = p_mid
    
    return None

def find_pressure_for_ht(steam, h_target, t, p_min=0.01, p_max=400, tol=1e-3, n_samples=100):
    # Sample enthalpy over a range of pressures at the given temperature
    pressures = np.linspace(p_min, p_max, n_samples)
    enthalpies = []
    valid_pressures = []
    for p in pressures:
        try:
            h = steam.h_pt(p, t)
            enthalpies.append(h)
            valid_pressures.append(p)
        except Exception:
            continue

    if not enthalpies:
        return None

    h_min = min(enthalpies)
    idx_min = enthalpies.index(h_min)
    p_min_enthalpy = valid_pressures[idx_min]
    # print(f"Minimum enthalpy: {h_min} kJ/kg at pressure: {p_min_enthalpy} bar")
    h_max = max(enthalpies)
    # idx_max = enthalpies.index(h_max)
    # p_max_enthalpy = valid_pressures[idx_max]
    # print(f"Maximum enthalpy: {h_max} kJ/kg at pressure: {p_max_enthalpy} bar")
    
    if not (h_min <= h_target <= h_max):
        return None  # No solution possible
    
    if t < steam.tsat_p(p_min_enthalpy): # Corrected condition for compressed liquid
        # If h_min <= h_target <= h_max and t < saturation temperature, we are in compressed liquid region
        # Then find the pressure from enthalpy at minimum pressure to maximum pressure
        print(f"Phase of water at {p_min_enthalpy} bar and {t} °C: Compressed Liquid")
        p_min = p_min_enthalpy
        # Find the lowest index > idx_min and enthalpy > h_target
        idx = next((i for i, h in enumerate(enthalpies[idx_min:], start=idx_min) if h > h_target), None)
        # print(f"First enthalpy greater than target: {enthalpies[idx]} kJ/kg at pressure: {valid_pressures[idx]} bar (index {idx})") if idx is not None else print("No enthalpy greater than target found.")
        p_max = valid_pressures[idx] if idx is not None else p_max
        
        # Binary search for pressure at given h, t
        for _ in range(n_samples):
            p_mid = (p_min + p_max) / 2
            # print(f"Trying pressure: {p_mid} bar")
            try:
                h_mid = steam.h_pt(p_mid, t)
                # print(f"Enthalpy at {p_mid} bar and {t} °C: {h_mid} kJ/kg")
            except Exception:
                p_max = p_mid
                continue
            if abs(h_mid - h_target) < tol:
                return p_mid
            if h_mid < h_target:
                p_min = p_mid
            else:
                p_max = p_mid
    else:
        print(f"Phase of water at {p_min_enthalpy} bar and {t} °C: Vapor")
        # Binary search for pressure at given h, t
        # Enthalpy increases with decreasing pressure in superheated region
        p_max = p_min_enthalpy
        # Find the p_min where enthalpy > h_target
        idx = next((i for i, h in enumerate(enthalpies) if h < h_target), None) - 1
        # print(f"Pmin where enthalpy is greater than target: {enthalpies[idx]} kJ/kg at pressure: {valid_pressures[idx]} bar (index {idx})") if idx is not None else print("No enthalpy greater than target found.")
        p_min = valid_pressures[idx] if idx is not None else p_min
        
        for _ in range(n_samples):
            p_mid = (p_min + p_max) / 2
            # print(f"Trying pressure: {p_mid} bar")
            try:
                h_mid = steam.h_pt(p_mid, t)
                # print(f"Enthalpy at {p_mid} bar and {t} °C: {h_mid} kJ/kg")
            except Exception:
                p_max = p_mid
                continue
            if abs(h_mid - h_target) < tol:
                return p_mid
            if h_mid < h_target:
                p_max = p_mid
            else:
                p_min = p_mid
    
    return None
    
def plot_ts_saturated_lines():
    # Plot saturated liquid and vapor lines
    T_critical = 373.9
    S_critical = 4.407
    t_sat = np.linspace(0.1, T_critical, 500)
    sL = []
    sV = []
    for t in t_sat:
        try:
            p_sat = steam.psat_t(t)
            sL.append(steam.sL_p(p_sat))
            sV.append(steam.sV_p(p_sat))
        except Exception:
            sL.append(np.nan)
            sV.append(np.nan)
    plt.plot(sL, t_sat, color='blue', linestyle='--', label='Saturated Liquid')
    plt.plot(sV, t_sat, color='red', linestyle='--', label='Saturated Vapor')
    # Plot critical point
    plt.plot([S_critical], [T_critical], marker='o', color='black', label='Critical Point')
    plt.xlabel('Entropy (kJ/kg·K)')
    plt.ylabel('Temperature (°C)')
    
def plot_ts_diagram_multiple_pressures(steam, pressures):
    # Plot isobars
    for p in pressures:
        t_min = 0
        t_max = 600
        temperatures = np.linspace(t_min, t_max, 500)
        entropies = []
        valid_temperatures = []
        for t in temperatures:
            try:
                s = steam.s_pt(p, t)
                entropies.append(s)
                valid_temperatures.append(t)
            except Exception:
                continue
        plt.plot(entropies, valid_temperatures, label=f'{p} bar')
    
    plot_ts_saturated_lines()

def get_point_data(point, steam):
    if "p" in point and "t" in point:
        s = steam.s_pt(point["p"], point["t"])
        t = point["t"]
        p = point["p"]
    elif "p" in point and "h" in point:
        t = steam.t_ph(point["p"], point["h"])
        s = steam.s_ph(point["p"], point["h"])
        p = point["p"]
    elif "h" in point and "t" in point:
        # Need to estimate pressure first
        p = find_pressure_for_ht(steam, point["h"], point["t"])
        if p is None:
            print(Fore.RED + f"Could not find pressure for enthalpy {point['h']} kJ/kg and temperature {point['t']} °C.")
            return None, None, None
        s = steam.s_pt(p, point["t"])
        t = point["t"]
    elif "s" in point and "t" in point:
        s = point["s"]
        t = point["t"]
        p = find_pressure_for_st(steam, s, t)
    else:
        return None, None, None
    return s, t, p

def plot_line_between_points(steam, pt_start, pt_end, n_points=50):
    
    pt_start_data = get_point_data(pt_start, steam)
    pt_end_data = get_point_data(pt_end, steam)
    
    if pt_start_data is None or pt_end_data is None:
        print(Fore.RED + f"Could not plot line between {pt_start['name']} and {pt_end['name']}: insufficient or invalid data.")
        return
    
    s_start, t_start, p_start = pt_start_data
    s_end, t_end, p_end = pt_end_data
    
    if pt_end['type'] == "expansion":
        plt.plot([s_start, s_end], [t_start, t_end], linestyle='-', label=f'Expansion {pt_start["name"]} to {pt_end["name"]}')
        plt.scatter([s_start, s_end], [t_start, t_end])
        plt.text(s_start, t_start, f' {pt_start["name"]}', fontsize=10, va='bottom')
        plt.text(s_end, t_end, f' {pt_end["name"]}', fontsize=10, va='bottom')
        return

    pressures = np.linspace(p_start, p_end, n_points)
    temperatures = np.linspace(t_start, t_end, n_points)
    entropies = []

    for p, t in zip(pressures, temperatures):
        try:
            s = steam.s_pt(p, t)
            entropies.append(s)
        except Exception:
            entropies.append(np.nan)

    plt.plot(entropies, temperatures, linestyle='-', label=f'Line {pt_start["name"]} to {pt_end["name"]}')
    plt.scatter([entropies[0], entropies[-1]], [temperatures[0], temperatures[-1]])
    plt.text(entropies[0], temperatures[0], f' {pt_start["name"]}', fontsize=10, va='bottom')
    plt.text(entropies[-1], temperatures[-1], f' {pt_end["name"]}', fontsize=10, va='bottom')
    
def plot_ts_diagram_DH3E():
    
    plot_ts_saturated_lines()
    
    # Define DH3E plant points at 100RO
    dh3e_points = [
        {"name": "1", "p": 0.0714, "t": 39.4, "type": ""}, # Condenser
        {"name": "2", "h": 168, "t": 39.8, "type": ""}, # Condensate pump outlet
        {"name": "3", "h": 307.7, "t": 73.2, "type": ""}, # LP Heater 8
        {"name": "4", "h": 384.7, "t": 91.6, "type": ""}, # LP Heater 7
        {"name": "5", "h": 481.4, "t": 114.5, "type": ""}, # LP Heater 6
        {"name": "6", "h": 591.1, "t": 140.3, "type": ""}, # LP Heater 5
        {"name": "7", "p": 8.25, "t": 171.69, "type": ""}, # Dearator: Change 171.7 -> 171.69 to match saturation temperature lower limit
        {"name": "8", "h": 767.6, "t": 177.4, "type": ""}, # BFP
        {"name": "9", "h": 888.9, "t": 205.4, "type": ""}, # HP Heater 3
        {"name": "10", "h": 1130.4, "t": 259.1, "type": ""}, # HP Heater 2
        {"name": "11", "h": 1288, "t": 291.9, "type": ""}, # HP Heater 1
        {"name": "12", "p": 242.2, "t": 566, "type": ""}, # Main Steam     
        {"name": "13", "h": 2992.6, "p": 47.67, "type": "expansion"}, # Reheater inlet      
        {"name": "14", "t": 566, "p": 43.38, "type": ""}, # Reheater outlet
        {"name": "1", "p": 0.0714, "t": 39.4, "type": "expansion"}, # Condenser           
    ]
    # s = []
    # t = []
    # p = []
    # for pt in dh3e_points:
    #     s_i, t_i, p_i = get_point_data(pt, steam)
    #     if s is not None and t is not None:
    #         s.append(s_i)
    #         t.append(t_i)
    #         p.append(p_i)
    #         plt.plot(s_i, t_i, 'ko')  # Black circle
    #         plt.text(s_i, t_i, f" {pt['name']}", color='black', fontsize=10, va='bottom')
    #     else:
    #         print(Fore.RED + f"Could not plot point {pt['name']}: insufficient or invalid data.")
    # plt.plot(s, t, label='DH3E Points')
    
    # plot_ts_diagram_multiple_pressures(steam, [242.2, 302.2])
    
    for i in range(len(dh3e_points) - 1):
        pt_start = dh3e_points[i]
        pt_end = dh3e_points[i + 1]
        plot_line_between_points(steam, pt_start, pt_end)
    
    plt.title('T-S Diagram for DH3E plant')
    plt.grid(True)
    plt.legend()
    plt.show()
    
def main():
    while True:
        print(Fore.BLUE + "\nChoose a function:")
        print(Fore.LIGHTYELLOW_EX + "1. Water/Steam properties at pressure and temperature")
        print(Fore.LIGHTYELLOW_EX + "2. Water/Steam properties at pressure and ideal entropy")
        print(Fore.LIGHTYELLOW_EX + "3. Water/Steam properties at enthalpy and temperature")
        print(Fore.LIGHTYELLOW_EX + "4. Plot T-S diagram at pressure")
        print(Fore.LIGHTYELLOW_EX + "5. Plot T-S diagram at multiple pressures")
        print(Fore.LIGHTYELLOW_EX + "6. Pump efficiency by thermodynamic method")
        print(Fore.LIGHTYELLOW_EX + "7. Plot T-S diagram for DH3E plant points")
        print(Fore.LIGHTYELLOW_EX + "8. Find pressure for given enthalpy and temperature")
        print(Fore.LIGHTYELLOW_EX + "0. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            p = float(input("Enter pressure (bar): "))
            t = float(input("Enter temperature (°C): "))
            print(f"Saturation Temperature: {Fore.CYAN}{steam.tsat_p(p)}{Style.RESET_ALL} °C")
            print(f"------------------------------------------")
            print(f"Entropy of Saturated Liquid: {steam.sL_p(p)} kJ/(kg K)")
            print(f"Enthalpy of Saturated Liquid: {steam.hL_p(p)} kJ/kg")
            print(f"------------------------------------------")
            print(f"Entropy of Saturated Vapor: {steam.sV_p(p)} kJ/(kg K)")
            print(f"Enthalpy of Saturated Vapor: {steam.hV_p(p)} kJ/kg")
            print(f"------------------------------------------")
            if t < steam.tsat_p(p):
                print(f"Phase of water at {p} bar and {t} °C: Compressed Liquid")
            elif t == steam.tsat_p(p):
                print(f"Phase of water at {p} bar and {t} °C: Saturated Liquid/Vapor Mixture")
            else:
                print(f"Phase of water at {p} bar and {t} °C: Superheated Vapor")
            print(f"Entropy at {Fore.CYAN}{p}{Style.RESET_ALL} bar and {Fore.CYAN}{t}{Style.RESET_ALL} °C: {Fore.GREEN}{steam.s_pt(p, t)}{Style.RESET_ALL} kJ/(kg K)") # Returns saturated vapor enthalpy if mixture
            print(f"Enthalpy at {Fore.CYAN}{p}{Style.RESET_ALL} bar and {Fore.CYAN}{t}{Style.RESET_ALL} °C: {Fore.GREEN}{steam.h_pt(p, t)}{Style.RESET_ALL} kJ/kg")
        elif choice == "2":
            p = float(input("Enter pressure (bar): "))
            s = float(input("Enter entropy (kJ/(kg K)): "))
            print(f"Temperature at {Fore.CYAN}{p}{Style.RESET_ALL} bar and {Fore.CYAN}{s}{Style.RESET_ALL} kJ/(kg K): {Fore.GREEN}{steam.t_ps(p, s)}{Style.RESET_ALL} °C")
            print(f"Enthalpy at {Fore.CYAN}{p}{Style.RESET_ALL} bar and {Fore.CYAN}{s}{Style.RESET_ALL} kJ/(kg K): {Fore.GREEN}{steam.h_ps(p, s)}{Style.RESET_ALL} kJ/kg")
        elif choice == "3":
            h = float(input("Enter enthalpy (kJ/kg): "))
            t = float(input("Enter temperature (°C): "))
            p = find_pressure_for_ht(steam, h, t)
            if p is not None:
                print(f"Pressure at {h} kJ/kg and {t} °C: {Fore.GREEN}{p}{Style.RESET_ALL} bar")
                print(f"Entropy at {p} bar and {t} °C: {Fore.GREEN}{steam.s_pt(p, t)}{Style.RESET_ALL} kJ/(kg K)")
            else:
                print(Fore.RED + "No valid pressure found for the given enthalpy and temperature.")
        elif choice == "4":
            p = float(input("Enter pressure (bar): "))
            plot_ts_diagram_multiple_pressures(steam, [p])
            plt.title('T-S Diagram at Multiple Pressures')
            plt.grid(True)
            plt.legend()
            plt.show()
        elif choice == "5":
            pressures = [1, 20, 50, 80, 100, 200, 300, 400]
            plot_ts_diagram_multiple_pressures(steam, pressures)
            plt.title('T-S Diagram at Multiple Pressures')
            plt.grid(True)
            plt.legend()
            plt.show()
        elif choice == "6":
            p1 = float(input("Enter inlet pressure (bar): "))
            t1 = float(input("Enter inlet temperature (°C): "))
            p2 = float(input("Enter outlet pressure (bar): "))
            t2 = float(input("Enter outlet temperature (°C): "))
            tsatp1 = steam.tsat_p(p1)
            if t1 < tsatp1:
                s1 = steam.s_pt(p1, t1)
                print(f"Entropy at inlet: {s1} kJ/(kg K)")
                h1 = steam.h_pt(p1, t1)
                print(f"Enthalpy at inlet: {h1} kJ/kg")
                h2 = steam.h_pt(p2, t2)
                h2_ideal = steam.h_ps(p2, s1)  # Ideal enthalpy at outlet
                efficiency = (h2_ideal - h1) / (h2 - h1) * 100
                print(f"Actual enthalpy at outlet: {h2} kJ/kg")
                print(f"Ideal enthalpy at outlet: {h2_ideal} kJ/kg")
                print(f"Pump efficiency: {efficiency:.2f}%")
            else:
                print(Fore.RED + f"Inlet temperature is above saturation temperature {Fore.CYAN}{tsatp1}{Style.RESET_ALL}, cannot calculate pump efficiency in this region.")
        elif choice == "7":
            print(Fore.BLUE + "Plotting T-S diagram for DH3E plant points...")
            plot_ts_diagram_DH3E()
        elif choice == "8":
            s = float(input("Enter entropy (kJ/(kg K)): "))
            t = float(input("Enter temperature (°C): "))
            p = find_pressure_for_st(steam, s, t)
            if p is not None:
                print(f"Pressure at {s} kJ/(kg K) and {t} °C: {Fore.GREEN}{p}{Style.RESET_ALL} bar")
                print(f"Enthalpy at {p} bar and {t} °C: {Fore.GREEN}{steam.h_pt(p, t)}{Style.RESET_ALL} kJ/kg")
            else:
                print(Fore.RED + "No valid pressure found for the given entropy and temperature.")
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print(Fore.RED + "Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
    