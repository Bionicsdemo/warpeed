#!/usr/bin/env python3
"""
Communication Feasibility Analysis for Warpeed Lightsail Project

This script performs aggressive parameter sweeps to determine what is needed
for viable optical communication from α Centauri to Earth.

Author: Communication Systems Engineer
Date: 2025-10-15
"""

import numpy as np
import json
import matplotlib.pyplot as plt
from communication_link_budget import OpticalLinkBudget
import os


def calculate_required_transmitter_power(target_snr_dB=10.0):
    """
    Calculate required transmitter power for viable communication.

    Args:
        target_snr_dB: Target SNR in dB

    Returns:
        dict: Required power calculations
    """
    print("\n" + "="*70)
    print("CALCULATING REQUIRED TRANSMITTER POWER")
    print("="*70)

    # Baseline system
    link = OpticalLinkBudget()

    # Calculate current SNR and power
    snr_baseline = link.calculate_SNR()
    current_snr_dB = snr_baseline['SNR_dB']
    current_power_W = link.tx_power_W

    # Calculate required power increase
    snr_deficit_dB = target_snr_dB - current_snr_dB
    power_increase_linear = 10**(snr_deficit_dB / 10)
    required_power_W = current_power_W * power_increase_linear

    print(f"Current transmitter power: {current_power_W} W")
    print(f"Current SNR: {current_snr_dB:.2f} dB")
    print(f"Target SNR: {target_snr_dB} dB")
    print(f"SNR deficit: {snr_deficit_dB:.2f} dB")
    print(f"Required power increase: {power_increase_linear:.2e}x")
    print(f"Required transmitter power: {required_power_W:.2e} W ({required_power_W/1000:.2e} kW)")

    return {
        'current_power_W': current_power_W,
        'required_power_W': required_power_W,
        'required_power_kW': required_power_W / 1000,
        'power_increase_factor': power_increase_linear,
        'snr_deficit_dB': snr_deficit_dB
    }


def explore_high_power_scenarios():
    """
    Explore scenarios with very high transmitter power.
    """
    print("\n" + "="*70)
    print("HIGH POWER TRANSMITTER SCENARIOS")
    print("="*70)

    scenarios = []
    powers_W = [1, 10, 100, 1000, 10000, 100000, 1e6, 1e7, 1e8, 1e9, 1e10]  # Up to 10 GW

    for power in powers_W:
        link = OpticalLinkBudget()
        link.tx_power_W = power

        # Calculate performance
        snr = link.calculate_SNR()
        data_rate = link.calculate_data_rate()
        viability = link.assess_communication_viability()

        scenario = {
            'tx_power_W': power,
            'tx_power_kW': power / 1000,
            'tx_power_MW': power / 1e6,
            'SNR_dB': float(snr['SNR_dB']),
            'link_margin_dB': float(snr['link_margin_dB']),
            'data_rate_Mbps': float(data_rate['data_rate_Mbps']),
            'time_per_image_hours': float(data_rate['time_per_image_hours']),
            'viable': bool(viability['communication_viable'])
        }

        scenarios.append(scenario)

        if viability['communication_viable']:
            print(f"✓ {power:.2e} W ({power/1000:.2e} kW): VIABLE - SNR={snr['SNR_dB']:.2f} dB, "
                  f"Rate={data_rate['data_rate_Mbps']:.6f} Mbps")
        else:
            print(f"✗ {power:.2e} W ({power/1000:.2e} kW): Not viable - SNR={snr['SNR_dB']:.2f} dB")

    return scenarios


