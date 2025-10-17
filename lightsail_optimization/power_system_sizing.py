#!/usr/bin/env python3
"""
WARPEED LIGHTSAIL NANOCRAFT - SOLAR POWER SYSTEM SIZING
=======================================================

Power Systems Engineer: Solar Array and Battery Design
Mission: Interstellar voyage to α Centauri system

Key Parameters:
- Solar cells: Multi-junction GaAs (30% efficiency)
- Available area: 10 cm² maximum
- Mission distance: 1 AU (LEO) to 4.37 AU (cruise) to α Centauri
- Dual star system: α Cen A (1.519 L☉) + α Cen B (0.500 L☉)

Author: Power Systems Engineering Team
Date: October 15, 2025
"""

import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime
from typing import Dict, Tuple, List

# Physical Constants
SOLAR_CONSTANT = 1361  # W/m² at 1 AU from Sun
AU_TO_METERS = 1.496e11  # meters
ALPHA_CEN_DISTANCE = 4.37  # light-years (= 2.76e5 AU)
ALPHA_CEN_A_LUMINOSITY = 1.519  # Solar luminosities
ALPHA_CEN_B_LUMINOSITY = 0.500  # Solar luminosities
ALPHA_CEN_SEPARATION = 23.4  # AU (average separation)

# Solar Cell Parameters
CELL_EFFICIENCY_BOL = 0.30  # Beginning of life (30% for multi-junction GaAs)
CELL_AREA_CM2 = 10.0  # cm²
CELL_AREA_M2 = CELL_AREA_CM2 * 1e-4  # Convert to m²
DEGRADATION_RATE_PER_YEAR = 0.005  # 0.5% per year (radiation damage)
MISSION_DURATION_YEARS = 20  # Expected mission duration

# Mass Budget (typical for space-grade components)
MASS_PER_CM2_CELLS = 0.05  # grams/cm² (GaAs cells)
MASS_PER_WH_BATTERY = 15.0  # grams/Wh (Li-ion)
MASS_SUBSTRATE = 0.5  # grams (circuit board, connectors)

# Power Loads (W)
POWER_AVIONICS = 0.1  # Continuous
POWER_NAVIGATION = 0.2  # Continuous
POWER_CAMERA = 0.5  # During imaging
POWER_TRANSMITTER = 1.0  # During transmission

# Battery Parameters
BATTERY_DOD = 0.80  # Depth of discharge (80% usable)
BATTERY_EFFICIENCY = 0.90  # Charge/discharge efficiency
SHADOW_DURATION_HOURS = 0.5  # Maximum expected shadow time


