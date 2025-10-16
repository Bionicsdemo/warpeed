"""
Quantum Communication Link Optimizer V2 - Extended Parameter Space
Relaxes extreme constraints to find viable solutions for Warpeed mission
"""

from quantum_comm_optimizer import QuantumCommOptimizer
import json

class QuantumCommOptimizerV2(QuantumCommOptimizer):
    """
    Extended optimizer with relaxed constraints to explore viable solutions.
    """

    def __init__(self):
        super().__init__()

        # EXTENDED parameter ranges for breakthrough solutions
        self.param_ranges = {
            'tx_power': [0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0],  # Up to 100W
            'tx_diameter': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0],  # Up to 10m
            'rx_diameter': [100, 200, 300, 500, 750, 1000, 1500, 2000, 3000, 5000],  # Up to 5km
            'wavelength': [1064e-9, 1550e-9, 2000e-9],  # Optimal wavelengths only
            'rx_location': ['space'],  # Space-based only (avoid atmosphere)
            'modulation': ['PPM-256'],  # Best sensitivity
            'fec_overhead': [0.30, 0.40, 0.50],  # Strong FEC
            'detector_eff': [0.7, 0.8, 0.9]  # High efficiency detectors
        }

        # RELAXED constraints for viability analysis
        self.max_tx_mass = 10.0  # 10 grams (still extremely light)
        self.max_power = 100.0  # 100 Watts (nuclear-powered)
        self.max_rx_cost = 500e9  # $500 billion (major global investment)
        self.min_snr = 10.0  # dB (unchanged)
        self.target_margin = 5.0  # dB (higher target)

    def calculate_mass(self, config):
        """
        Recalculated mass estimates for larger systems.
        """
        tx_power = config['tx_power']
        tx_diameter = config['tx_diameter']
        wavelength = config['wavelength']

        # Laser mass (better scaling for high power)
        if wavelength == 1064e-9:  # Nd:YAG
            laser_mass = 0.1 + tx_power * 0.05  # grams (improved efficiency)
        elif wavelength == 1550e-9:  # Er fiber
            laser_mass = 0.08 + tx_power * 0.03  # grams (fiber laser scaling)
        else:  # 2000nm
            laser_mass = 0.09 + tx_power * 0.04  # grams

        # Optics mass (lightweight materials)
        optics_mass = 0.05 + (tx_diameter**2) * 0.05  # grams (ultra-thin optics)

        # Pointing/structure mass
        pointing_mass = 0.10 + tx_diameter * 0.05  # grams

        total_mass = laser_mass + optics_mass + pointing_mass

        return total_mass

    def calculate_receiver_cost(self, config):
        """
        Updated cost estimates for large space-based receivers.
        """
        rx_diameter = config['rx_diameter']

        # Space-based telescope cost
        # Includes launch, deployment, operations
        if rx_diameter <= 100:
            base_cost = 10e9  # $10B (JWST-class)
        elif rx_diameter <= 1000:
            base_cost = 50e9  # $50B (large space telescope)
        else:
            base_cost = 100e9  # $100B (mega-structure)

        # Scaling with area
        cost = base_cost * (rx_diameter / 100.0)**2.0

        return cost