def explore_aperture_combinations():
    """
    Explore combinations of transmitter and receiver apertures.
    """
    print("\n" + "="*70)
    print("APERTURE COMBINATION EXPLORATION")
    print("="*70)

    scenarios = []
    tx_diameters = [1, 5, 10, 20, 50, 100]  # meters
    rx_diameters = [100, 200, 500, 1000]  # meters (including array concepts)

    for tx_d in tx_diameters:
        for rx_d in rx_diameters:
            link = OpticalLinkBudget()
            link.tx_power_W = 100.0  # Use moderate power
            link.tx_aperture_diameter_m = tx_d
            link.tx_aperture_area_m2 = np.pi * (tx_d / 2)**2
            link.rx_aperture_diameter_m = rx_d
            link.rx_aperture_area_m2 = np.pi * (rx_d / 2)**2
            link.atmospheric_transmission = 1.0  # Space receiver
            link.airmass = 1.0

            snr = link.calculate_SNR()
            data_rate = link.calculate_data_rate()
            viability = link.assess_communication_viability()

            scenario = {
                'tx_diameter_m': tx_d,
                'rx_diameter_m': rx_d,
                'SNR_dB': float(snr['SNR_dB']),
                'link_margin_dB': float(snr['link_margin_dB']),
                'data_rate_Mbps': float(data_rate['data_rate_Mbps']),
                'time_per_image_hours': float(data_rate['time_per_image_hours']),
                'viable': bool(viability['communication_viable'])
            }

            scenarios.append(scenario)

            if viability['communication_viable']:
                print(f"✓ TX={tx_d}m, RX={rx_d}m: VIABLE - SNR={snr['SNR_dB']:.2f} dB, "
                      f"Rate={data_rate['data_rate_Mbps']:.6f} Mbps")

    # Print summary of viable scenarios
    viable_scenarios = [s for s in scenarios if s['viable']]
    print(f"\nTotal viable scenarios: {len(viable_scenarios)} out of {len(scenarios)}")

    return scenarios


def calculate_minimum_viable_system():
    """
    Calculate the minimum system parameters needed for viable communication.
    """
    print("\n" + "="*70)
    print("MINIMUM VIABLE SYSTEM ANALYSIS")
    print("="*70)

    # Binary search for minimum power with fixed apertures
    print("\nFinding minimum power (TX=10m, RX=100m, Space)...")

    power_low = 1.0
    power_high = 1e12
    target_snr = 10.0
    tolerance = 0.1

    while (power_high - power_low) / power_low > 0.01:  # 1% tolerance
        power_mid = (power_low + power_high) / 2

        link = OpticalLinkBudget()
        link.tx_power_W = power_mid
        link.tx_aperture_diameter_m = 10.0
        link.tx_aperture_area_m2 = np.pi * (10.0 / 2)**2
        link.atmospheric_transmission = 1.0
        link.airmass = 1.0

        snr = link.calculate_SNR()
        snr_dB = snr['SNR_dB']

        if snr_dB < target_snr:
            power_low = power_mid
        else:
            power_high = power_mid

    min_power = power_high

    # Verify minimum power
    link = OpticalLinkBudget()
    link.tx_power_W = min_power
    link.tx_aperture_diameter_m = 10.0
    link.tx_aperture_area_m2 = np.pi * (10.0 / 2)**2
    link.atmospheric_transmission = 1.0
    link.airmass = 1.0

    snr = link.calculate_SNR()
    data_rate = link.calculate_data_rate()

    print(f"Minimum viable power: {min_power:.2e} W ({min_power/1000:.2e} kW, {min_power/1e6:.2e} MW)")
    print(f"SNR: {snr['SNR_dB']:.2f} dB")
    print(f"Data rate: {data_rate['data_rate_Mbps']:.6f} Mbps")
    print(f"Time per image: {data_rate['time_per_image_hours']:.2f} hours")

    return {
        'min_power_W': min_power,
        'min_power_kW': min_power / 1000,
        'min_power_MW': min_power / 1e6,
        'tx_diameter_m': 10.0,
        'rx_diameter_m': 100.0,
        'SNR_dB': float(snr['SNR_dB']),
        'data_rate_Mbps': float(data_rate['data_rate_Mbps']),
        'time_per_image_hours': float(data_rate['time_per_image_hours'])
    }