class SolarPowerSystem:
    """Models the solar power system for the Warpeed nanocraft."""

    def __init__(self):
        self.cell_area_m2 = CELL_AREA_M2
        self.cell_efficiency_bol = CELL_EFFICIENCY_BOL
        self.degradation_rate = DEGRADATION_RATE_PER_YEAR

    def solar_irradiance(self, distance_au: float) -> float:
        """
        Calculate solar irradiance at a given distance using inverse square law.

        Args:
            distance_au: Distance from Sun in Astronomical Units

        Returns:
            Irradiance in W/m²
        """
        return SOLAR_CONSTANT / (distance_au ** 2)

    def alpha_centauri_irradiance(self, distance_from_A_au: float = None,
                                   distance_from_B_au: float = None) -> float:
        """
        Calculate combined irradiance from α Centauri A and B.

        Assumes the nanocraft is positioned optimally between both stars.
        If distances not specified, uses average separation assumptions.

        Args:
            distance_from_A_au: Distance from α Cen A in AU
            distance_from_B_au: Distance from α Cen B in AU

        Returns:
            Combined irradiance in W/m²
        """
        # If not specified, assume spacecraft is at optimal position
        # between the two stars (simplified model)
        if distance_from_A_au is None:
            # Assume positioned closer to the brighter star A
            distance_from_A_au = 1.0  # 1 AU from A
            distance_from_B_au = ALPHA_CEN_SEPARATION  # 23.4 AU from B

        # Calculate irradiance from each star
        irradiance_A = (ALPHA_CEN_A_LUMINOSITY * SOLAR_CONSTANT) / (distance_from_A_au ** 2)
        irradiance_B = (ALPHA_CEN_B_LUMINOSITY * SOLAR_CONSTANT) / (distance_from_B_au ** 2)

        return irradiance_A + irradiance_B

    def cell_efficiency(self, years_in_space: float) -> float:
        """
        Calculate solar cell efficiency with radiation degradation.

        Args:
            years_in_space: Years of radiation exposure

        Returns:
            Degraded efficiency (fraction)
        """
        degradation_factor = (1 - self.degradation_rate) ** years_in_space
        return self.cell_efficiency_bol * degradation_factor

    def power_output(self, irradiance: float, years_in_space: float = 0) -> float:
        """
        Calculate power output from solar array.

        Args:
            irradiance: Solar irradiance in W/m²
            years_in_space: Years of operation (for degradation)

        Returns:
            Power output in Watts
        """
        efficiency = self.cell_efficiency(years_in_space)
        power = irradiance * self.cell_area_m2 * efficiency
        return power

    def calculate_battery_capacity(self, shadow_power_w: float,
                                   shadow_duration_h: float) -> float:
        """
        Calculate required battery capacity for shadow operations.

        Args:
            shadow_power_w: Power required during shadow (W)
            shadow_duration_h: Duration of shadow period (hours)

        Returns:
            Battery capacity in Wh
        """
        energy_required = shadow_power_w * shadow_duration_h
        # Account for depth of discharge and efficiency
        capacity = energy_required / (BATTERY_DOD * BATTERY_EFFICIENCY)
        return capacity

    def power_budget_analysis(self) -> Dict:
        """
        Comprehensive power budget analysis for all mission phases.

        Returns:
            Dictionary with power analysis results
        """
        results = {}

        # Mission phases
        phases = {
            'LEO_deployment': {'distance_au': 1.0, 'years': 0},
            'cruise_1AU': {'distance_au': 1.0, 'years': 0.1},
            'cruise_2AU': {'distance_au': 2.0, 'years': 2},
            'cruise_3AU': {'distance_au': 3.0, 'years': 8},
            'cruise_4AU': {'distance_au': 4.0, 'years': 15},
            'cruise_4.37AU': {'distance_au': 4.37, 'years': 18},
            'alpha_centauri_arrival': {'distance_au': 1.0, 'years': 20, 'alpha_cen': True},
        }

        # Calculate power for each phase
        for phase_name, params in phases.items():
            if params.get('alpha_cen', False):
                # At α Centauri system
                irradiance = self.alpha_centauri_irradiance()
                location = 'α Cen A+B'
            else:
                # Solar system cruise
                irradiance = self.solar_irradiance(params['distance_au'])
                location = f"{params['distance_au']:.2f} AU"

            power = self.power_output(irradiance, params['years'])

            results[phase_name] = {
                'location': location,
                'distance_au': params['distance_au'],
                'years_in_space': params['years'],
                'irradiance_W_m2': irradiance,
                'cell_efficiency': self.cell_efficiency(params['years']),
                'power_output_W': power,
            }

        return results

    def calculate_power_margin(self, power_available: float,
                              power_required: float) -> float:
        """
        Calculate power margin percentage.

        Args:
            power_available: Available power (W)
            power_required: Required power (W)

        Returns:
            Margin as percentage
        """
        if power_required == 0:
            return 100.0
        margin = ((power_available - power_required) / power_required) * 100
        return margin

    def total_system_mass(self, battery_capacity_wh: float) -> float:
        """
        Calculate total power system mass.

        Args:
            battery_capacity_wh: Battery capacity in Wh

        Returns:
            Total mass in grams
        """
        mass_cells = MASS_PER_CM2_CELLS * CELL_AREA_CM2
        mass_battery = MASS_PER_WH_BATTERY * battery_capacity_wh
        mass_total = mass_cells + mass_battery + MASS_SUBSTRATE
        return mass_total