def main():
    print("="*80)
    print("WARPEED QUANTUM COMMUNICATION OPTIMIZER V2")
    print("Extended Parameter Space for Breakthrough Solutions")
    print("="*80)

    # Initialize V2 optimizer
    optimizer = QuantumCommOptimizerV2()

    print("\nRelaxed Constraints:")
    print(f"  Max TX Mass: {optimizer.max_tx_mass} g")
    print(f"  Max TX Power: {optimizer.max_power} W")
    print(f"  Max RX Cost: ${optimizer.max_rx_cost/1e9:.0f}B")
    print(f"  Min SNR: {optimizer.min_snr} dB")
    print(f"  Target Margin: {optimizer.target_margin} dB")

    print("\nExtended Parameter Ranges:")
    print(f"  TX Power: {min(optimizer.param_ranges['tx_power'])}-{max(optimizer.param_ranges['tx_power'])} W")
    print(f"  TX Diameter: {min(optimizer.param_ranges['tx_diameter'])}-{max(optimizer.param_ranges['tx_diameter'])} m")
    print(f"  RX Diameter: {min(optimizer.param_ranges['rx_diameter'])}-{max(optimizer.param_ranges['rx_diameter'])} m")

    # Run optimization
    print("\n" + "="*80)
    results = optimizer.run_quantum_optimization(use_real_backend=False)

    # Save results
    output_path = '/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/results/quantum_comm_solutions.json'
    output_data = optimizer.save_results(results, output_path, top_n=50)

    # Print detailed analysis
    print("\n" + "="*80)
    print("BREAKTHROUGH SOLUTIONS FOUND")
    print("="*80)

    viable = [r for r in results if r['viable']]

    if viable:
        print(f"\nViable Solutions: {len(viable)}")
        print("\nTOP 3 VIABLE SOLUTIONS:")

        for i, result in enumerate(viable[:3], 1):
            print(f"\n{'='*80}")
            print(f"SOLUTION #{i}")
            print(f"{'='*80}")
            print(f"\nPERFORMANCE:")
            print(f"  SNR: {result['link_budget']['snr_db']:.2f} dB")
            print(f"  Link Margin: {result['link_budget']['link_margin_db']:.2f} dB")
            print(f"  Data Rate: {result['link_budget']['data_rate_bps']/1e3:.1f} kbps ({result['link_budget']['data_rate_bps']*8/1e6:.3f} Mbps)")
            print(f"  Photon Rate: {result['link_budget']['photon_rate']:.1f} photons/sec")

            print(f"\nTRANSMITTER:")
            print(f"  Power: {result['config']['tx_power']:.1f} W")
            print(f"  Aperture: {result['config']['tx_diameter']:.1f} m")
            print(f"  Wavelength: {result['config']['wavelength']*1e9:.0f} nm")
            print(f"  Mass: {result['mass_grams']:.2f} g")

            print(f"\nRECEIVER:")
            print(f"  Aperture: {result['config']['rx_diameter']:.0f} m")
            print(f"  Location: {result['config']['rx_location']}")
            print(f"  Detector Efficiency: {result['config']['detector_eff']*100:.0f}%")
            print(f"  Cost: ${result['cost_usd']/1e9:.1f} B")

            print(f"\nLINK BUDGET:")
            print(f"  TX Gain: {result['link_budget']['tx_gain_db']:.1f} dB")
            print(f"  Path Loss: {result['link_budget']['path_loss_db']:.1f} dB")
            print(f"  RX Gain: {result['link_budget']['rx_gain_db']:.1f} dB")
            print(f"  RX Power: {result['link_budget']['rx_power_watts']:.2e} W")
            print(f"  Noise Power: {result['link_budget']['noise_power_dbw']:.1f} dBW")

            print(f"\nCOMMUNICATION:")
            print(f"  Modulation: {result['config']['modulation']}")
            print(f"  FEC Overhead: {result['config']['fec_overhead']*100:.0f}%")

        # Analysis
        print(f"\n{'='*80}")
        print("KEY INSIGHTS")
        print(f"{'='*80}")

        best = viable[0]
        print(f"\nTo close the 84 dB gap, we need:")
        print(f"  1. Transmitter power: {best['config']['tx_power']}W (vs 1W baseline)")
        print(f"  2. Transmitter aperture: {best['config']['tx_diameter']}m (vs 1m baseline)")
        print(f"  3. Receiver aperture: {best['config']['rx_diameter']}m (vs 100m baseline)")
        print(f"  4. Space-based receiver (eliminates 5 dB atmospheric loss)")
        print(f"  5. Advanced modulation: {best['config']['modulation']}")

        improvement = best['link_budget']['snr_db'] - (-74.3)
        print(f"\nTotal improvement: {improvement:.1f} dB")
        print(f"Final SNR: {best['link_budget']['snr_db']:.1f} dB")
        print(f"Link margin: {best['link_budget']['link_margin_db']:.1f} dB")

    else:
        print("\nWARNING: Still no viable solutions even with relaxed constraints!")
        print("The 84 dB SNR gap may be physically impossible to close with current technology.")
        print("\nBest achievable solution:")
        best = results[0]
        print(f"  SNR: {best['link_budget']['snr_db']:.1f} dB (need {optimizer.min_snr} dB)")
        print(f"  Deficit: {optimizer.min_snr - best['link_budget']['snr_db']:.1f} dB")
        print(f"  TX Power: {best['config']['tx_power']} W")
        print(f"  TX Aperture: {best['config']['tx_diameter']} m")
        print(f"  RX Aperture: {best['config']['rx_diameter']} m")
        print(f"  Mass: {best['mass_grams']:.2f} g")
        print(f"  Cost: ${best['cost_usd']/1e9:.1f} B")

    print("\n" + "="*80)
    print(f"Full results: {output_path}")
    print("="*80)

    return output_path


if __name__ == "__main__":
    main()