def generate_feasibility_plots(power_scenarios, aperture_scenarios, output_dir):
    """
    Generate comprehensive feasibility plots.
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    # Plot 1: SNR vs Transmitter Power
    powers = [s['tx_power_W'] for s in power_scenarios]
    snrs = [s['SNR_dB'] for s in power_scenarios]
    viable = [s['viable'] for s in power_scenarios]

    colors = ['green' if v else 'red' for v in viable]
    ax1.semilogx(powers, snrs, 'o-', markersize=8, linewidth=2, color='blue')
    ax1.scatter(powers, snrs, c=colors, s=100, edgecolors='black', zorder=3)
    ax1.axhline(y=10, color='green', linestyle='--', linewidth=2, label='Required SNR (10 dB)')
    ax1.set_xlabel('Transmitter Power (W)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('SNR (dB)', fontsize=12, fontweight='bold')
    ax1.set_title('SNR vs Transmitter Power\n(1m TX, 100m RX, Ground)', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # Plot 2: Data Rate vs Transmitter Power
    data_rates = [s['data_rate_Mbps'] for s in power_scenarios]
    ax2.loglog(powers, data_rates, 'o-', markersize=8, linewidth=2, color='purple')
    ax2.scatter(powers, data_rates, c=colors, s=100, edgecolors='black', zorder=3)
    ax2.set_xlabel('Transmitter Power (W)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Data Rate (Mbps)', fontsize=12, fontweight='bold')
    ax2.set_title('Achievable Data Rate vs Transmitter Power', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, which='both')

    # Plot 3: SNR heatmap for aperture combinations
    tx_diams = sorted(list(set([s['tx_diameter_m'] for s in aperture_scenarios])))
    rx_diams = sorted(list(set([s['rx_diameter_m'] for s in aperture_scenarios])))

    snr_matrix = np.zeros((len(rx_diams), len(tx_diams)))
    for s in aperture_scenarios:
        i = rx_diams.index(s['rx_diameter_m'])
        j = tx_diams.index(s['tx_diameter_m'])
        snr_matrix[i, j] = s['SNR_dB']

    im = ax3.imshow(snr_matrix, cmap='RdYlGn', aspect='auto', vmin=-100, vmax=20)
    ax3.set_xticks(range(len(tx_diams)))
    ax3.set_yticks(range(len(rx_diams)))
    ax3.set_xticklabels([f'{d}m' for d in tx_diams])
    ax3.set_yticklabels([f'{d}m' for d in rx_diams])
    ax3.set_xlabel('Transmitter Diameter', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Receiver Diameter', fontsize=12, fontweight='bold')
    ax3.set_title('SNR Heatmap (100W, Space Receiver)', fontsize=13, fontweight='bold')

    # Add text annotations
    for i in range(len(rx_diams)):
        for j in range(len(tx_diams)):
            text = ax3.text(j, i, f'{snr_matrix[i, j]:.0f}',
                           ha="center", va="center", color="black", fontsize=9, fontweight='bold')

    cbar = plt.colorbar(im, ax=ax3)
    cbar.set_label('SNR (dB)', fontsize=11, fontweight='bold')

    # Plot 4: Viable/not viable summary table
    ax4.axis('off')
    ax4.set_title('Communication Feasibility Summary', fontsize=13, fontweight='bold', pad=20)

    # Count viable scenarios at different power levels
    viable_1W = sum(1 for s in power_scenarios if s['tx_power_W'] == 1 and s['viable'])
    viable_100W = sum(1 for s in power_scenarios if s['tx_power_W'] == 100 and s['viable'])
    viable_1kW = sum(1 for s in power_scenarios if s['tx_power_W'] == 1000 and s['viable'])
    viable_1MW = sum(1 for s in power_scenarios if s['tx_power_W'] == 1e6 and s['viable'])

    viable_apertures = sum(1 for s in aperture_scenarios if s['viable'])
    total_apertures = len(aperture_scenarios)

    summary_text = f"""
    BASELINE SYSTEM (1W, 1m TX, 100m RX, Ground):
    • SNR: {power_scenarios[0]['SNR_dB']:.2f} dB (Need: 10 dB)
    • Deficit: {10 - power_scenarios[0]['SNR_dB']:.2f} dB
    • Viable: {'YES' if power_scenarios[0]['viable'] else 'NO'}

    POWER SCALING (1m TX, 100m RX, Ground):
    • 1 W: {'Viable' if viable_1W else 'Not viable'}
    • 100 W: {'Viable' if viable_100W else 'Not viable'}
    • 1 kW: {'Viable' if viable_1kW else 'Not viable'}
    • 1 MW: {'Viable' if viable_1MW else 'Not viable'}

    APERTURE OPTIMIZATION (100W, Space):
    • Viable configurations: {viable_apertures}/{total_apertures}
    • Best TX aperture: {max([s for s in aperture_scenarios if s['viable']], key=lambda x: x['SNR_dB'])['tx_diameter_m'] if viable_apertures > 0 else 'N/A'}m

    KEY FINDINGS:
    • Interstellar optical communication is EXTREMELY challenging
    • Requires MW-class transmitter power OR very large apertures
    • Space-based receiver essential for best performance
    • Alternative: Radio wavelengths provide better link budget
    """

    ax4.text(0.1, 0.5, summary_text, transform=ax4.transAxes,
             fontsize=10, verticalalignment='center',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
             family='monospace')

    plt.tight_layout()
    output_path = os.path.join(output_dir, 'communication_feasibility_analysis.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nFeasibility plots saved to: {output_path}")
    plt.close()


def main():
    """Main execution function."""

    print("\n" + "="*70)
    print("WARPEED LIGHTSAIL COMMUNICATION FEASIBILITY ANALYSIS")
    print("Complete analysis of requirements for α Centauri → Earth communication")
    print("="*70)

    # Calculate required power
    required_power = calculate_required_transmitter_power()

    # Explore high power scenarios
    power_scenarios = explore_high_power_scenarios()

    # Explore aperture combinations
    aperture_scenarios = explore_aperture_combinations()

    # Calculate minimum viable system
    min_system = calculate_minimum_viable_system()

    # Generate plots
    output_dir = '/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/results'
    generate_feasibility_plots(power_scenarios, aperture_scenarios, output_dir)

    # Save comprehensive results
    results = {
        'required_power_analysis': required_power,
        'minimum_viable_system': min_system,
        'power_sweep_scenarios': power_scenarios,
        'aperture_combinations': aperture_scenarios,
        'conclusions': {
            'baseline_viable': power_scenarios[0]['viable'],
            'baseline_snr_dB': power_scenarios[0]['SNR_dB'],
            'baseline_snr_deficit_dB': 10.0 - power_scenarios[0]['SNR_dB'],
            'min_viable_power_MW': min_system['min_power_MW'],
            'total_viable_configurations': sum(1 for s in aperture_scenarios if s['viable']),
            'recommendation': 'Use radio wavelengths (X-band or Ka-band) for better link budget'
        }
    }

    output_path = os.path.join(output_dir, 'communication_feasibility_results.json')
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nFeasibility results saved to: {output_path}")

    # Print final summary
    print("\n" + "="*70)
    print("FINAL CONCLUSIONS")
    print("="*70)
    print(f"\nBaseline System (1W, 1m TX, 100m RX):")
    print(f"  SNR: {power_scenarios[0]['SNR_dB']:.2f} dB")
    print(f"  SNR Deficit: {10.0 - power_scenarios[0]['SNR_dB']:.2f} dB")
    print(f"  Viable: {'YES' if power_scenarios[0]['viable'] else 'NO'}")

    print(f"\nMinimum Viable System:")
    print(f"  Transmitter Power: {min_system['min_power_MW']:.2e} MW")
    print(f"  Transmitter Diameter: {min_system['tx_diameter_m']} m")
    print(f"  Receiver Diameter: {min_system['rx_diameter_m']} m")
    print(f"  Location: Space-based receiver")
    print(f"  Data Rate: {min_system['data_rate_Mbps']:.6f} Mbps")
    print(f"  Time per Image: {min_system['time_per_image_hours']:.2f} hours")

    print(f"\nRECOMMENDATION:")
    print(f"  Optical communication at 1550nm from α Centauri is impractical")
    print(f"  with current technology. Consider:")
    print(f"  1. Radio wavelengths (X-band: 8-12 GHz) for ~40 dB better path loss")
    print(f"  2. Larger transmitter/receiver arrays")
    print(f"  3. Nuclear-powered transmitter (MW-class)")
    print(f"  4. Relay satellites closer to Earth")

    print("\n" + "="*70)

    return results


if __name__ == "__main__":
    main()
