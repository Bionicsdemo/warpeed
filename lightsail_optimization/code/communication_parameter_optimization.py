#!/usr/bin/env python3
"""
Communication Parameter Optimization for Warpeed Lightsail Project

This script explores different parameter combinations to achieve viable
optical communication from α Centauri to Earth.

Author: Communication Systems Engineer
Date: 2025-10-15
"""

import numpy as np
import json
import matplotlib.pyplot as plt
from communication_link_budget import OpticalLinkBudget
import os


class CommunicationParameterOptimizer:
    """
    Optimizes communication system parameters to achieve viable link.
    """

    def __init__(self):
        """Initialize optimizer."""
        self.scenarios = []

    def explore_scenarios(self):
        """
        Explore different parameter combinations to achieve viable communication.
        """
        print("\n" + "="*70)
        print("COMMUNICATION PARAMETER OPTIMIZATION")
        print("Exploring scenarios for viable α Centauri → Earth communication")
        print("="*70)

        # Scenario 1: Baseline (from requirements)
        print("\n--- Scenario 1: Baseline Parameters ---")
        scenario1 = OpticalLinkBudget()
        self.run_scenario("Baseline (1W, 1m TX, 100m RX)", scenario1)

        # Scenario 2: Increase transmitter power to 10W
        print("\n--- Scenario 2: Higher Transmitter Power ---")
        scenario2 = OpticalLinkBudget()
        scenario2.tx_power_W = 10.0
        self.run_scenario("10W Transmitter", scenario2)

        # Scenario 3: Increase transmitter power to 100W
        print("\n--- Scenario 3: Very High Transmitter Power ---")
        scenario3 = OpticalLinkBudget()
        scenario3.tx_power_W = 100.0
        self.run_scenario("100W Transmitter", scenario3)

        # Scenario 4: Larger transmitter aperture (10m)
        print("\n--- Scenario 4: Larger Transmitter Aperture ---")
        scenario4 = OpticalLinkBudget()
        scenario4.tx_aperture_diameter_m = 10.0
        scenario4.tx_aperture_area_m2 = np.pi * (scenario4.tx_aperture_diameter_m / 2)**2
        self.run_scenario("10m Transmitter Aperture", scenario4)

        # Scenario 5: Larger receiver (VLT or ELT class: 39m)
        print("\n--- Scenario 5: Extremely Large Telescope Receiver ---")
        scenario5 = OpticalLinkBudget()
        scenario5.rx_aperture_diameter_m = 39.0  # ELT size
        scenario5.rx_aperture_area_m2 = np.pi * (scenario5.rx_aperture_diameter_m / 2)**2
        self.run_scenario("ELT-class Receiver (39m)", scenario5)

        # Scenario 6: Combination - 100W, 10m TX, 100m RX
        print("\n--- Scenario 6: Optimized System ---")
        scenario6 = OpticalLinkBudget()
        scenario6.tx_power_W = 100.0
        scenario6.tx_aperture_diameter_m = 10.0
        scenario6.tx_aperture_area_m2 = np.pi * (scenario6.tx_aperture_diameter_m / 2)**2
        self.run_scenario("100W + 10m TX + 100m RX", scenario6)

        # Scenario 7: Space-based receiver (no atmosphere)
        print("\n--- Scenario 7: Space-Based Receiver ---")
        scenario7 = OpticalLinkBudget()
        scenario7.atmospheric_transmission = 1.0  # No atmosphere
        scenario7.airmass = 1.0
        scenario7.tx_power_W = 10.0
        scenario7.tx_aperture_diameter_m = 5.0
        scenario7.tx_aperture_area_m2 = np.pi * (scenario7.tx_aperture_diameter_m / 2)**2
        self.run_scenario("Space Receiver (10W, 5m TX, 100m RX)", scenario7)

        # Scenario 8: Ultimate system - space receiver with large TX
        print("\n--- Scenario 8: Ultimate Space-Based System ---")
        scenario8 = OpticalLinkBudget()
        scenario8.atmospheric_transmission = 1.0  # No atmosphere
        scenario8.airmass = 1.0
        scenario8.tx_power_W = 100.0
        scenario8.tx_aperture_diameter_m = 10.0
        scenario8.tx_aperture_area_m2 = np.pi * (scenario8.tx_aperture_diameter_m / 2)**2
        scenario8.rx_aperture_diameter_m = 100.0
        scenario8.rx_aperture_area_m2 = np.pi * (scenario8.rx_aperture_diameter_m / 2)**2
        self.run_scenario("Ultimate (100W, 10m TX, 100m RX, Space)", scenario8)

        return self.scenarios

    def run_scenario(self, name, link_budget):
        """
        Run a single scenario and record results.

        Args:
            name: Scenario name
            link_budget: OpticalLinkBudget instance with configured parameters
        """
        # Calculate all parameters
        rx_power = link_budget.calculate_received_power()
        snr = link_budget.calculate_SNR()
        data_rate = link_budget.calculate_data_rate()
        viability = link_budget.assess_communication_viability()

        # Store scenario results
        scenario_data = {
            'name': name,
            'parameters': {
                'tx_power_W': link_budget.tx_power_W,
                'tx_diameter_m': link_budget.tx_aperture_diameter_m,
                'rx_diameter_m': link_budget.rx_aperture_diameter_m,
                'atmospheric_transmission': link_budget.atmospheric_transmission,
            },
            'results': {
                'SNR_dB': float(snr['SNR_dB']),
                'link_margin_dB': float(snr['link_margin_dB']),
                'data_rate_bps': float(data_rate['data_rate_bps']),
                'data_rate_Mbps': float(data_rate['data_rate_Mbps']),
                'time_per_image_hours': float(data_rate['time_per_image_hours']),
                'images_per_year': float(data_rate['images_per_year']),
                'viable': bool(viability['communication_viable']),
            }
        }

        self.scenarios.append(scenario_data)

        # Print summary
        print(f"TX Power: {link_budget.tx_power_W}W, "
              f"TX Diameter: {link_budget.tx_aperture_diameter_m}m, "
              f"RX Diameter: {link_budget.rx_aperture_diameter_m}m")
        print(f"SNR: {snr['SNR_dB']:.2f} dB, "
              f"Data Rate: {data_rate['data_rate_Mbps']:.6f} Mbps, "
              f"Viable: {viability['communication_viable']}")

    def generate_comparison_plots(self, output_path):
        """
        Generate comparison plots of different scenarios.

        Args:
            output_path: Path to save comparison plot
        """
        if not self.scenarios:
            print("No scenarios to plot!")
            return

        # Extract data
        names = [s['name'] for s in self.scenarios]
        snr_values = [s['results']['SNR_dB'] for s in self.scenarios]
        data_rates = [s['results']['data_rate_Mbps'] for s in self.scenarios]
        viable = [s['results']['viable'] for s in self.scenarios]
        time_per_image = [s['results']['time_per_image_hours'] for s in self.scenarios]

        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        # Plot 1: SNR comparison
        colors = ['green' if v else 'red' for v in viable]
        bars1 = ax1.barh(names, snr_values, color=colors, alpha=0.7, edgecolor='black')
        ax1.axvline(x=10, color='blue', linestyle='--', linewidth=2, label='Required SNR (10 dB)')
        ax1.set_xlabel('SNR (dB)', fontsize=11, fontweight='bold')
        ax1.set_title('Signal-to-Noise Ratio by Scenario', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')
        ax1.legend()

        # Add value labels
        for i, (bar, val) in enumerate(zip(bars1, snr_values)):
            ax1.text(val, bar.get_y() + bar.get_height()/2,
                    f' {val:.1f} dB', va='center', fontsize=9, fontweight='bold')

        # Plot 2: Data Rate comparison (log scale)
        bars2 = ax2.barh(names, data_rates, color=colors, alpha=0.7, edgecolor='black')
        ax2.set_xlabel('Data Rate (Mbps)', fontsize=11, fontweight='bold')
        ax2.set_xscale('log')
        ax2.set_title('Achievable Data Rate by Scenario', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x', which='both')

        # Add value labels
        for i, (bar, val) in enumerate(zip(bars2, data_rates)):
            ax2.text(val * 1.5, bar.get_y() + bar.get_height()/2,
                    f'{val:.2e}', va='center', fontsize=8)

        # Plot 3: Time per image (log scale)
        bars3 = ax3.barh(names, time_per_image, color=colors, alpha=0.7, edgecolor='black')
        ax3.set_xlabel('Time per Image (hours)', fontsize=11, fontweight='bold')
        ax3.set_xscale('log')
        ax3.set_title('Image Transmission Time by Scenario', fontsize=13, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='x', which='both')

        # Add value labels
        for i, (bar, val) in enumerate(zip(bars3, time_per_image)):
            ax3.text(val * 1.5, bar.get_y() + bar.get_height()/2,
                    f'{val:.1f}h', va='center', fontsize=8)

        # Plot 4: Parameter comparison table
        ax4.axis('off')
        ax4.set_title('Scenario Parameter Summary', fontsize=13, fontweight='bold', pad=20)

        table_data = [['Scenario', 'TX\nPower\n(W)', 'TX\nDiam\n(m)', 'RX\nDiam\n(m)',
                       'Atm', 'SNR\n(dB)', 'Rate\n(Mbps)', 'Viable']]

        for s in self.scenarios:
            atm_str = 'Space' if s['parameters']['atmospheric_transmission'] >= 0.99 else 'Ground'
            viable_str = 'YES' if s['results']['viable'] else 'NO'
            row = [
                s['name'][:20] + '...' if len(s['name']) > 20 else s['name'],
                f"{s['parameters']['tx_power_W']:.0f}",
                f"{s['parameters']['tx_diameter_m']:.1f}",
                f"{s['parameters']['rx_diameter_m']:.0f}",
                atm_str,
                f"{s['results']['SNR_dB']:.1f}",
                f"{s['results']['data_rate_Mbps']:.2e}",
                viable_str
            ]
            table_data.append(row)

        table = ax4.table(cellText=table_data, cellLoc='center',
                         bbox=[0, 0, 1, 1], edges='closed')
        table.auto_set_font_size(False)
        table.set_fontsize(8)

        # Style header row
        for i in range(8):
            cell = table[(0, i)]
            cell.set_facecolor('lightblue')
            cell.set_text_props(weight='bold', fontsize=9)

        # Color code viable/not viable
        for i in range(1, len(table_data)):
            viable_cell = table[(i, 7)]
            if table_data[i][7] == 'YES':
                viable_cell.set_facecolor('lightgreen')
                viable_cell.set_text_props(weight='bold')
            else:
                viable_cell.set_facecolor('lightcoral')
                viable_cell.set_text_props(weight='bold')

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\nComparison plots saved to: {output_path}")
        plt.close()

    def save_results(self, output_dir):
        """
        Save scenario comparison results to JSON.

        Args:
            output_dir: Directory to save results
        """
        output_path = os.path.join(output_dir, 'communication_optimization_results.json')

        # Find best scenario
        viable_scenarios = [s for s in self.scenarios if s['results']['viable']]

        if viable_scenarios:
            # Best = highest data rate among viable scenarios
            best_scenario = max(viable_scenarios, key=lambda s: s['results']['data_rate_bps'])
            recommendation = {
                'viable_communication_possible': True,
                'best_scenario': best_scenario['name'],
                'best_parameters': best_scenario['parameters'],
                'best_results': best_scenario['results'],
                'total_viable_scenarios': len(viable_scenarios),
            }
        else:
            # Find closest to viable (highest SNR)
            best_scenario = max(self.scenarios, key=lambda s: s['results']['SNR_dB'])
            recommendation = {
                'viable_communication_possible': False,
                'closest_scenario': best_scenario['name'],
                'closest_parameters': best_scenario['parameters'],
                'closest_results': best_scenario['results'],
                'snr_deficit_dB': 10.0 - best_scenario['results']['SNR_dB'],
            }

        results = {
            'summary': recommendation,
            'all_scenarios': self.scenarios
        }

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"Optimization results saved to: {output_path}")

        # Print recommendation
        print("\n" + "="*70)
        print("RECOMMENDATION")
        print("="*70)

        if recommendation['viable_communication_possible']:
            print(f"VIABLE COMMUNICATION IS POSSIBLE!")
            print(f"\nRecommended Configuration: {recommendation['best_scenario']}")
            print(f"Parameters:")
            print(f"  - Transmitter Power: {recommendation['best_parameters']['tx_power_W']:.0f} W")
            print(f"  - Transmitter Diameter: {recommendation['best_parameters']['tx_diameter_m']:.1f} m")
            print(f"  - Receiver Diameter: {recommendation['best_parameters']['rx_diameter_m']:.0f} m")
            print(f"  - Location: {'Space' if recommendation['best_parameters']['atmospheric_transmission'] >= 0.99 else 'Ground'}")
            print(f"\nPerformance:")
            print(f"  - SNR: {recommendation['best_results']['SNR_dB']:.2f} dB")
            print(f"  - Link Margin: {recommendation['best_results']['link_margin_dB']:.2f} dB")
            print(f"  - Data Rate: {recommendation['best_results']['data_rate_Mbps']:.6f} Mbps")
            print(f"  - Time per Image: {recommendation['best_results']['time_per_image_hours']:.2f} hours")
            print(f"  - Images per Year: {recommendation['best_results']['images_per_year']:.1f}")
        else:
            print(f"VIABLE COMMUNICATION NOT ACHIEVED with tested configurations.")
            print(f"\nClosest Configuration: {recommendation['closest_scenario']}")
            print(f"SNR Deficit: {recommendation['snr_deficit_dB']:.2f} dB")
            print(f"\nSuggestions to achieve viability:")
            print(f"  - Further increase transmitter power")
            print(f"  - Use larger transmitter aperture")
            print(f"  - Deploy space-based receiver")
            print(f"  - Use receiver array (multiple telescopes)")

        return results


def main():
    """Main execution function."""

    print("\n" + "="*70)
    print("WARPEED LIGHTSAIL COMMUNICATION OPTIMIZATION")
    print("="*70)

    # Initialize optimizer
    optimizer = CommunicationParameterOptimizer()

    # Explore scenarios
    scenarios = optimizer.explore_scenarios()

    # Save results
    output_dir = '/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/results'
    results = optimizer.save_results(output_dir)

    # Generate comparison plots
    plot_path = os.path.join(output_dir, 'communication_scenarios_comparison.png')
    optimizer.generate_comparison_plots(plot_path)

    print("\n" + "="*70)
    print("OPTIMIZATION COMPLETE")
    print("="*70)

    return results


if __name__ == "__main__":
    main()