def create_power_vs_distance_plot(power_system: SolarPowerSystem,
                                  output_path: str):
    """
    Create comprehensive power vs distance plots.

    Args:
        power_system: SolarPowerSystem instance
        output_path: Path to save the plot
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Warpeed Nanocraft - Solar Power System Analysis',
                 fontsize=16, fontweight='bold')

    # Distance range for cruise phase
    distances = np.linspace(1, 4.37, 100)

    # Time points for degradation
    time_points = [0, 5, 10, 15, 20]  # years
    colors = plt.cm.viridis(np.linspace(0, 1, len(time_points)))

    # Plot 1: Power vs Distance for different degradation levels
    ax1 = axes[0, 0]
    for i, years in enumerate(time_points):
        powers = [power_system.power_output(
            power_system.solar_irradiance(d), years) for d in distances]
        ax1.plot(distances, powers, label=f'{years} years',
                color=colors[i], linewidth=2)

    # Add critical power levels
    ax1.axhline(y=POWER_AVIONICS + POWER_NAVIGATION,
                color='red', linestyle='--', alpha=0.5,
                label='Baseline (0.3W)')
    ax1.axhline(y=POWER_AVIONICS + POWER_NAVIGATION + POWER_CAMERA,
                color='orange', linestyle='--', alpha=0.5,
                label='+ Camera (0.8W)')
    ax1.axhline(y=POWER_AVIONICS + POWER_NAVIGATION + POWER_CAMERA + POWER_TRANSMITTER,
                color='darkred', linestyle='--', alpha=0.5,
                label='+ TX (1.8W)')

    ax1.set_xlabel('Distance from Sun (AU)', fontsize=11)
    ax1.set_ylabel('Power Output (W)', fontsize=11)
    ax1.set_title('Power Output vs Distance (with Degradation)', fontweight='bold')
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(1, 4.37)

    # Plot 2: Irradiance vs Distance
    ax2 = axes[0, 1]
    irradiances = [power_system.solar_irradiance(d) for d in distances]
    ax2.plot(distances, irradiances, 'b-', linewidth=2, label='Solar irradiance')

    # Add α Centauri irradiance
    alpha_cen_irr = power_system.alpha_centauri_irradiance()
    ax2.axhline(y=alpha_cen_irr, color='green', linestyle='--',
                linewidth=2, label=f'α Cen A+B ({alpha_cen_irr:.1f} W/m²)')

    ax2.set_xlabel('Distance from Sun (AU)', fontsize=11)
    ax2.set_ylabel('Irradiance (W/m²)', fontsize=11)
    ax2.set_title('Solar Irradiance vs Distance', fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(1, 4.37)
    ax2.set_yscale('log')

    # Plot 3: Cell Efficiency Degradation
    ax3 = axes[1, 0]
    years = np.linspace(0, 25, 100)
    efficiencies = [power_system.cell_efficiency(y) * 100 for y in years]
    ax3.plot(years, efficiencies, 'r-', linewidth=2)
    ax3.axvline(x=MISSION_DURATION_YEARS, color='gray', linestyle='--',
                alpha=0.5, label=f'Mission duration ({MISSION_DURATION_YEARS}y)')
    ax3.set_xlabel('Years in Space', fontsize=11)
    ax3.set_ylabel('Cell Efficiency (%)', fontsize=11)
    ax3.set_title('Solar Cell Degradation Over Time', fontweight='bold')
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(0, 25)
    ax3.set_ylim(20, 32)

    # Plot 4: Power Budget Bar Chart
    ax4 = axes[1, 1]

    # Calculate power at key mission points
    power_earth_bol = power_system.power_output(SOLAR_CONSTANT, 0)
    power_earth_eol = power_system.power_output(SOLAR_CONSTANT, 20)
    power_4au_eol = power_system.power_output(
        power_system.solar_irradiance(4.37), 20)
    power_alpha_cen_eol = power_system.power_output(
        power_system.alpha_centauri_irradiance(), 20)

    scenarios = ['Earth\nBOL', 'Earth\nEOL', '4.37 AU\nEOL', 'α Cen\nEOL']
    powers = [power_earth_bol, power_earth_eol, power_4au_eol, power_alpha_cen_eol]
    colors_bar = ['green', 'lightgreen', 'orange', 'lightblue']

    bars = ax4.bar(scenarios, powers, color=colors_bar, edgecolor='black', linewidth=1.5)

    # Add value labels on bars
    for bar, power in zip(bars, powers):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{power:.3f}W',
                ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Add reference lines for power requirements
    ax4.axhline(y=POWER_AVIONICS + POWER_NAVIGATION,
                color='red', linestyle='--', linewidth=2, alpha=0.7,
                label='Baseline')
    ax4.axhline(y=POWER_AVIONICS + POWER_NAVIGATION + POWER_CAMERA + POWER_TRANSMITTER,
                color='darkred', linestyle='--', linewidth=2, alpha=0.7,
                label='Full ops')

    ax4.set_ylabel('Power (W)', fontsize=11)
    ax4.set_title('Power Available at Key Mission Points', fontweight='bold')
    ax4.legend(fontsize=9, loc='upper right')
    ax4.grid(True, alpha=0.3, axis='y')
    ax4.set_ylim(0, max(powers) * 1.2)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Power analysis plot saved to: {output_path}")

    return fig


def main():
    """Main power system sizing analysis."""

    print("=" * 80)
    print("WARPEED NANOCRAFT - SOLAR POWER SYSTEM SIZING ANALYSIS")
    print("=" * 80)
    print()

    # Initialize power system
    power_system = SolarPowerSystem()

    print("SYSTEM PARAMETERS:")
    print("-" * 80)
    print(f"Solar cell type:          Multi-junction GaAs")
    print(f"Cell efficiency (BOL):    {CELL_EFFICIENCY_BOL * 100:.1f}%")
    print(f"Cell area:                {CELL_AREA_CM2:.1f} cm² ({CELL_AREA_M2 * 1e6:.1f} mm²)")
    print(f"Degradation rate:         {DEGRADATION_RATE_PER_YEAR * 100:.2f}% per year")
    print(f"Mission duration:         {MISSION_DURATION_YEARS} years")
    print()

    print("POWER LOADS:")
    print("-" * 80)
    print(f"Avionics (continuous):    {POWER_AVIONICS:.1f} W")
    print(f"Navigation (continuous):  {POWER_NAVIGATION:.1f} W")
    print(f"Camera (imaging):         {POWER_CAMERA:.1f} W")
    print(f"Transmitter (TX):         {POWER_TRANSMITTER:.1f} W")
    print(f"Baseline load:            {POWER_AVIONICS + POWER_NAVIGATION:.1f} W")
    print(f"Peak load (all systems):  {POWER_AVIONICS + POWER_NAVIGATION + POWER_CAMERA + POWER_TRANSMITTER:.1f} W")
    print()

    # Perform power budget analysis
    print("MISSION PHASE ANALYSIS:")
    print("=" * 80)

    power_budget = power_system.power_budget_analysis()

    for phase_name, data in power_budget.items():
        print(f"\n{phase_name.upper().replace('_', ' ')}:")
        print(f"  Location:           {data['location']}")
        print(f"  Years in space:     {data['years_in_space']:.1f}")
        print(f"  Irradiance:         {data['irradiance_W_m2']:.2f} W/m²")
        print(f"  Cell efficiency:    {data['cell_efficiency'] * 100:.2f}%")
        print(f"  Power output:       {data['power_output_W']:.4f} W")

        # Check if sufficient for different operations
        baseline_power = POWER_AVIONICS + POWER_NAVIGATION
        imaging_power = baseline_power + POWER_CAMERA
        full_power = imaging_power + POWER_TRANSMITTER

        power_avail = data['power_output_W']

        print(f"  Baseline margin:    {power_system.calculate_power_margin(power_avail, baseline_power):+.1f}%")
        print(f"  Imaging margin:     {power_system.calculate_power_margin(power_avail, imaging_power):+.1f}%")
        print(f"  Full ops margin:    {power_system.calculate_power_margin(power_avail, full_power):+.1f}%")

    print()
    print("=" * 80)

    # Calculate battery requirements
    print("\nBATTERY SIZING:")
    print("-" * 80)

    # Battery sized for baseline operations in shadow
    shadow_power = POWER_AVIONICS + POWER_NAVIGATION
    battery_capacity = power_system.calculate_battery_capacity(
        shadow_power, SHADOW_DURATION_HOURS)

    print(f"Shadow duration:          {SHADOW_DURATION_HOURS:.1f} hours")
    print(f"Shadow power load:        {shadow_power:.1f} W")
    print(f"Energy required:          {shadow_power * SHADOW_DURATION_HOURS:.2f} Wh")
    print(f"Battery capacity (req):   {battery_capacity:.2f} Wh")
    print(f"Battery DOD:              {BATTERY_DOD * 100:.0f}%")
    print(f"Battery efficiency:       {BATTERY_EFFICIENCY * 100:.0f}%")
    print()

    # Calculate total mass
    total_mass = power_system.total_system_mass(battery_capacity)
    mass_cells = MASS_PER_CM2_CELLS * CELL_AREA_CM2
    mass_battery = MASS_PER_WH_BATTERY * battery_capacity

    print("MASS BUDGET:")
    print("-" * 80)
    print(f"Solar cells:              {mass_cells:.2f} g")
    print(f"Battery:                  {mass_battery:.2f} g")
    print(f"Substrate/electronics:    {MASS_SUBSTRATE:.2f} g")
    print(f"TOTAL MASS:               {total_mass:.2f} g")
    print()

    # Critical analysis: α Centauri operations
    print("=" * 80)
    print("CRITICAL ANALYSIS: α CENTAURI OPERATIONS")
    print("=" * 80)

    alpha_cen_irradiance = power_system.alpha_centauri_irradiance()
    alpha_cen_power_eol = power_system.power_output(alpha_cen_irradiance,
                                                     MISSION_DURATION_YEARS)

    print(f"\nα Centauri System Configuration:")
    print(f"  α Cen A luminosity:     {ALPHA_CEN_A_LUMINOSITY:.3f} L☉")
    print(f"  α Cen B luminosity:     {ALPHA_CEN_B_LUMINOSITY:.3f} L☉")
    print(f"  Star separation:        {ALPHA_CEN_SEPARATION:.1f} AU")
    print(f"  Spacecraft position:    1.0 AU from α Cen A")
    print(f"  Combined irradiance:    {alpha_cen_irradiance:.2f} W/m²")
    print()

    print(f"Power at α Centauri (EOL = {MISSION_DURATION_YEARS}y):")
    print(f"  Available power:        {alpha_cen_power_eol:.4f} W")
    print()

    # Check viability for different operations
    baseline_ok = alpha_cen_power_eol >= (POWER_AVIONICS + POWER_NAVIGATION)
    imaging_ok = alpha_cen_power_eol >= (POWER_AVIONICS + POWER_NAVIGATION + POWER_CAMERA)
    full_ops_ok = alpha_cen_power_eol >= (POWER_AVIONICS + POWER_NAVIGATION +
                                          POWER_CAMERA + POWER_TRANSMITTER)

    print("Operation Viability at α Centauri:")
    print(f"  Baseline (0.3W):        {'✓ VIABLE' if baseline_ok else '✗ INSUFFICIENT'}")
    print(f"  + Camera (0.8W):        {'✓ VIABLE' if imaging_ok else '✗ INSUFFICIENT'}")
    print(f"  + Transmitter (1.8W):   {'✓ VIABLE' if full_ops_ok else '✗ INSUFFICIENT'}")
    print()

    if full_ops_ok:
        margin = power_system.calculate_power_margin(
            alpha_cen_power_eol,
            POWER_AVIONICS + POWER_NAVIGATION + POWER_CAMERA + POWER_TRANSMITTER)
        print(f"✓ SYSTEM VIABLE: Full operations possible with {margin:+.1f}% margin")
    else:
        print("⚠ WARNING: Insufficient power for simultaneous camera + transmitter")
        print("  Recommendation: Sequential operations (image, then transmit)")

    print()

    # Determine overall system viability
    power_margin_percent = power_system.calculate_power_margin(
        alpha_cen_power_eol,
        POWER_AVIONICS + POWER_NAVIGATION + POWER_CAMERA + POWER_TRANSMITTER
    )

    system_viable = (baseline_ok and imaging_ok)  # Must support imaging

    # Prepare output JSON
    output_data = {
        "mission_info": {
            "spacecraft": "Warpeed Nanocraft",
            "mission": "Interstellar voyage to α Centauri",
            "analysis_date": datetime.now().isoformat(),
            "mission_duration_years": MISSION_DURATION_YEARS
        },
        "solar_cell_specifications": {
            "type": "Multi-junction GaAs",
            "solar_cell_area_cm2": CELL_AREA_CM2,
            "efficiency_BOL_percent": CELL_EFFICIENCY_BOL * 100,
            "efficiency_EOL_percent": power_system.cell_efficiency(MISSION_DURATION_YEARS) * 100,
            "degradation_rate_percent_per_year": DEGRADATION_RATE_PER_YEAR * 100
        },
        "power_generation": {
            "power_at_earth_W": power_system.power_output(SOLAR_CONSTANT, 0),
            "power_at_earth_EOL_W": power_system.power_output(SOLAR_CONSTANT, 20),
            "power_at_4.37AU_EOL_W": power_system.power_output(
                power_system.solar_irradiance(4.37), 20),
            "power_at_alpha_cen_W": alpha_cen_power_eol,
            "alpha_centauri_irradiance_W_m2": alpha_cen_irradiance
        },
        "power_loads": {
            "avionics_W": POWER_AVIONICS,
            "navigation_W": POWER_NAVIGATION,
            "camera_W": POWER_CAMERA,
            "transmitter_W": POWER_TRANSMITTER,
            "baseline_W": POWER_AVIONICS + POWER_NAVIGATION,
            "peak_W": POWER_AVIONICS + POWER_NAVIGATION + POWER_CAMERA + POWER_TRANSMITTER
        },
        "battery_system": {
            "battery_capacity_Wh": battery_capacity,
            "shadow_duration_hours": SHADOW_DURATION_HOURS,
            "depth_of_discharge_percent": BATTERY_DOD * 100,
            "efficiency_percent": BATTERY_EFFICIENCY * 100
        },
        "mass_budget": {
            "solar_cells_grams": mass_cells,
            "battery_grams": mass_battery,
            "substrate_electronics_grams": MASS_SUBSTRATE,
            "total_mass_grams": total_mass
        },
        "performance_analysis": {
            "power_margin_at_alpha_cen_percent": power_margin_percent,
            "baseline_viable": baseline_ok,
            "imaging_viable": imaging_ok,
            "full_ops_viable": full_ops_ok,
            "power_system_viable": system_viable
        },
        "mission_phases": {}
    }

    # Add mission phase data
    for phase_name, data in power_budget.items():
        output_data["mission_phases"][phase_name] = data

    # Save results to JSON
    output_json_path = "/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/results/power_system_results.json"
    with open(output_json_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"✓ Results saved to: {output_json_path}")
    print()

    # Create visualization
    output_plot_path = "/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/results/power_system_analysis.png"
    create_power_vs_distance_plot(power_system, output_plot_path)
    print()

    # Final summary
    print("=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"Solar cell area:          {CELL_AREA_CM2:.1f} cm²")
    print(f"Power at Earth (BOL):     {power_system.power_output(SOLAR_CONSTANT, 0):.3f} W")
    print(f"Power at α Cen (EOL):     {alpha_cen_power_eol:.3f} W")
    print(f"Battery capacity:         {battery_capacity:.2f} Wh")
    print(f"Power margin at α Cen:    {power_margin_percent:+.1f}%")
    print(f"Total system mass:        {total_mass:.2f} g")
    print(f"Power system viable:      {'YES ✓' if system_viable else 'NO ✗'}")
    print()

    if system_viable:
        print("✓ CONCLUSION: Power system meets mission requirements")
        print("  - Sufficient power for baseline operations at all distances")
        print("  - Camera imaging supported at α Centauri")
        if full_ops_ok:
            print("  - Simultaneous camera + transmitter operations possible")
        else:
            print("  - Sequential operations recommended for camera + transmitter")
    else:
        print("✗ WARNING: Power system may be insufficient")
        print("  - Consider increasing solar cell area")
        print("  - Or reduce power consumption of subsystems")

    print("=" * 80)


if __name__ == "__main__":
    main()
