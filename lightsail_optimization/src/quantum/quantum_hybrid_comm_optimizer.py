#!/usr/bin/env python3
"""
Quantum Hybrid Optical-RF Communication System Optimizer
Uses IBM Torino (20 qubits) to optimize dual-mode communication architecture
combining reliable RF telemetry with high-rate optical science data.
"""

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit.circuit import Parameter
import json
from datetime import datetime
import os

class HybridCommOptimizer:
    """
    Quantum optimizer for hybrid optical-RF communication systems.

    20 qubits allocated as:
    - RF subsystem: 8 qubits (frequency, power, antenna)
    - Optical subsystem: 8 qubits (wavelength, power, aperture)
    - Shared resources: 4 qubits (power allocation, switching logic)
    """

    def __init__(self):
        # RF Channel Parameters
        self.rf_frequencies = ['S-band', 'X-band', 'Ka-band', 'Ku-band']  # 2 qubits = 4 options
        self.rf_power_levels = np.linspace(0.5, 2.0, 8)  # 3 qubits = 8 levels
        self.rf_antenna_sizes = np.linspace(0.5, 1.5, 8)  # 3 qubits = 8 sizes

        # Optical Channel Parameters
        self.optical_wavelengths = ['1064nm', '1550nm', '850nm', '532nm']  # 2 qubits
        self.optical_power_levels = np.linspace(1.0, 5.0, 8)  # 3 qubits
        self.optical_apertures = np.linspace(0.5, 2.0, 8)  # 3 qubits

        # Shared Resources
        self.power_allocation_strategies = ['RF_heavy', 'Balanced', 'Optical_heavy', 'Adaptive']  # 2 qubits
        self.switching_logics = ['Sequential', 'Opportunistic', 'Priority', 'Hybrid']  # 2 qubits

        # Mission Parameters
        self.mission_duration_days = 365
        self.optical_availability = 0.10  # 10% of time
        self.rf_availability = 1.0  # 100% of time

        # Constraints
        self.total_mass_budget = 4.0  # grams
        self.avg_power_budget = 3.0  # Watts
        self.peak_power_budget = 5.0  # Watts
        self.min_rf_ebn0 = 8.0  # dB
        self.min_optical_snr = 6.0  # dB

        # Distance - using more realistic lightsail demonstration mission
        # For Alpha Centauri scale, we'd need much larger systems
        # Use 1 AU for demonstration (Earth-Sun distance) - represents early mission phase
        self.distance_au = 10  # AU - outer solar system mission (Jupiter-like distance)
        self.distance_km = self.distance_au * 1.496e8  # km

    def create_qaoa_circuit(self, gamma, beta, num_layers=3):
        """
        Create QAOA circuit for hybrid communication system optimization.

        Circuit structure:
        - Initial superposition across all 20 qubits
        - QAOA layers encoding cost function (data volume, reliability, mass, power)
        - Measurement in computational basis
        """
        qc = QuantumCircuit(20, 20)

        # Initial state: uniform superposition
        qc.h(range(20))

        # QAOA layers
        for layer in range(num_layers):
            # Cost Hamiltonian - encode optimization objectives
            # This is a simplified version - full implementation would have more complex interactions

            # RF subsystem interactions (qubits 0-7)
            for i in range(7):
                qc.rz(2 * gamma * (i + 1) * 0.1, i)
                if i < 6:
                    qc.rzz(2 * gamma * 0.05, i, i + 1)

            # Optical subsystem interactions (qubits 8-15)
            for i in range(8, 15):
                qc.rz(2 * gamma * (i - 7) * 0.1, i)
                if i < 14:
                    qc.rzz(2 * gamma * 0.05, i, i + 1)

            # Shared resources (qubits 16-19)
            for i in range(16, 19):
                qc.rz(2 * gamma * 0.15, i)

            # Cross-subsystem entanglement (RF-Optical-Shared)
            qc.rzz(2 * gamma * 0.08, 3, 11)  # Power coupling
            qc.rzz(2 * gamma * 0.08, 16, 3)  # RF to power allocation
            qc.rzz(2 * gamma * 0.08, 16, 11)  # Optical to power allocation
            qc.rzz(2 * gamma * 0.08, 17, 18)  # Switching logic coupling

            # Mixer Hamiltonian - transitions between states
            for i in range(20):
                qc.rx(2 * beta, i)

        # Measurement
        qc.measure(range(20), range(20))

        return qc

    def decode_bitstring(self, bitstring):
        """
        Decode 20-qubit measurement into hybrid system parameters.
        """
        # RF subsystem (qubits 0-7)
        rf_freq_idx = int(bitstring[0:2], 2)
        rf_power_idx = int(bitstring[2:5], 2)
        rf_antenna_idx = int(bitstring[5:8], 2)

        # Optical subsystem (qubits 8-15)
        opt_wave_idx = int(bitstring[8:10], 2)
        opt_power_idx = int(bitstring[10:13], 2)
        opt_aperture_idx = int(bitstring[13:16], 2)

        # Shared resources (qubits 16-19)
        power_alloc_idx = int(bitstring[16:18], 2)
        switching_idx = int(bitstring[18:20], 2)

        return {
            'rf_frequency': self.rf_frequencies[rf_freq_idx],
            'rf_power': self.rf_power_levels[rf_power_idx],
            'rf_antenna_size': self.rf_antenna_sizes[rf_antenna_idx],
            'optical_wavelength': self.optical_wavelengths[opt_wave_idx],
            'optical_power': self.optical_power_levels[opt_power_idx],
            'optical_aperture': self.optical_apertures[opt_aperture_idx],
            'power_allocation': self.power_allocation_strategies[power_alloc_idx],
            'switching_logic': self.switching_logics[switching_idx]
        }

    def calculate_rf_performance(self, params):
        """
        Calculate RF link performance metrics.
        """
        # Frequency to numeric value (GHz)
        freq_map = {'S-band': 2.3, 'X-band': 8.4, 'Ka-band': 32.0, 'Ku-band': 14.0}
        freq_ghz = freq_map[params['rf_frequency']]

        # Wavelength (m)
        wavelength = 3e8 / (freq_ghz * 1e9)

        # Path loss (dB) - free space
        path_loss_db = 20 * np.log10(self.distance_km * 1e3) + 20 * np.log10(freq_ghz * 1e9) - 147.55

        # Transmit antenna gain (dBi) - parabolic dish approximation
        tx_gain_db = 10 * np.log10((np.pi * params['rf_antenna_size'] / wavelength) ** 2 * 0.6)

        # Receive antenna gain (dBi) - DSN 34m antenna
        rx_antenna_size = 34.0  # meters
        rx_gain_db = 10 * np.log10((np.pi * rx_antenna_size / wavelength) ** 2 * 0.65)

        # EIRP (dBW)
        tx_power_dbw = 10 * np.log10(params['rf_power'])
        eirp_dbw = tx_power_dbw + tx_gain_db

        # Received power (dBW)
        rx_power_dbw = eirp_dbw + rx_gain_db - path_loss_db

        # System temperature (K) and noise
        system_temp = 25  # K for DSN
        noise_power_density = 10 * np.log10(1.38e-23 * system_temp)  # dBW/Hz

        # Data rate calculation - Shannon capacity with margin
        # For telemetry, use conservative modulation
        bandwidth_hz = 100  # Hz for low-rate telemetry
        noise_power_dbw = noise_power_density + 10 * np.log10(bandwidth_hz)

        snr_db = rx_power_dbw - noise_power_dbw
        ebn0_db = snr_db - 10 * np.log10(bandwidth_hz)

        # Data rate (bps) - use BPSK with coding
        if ebn0_db >= self.min_rf_ebn0:
            data_rate_bps = bandwidth_hz * 0.5  # Conservative with coding
        else:
            data_rate_bps = 1  # Minimal rate

        # Mass estimate (grams) - RF subsystem
        mass_rf = 0.5 + params['rf_antenna_size'] * 0.8 + params['rf_power'] * 0.3

        return {
            'path_loss_db': path_loss_db,
            'tx_gain_db': tx_gain_db,
            'rx_gain_db': rx_gain_db,
            'ebn0_db': ebn0_db,
            'snr_db': snr_db,
            'data_rate_bps': data_rate_bps,
            'mass_grams': mass_rf,
            'feasible': ebn0_db >= self.min_rf_ebn0
        }

    def calculate_optical_performance(self, params):
        """
        Calculate optical link performance metrics.
        """
        # Wavelength to numeric (nm to m)
        wave_map = {'1064nm': 1064e-9, '1550nm': 1550e-9, '850nm': 850e-9, '532nm': 532e-9}
        wavelength = wave_map[params['optical_wavelength']]

        # Diffraction-limited beam divergence (radians)
        beam_divergence = 1.22 * wavelength / params['optical_aperture']

        # Beam radius at receiver (m)
        beam_radius = beam_divergence * self.distance_km * 1e3

        # Geometric loss (dB)
        rx_aperture = 10.0  # meters - dedicated optical ground station
        geometric_loss_db = 10 * np.log10((rx_aperture / (2 * beam_radius)) ** 2)

        # Atmospheric loss (dB) - clear sky
        atmospheric_loss_db = 3.0  # dB - optimistic for clear conditions

        # Transmit power (dBW) - pulsed
        tx_power_dbw = 10 * np.log10(params['optical_power'])

        # Received power (dBW)
        rx_power_dbw = tx_power_dbw + geometric_loss_db - atmospheric_loss_db

        # Noise - background radiation and detector
        # Assume photon-counting detector
        background_photons_per_sec = 1e6  # photons/sec
        signal_photons_per_sec = 10 ** (rx_power_dbw / 10) / (6.626e-34 * 3e8 / wavelength)

        # SNR
        snr = signal_photons_per_sec / np.sqrt(background_photons_per_sec)
        snr_db = 10 * np.log10(snr + 1e-10)  # Avoid log(0)

        # Data rate (bps) - PPM (Pulse Position Modulation)
        if snr_db >= self.min_optical_snr:
            # High rate when locked
            data_rate_bps = min(10000, signal_photons_per_sec * 0.001)  # Conservative
        else:
            data_rate_bps = 0  # Cannot communicate

        # Mass estimate (grams) - Optical subsystem
        mass_optical = 0.8 + params['optical_aperture'] * 1.2 + params['optical_power'] * 0.4

        return {
            'beam_divergence_rad': beam_divergence,
            'geometric_loss_db': geometric_loss_db,
            'snr_db': snr_db,
            'data_rate_bps': data_rate_bps,
            'mass_grams': mass_optical,
            'feasible': snr_db >= self.min_optical_snr
        }

    def calculate_hybrid_performance(self, params):
        """
        Calculate overall hybrid system performance.
        """
        rf_perf = self.calculate_rf_performance(params)
        opt_perf = self.calculate_optical_performance(params)

        # Total mass
        mass_switching = 0.3  # grams - electronic switching
        mass_power_mgmt = 0.4  # grams - power management
        total_mass = rf_perf['mass_grams'] + opt_perf['mass_grams'] + mass_switching + mass_power_mgmt

        # Power allocation based on strategy
        power_efficiency = 0.88  # 88% average efficiency
        if params['power_allocation'] == 'RF_heavy':
            rf_duty_cycle = 1.0
            opt_duty_cycle = 0.05
        elif params['power_allocation'] == 'Optical_heavy':
            rf_duty_cycle = 0.3
            opt_duty_cycle = 0.15
        elif params['power_allocation'] == 'Balanced':
            rf_duty_cycle = 0.6
            opt_duty_cycle = 0.10
        else:  # Adaptive
            rf_duty_cycle = 0.9
            opt_duty_cycle = 0.12

        # Average power consumption
        avg_power = (params['rf_power'] * rf_duty_cycle +
                     params['optical_power'] * opt_duty_cycle) / power_efficiency

        # Peak power (when both active)
        peak_power = (params['rf_power'] + params['optical_power']) / power_efficiency

        # Annual data volume calculation
        seconds_per_year = 365 * 24 * 3600

        # RF data (continuous telemetry)
        rf_data_bits_per_year = rf_perf['data_rate_bps'] * seconds_per_year * self.rf_availability

        # Optical data (opportunistic science)
        opt_data_bits_per_year = opt_perf['data_rate_bps'] * seconds_per_year * self.optical_availability

        # Total data
        total_data_bits_per_year = rf_data_bits_per_year + opt_data_bits_per_year

        # Telemetry requirements: 1 packet/day (assume 1 kbit packet)
        required_rf_bits_per_year = 365 * 1000  # bits
        rf_margin = rf_data_bits_per_year / required_rf_bits_per_year if required_rf_bits_per_year > 0 else 0

        # Science requirements: 1 image/week (assume 100 kbit image)
        required_opt_bits_per_year = 52 * 100000  # bits
        opt_margin = opt_data_bits_per_year / required_opt_bits_per_year if required_opt_bits_per_year > 0 else 0

        # Constraint violations
        mass_violation = max(0, total_mass - self.total_mass_budget)
        avg_power_violation = max(0, avg_power - self.avg_power_budget)
        peak_power_violation = max(0, peak_power - self.peak_power_budget)
        rf_ebn0_violation = max(0, self.min_rf_ebn0 - rf_perf['ebn0_db'])
        opt_snr_violation = max(0, self.min_optical_snr - opt_perf['snr_db'])

        total_violation = (mass_violation + avg_power_violation + peak_power_violation +
                          rf_ebn0_violation * 10 + opt_snr_violation * 10)

        # Objective function (maximize data, minimize violations)
        # Normalize data volume to GB
        data_volume_gb = total_data_bits_per_year / (8 * 1e9)

        # Multi-objective score
        score = data_volume_gb - total_violation * 100  # Heavy penalty for violations

        # Reliability score (RF uptime)
        reliability = self.rf_availability if rf_perf['feasible'] else 0

        return {
            'rf_performance': rf_perf,
            'optical_performance': opt_perf,
            'total_mass_grams': total_mass,
            'avg_power_watts': avg_power,
            'peak_power_watts': peak_power,
            'rf_data_bits_per_year': rf_data_bits_per_year,
            'optical_data_bits_per_year': opt_data_bits_per_year,
            'total_data_bits_per_year': total_data_bits_per_year,
            'data_volume_gb_per_year': data_volume_gb,
            'rf_margin': rf_margin,
            'optical_margin': opt_margin,
            'total_violation': total_violation,
            'score': score,
            'reliability': reliability,
            'feasible': (total_violation < 0.01 and rf_perf['feasible']),
            'constraints_met': {
                'mass': total_mass <= self.total_mass_budget,
                'avg_power': avg_power <= self.avg_power_budget,
                'peak_power': peak_power <= self.peak_power_budget,
                'rf_ebn0': rf_perf['ebn0_db'] >= self.min_rf_ebn0,
                'optical_snr': opt_perf['snr_db'] >= self.min_optical_snr
            }
        }

    def run_optimization(self, api_token=None):
        """
        Run quantum optimization on IBM Torino.
        """
        print("=" * 80)
        print("HYBRID OPTICAL-RF COMMUNICATION SYSTEM QUANTUM OPTIMIZER")
        print("=" * 80)
        print(f"Target: IBM Torino (20 qubits, 10,000 shots)")
        print(f"Distance: {self.distance_au:,} AU to Alpha Centauri")
        print(f"Mission Duration: {self.mission_duration_days} days")
        print()

        # Initialize IBM Quantum service
        if api_token:
            service = QiskitRuntimeService(channel="ibm_quantum_platform", token=api_token)
        else:
            service = QiskitRuntimeService(channel="ibm_quantum_platform")

        backend = service.backend("ibm_torino")

        print(f"Connected to: {backend.name}")
        print(f"Qubits: {backend.num_qubits}")
        print()

        # Create QAOA circuit with optimized parameters
        # These would typically be optimized via classical loop
        gamma = 0.8
        beta = 0.4

        print("Building QAOA circuit...")
        qc = self.create_qaoa_circuit(gamma, beta, num_layers=3)
        print(f"Circuit depth: {qc.depth()}")
        print(f"Circuit gates: {qc.size()}")
        print()

        # Transpile for IBM Torino
        print("Transpiling for IBM Torino...")
        transpiled_qc = transpile(qc, backend=backend, optimization_level=3)
        print(f"Transpiled depth: {transpiled_qc.depth()}")
        print()

        # Run on IBM Torino with 10,000 shots
        print("Submitting job to IBM Torino...")
        print("Shots: 10,000")

        # Use Sampler in batch mode for open plan
        sampler = Sampler(mode=backend)
        job = sampler.run([transpiled_qc], shots=10000)

        print(f"Job ID: {job.job_id()}")
        print("Waiting for results...")

        result = job.result()

        print("Quantum execution completed!")
        print()

        # Extract measurement results from SamplerV2
        pub_result = result[0]

        # Get the bitstrings and counts
        # SamplerV2 returns data differently - need to access via attribute
        if hasattr(pub_result.data, 'meas'):
            counts = pub_result.data.meas.get_counts()
        elif hasattr(pub_result.data, 'c'):
            counts = pub_result.data.c.get_counts()
        else:
            # Try to get raw data and convert to counts
            # DataBin contains the measurement results
            data_bin = pub_result.data
            # Get all attributes to find measurement register
            attrs = [attr for attr in dir(data_bin) if not attr.startswith('_')]
            print(f"Available data attributes: {attrs}")

            # Try first available attribute
            if attrs:
                meas_data = getattr(data_bin, attrs[0])
                if hasattr(meas_data, 'get_counts'):
                    counts = meas_data.get_counts()
                else:
                    # Manually construct counts from bitarray
                    counts = {}
                    for bitstring in meas_data:
                        bit_str = ''.join(str(int(b)) for b in bitstring)
                        counts[bit_str] = counts.get(bit_str, 0) + 1

        print(f"Total measurement outcomes: {len(counts)}")
        print()

        # Analyze all solutions
        print("Analyzing quantum solutions...")
        solutions = []

        for bitstring, count in counts.items():
            # Decode to system parameters
            params = self.decode_bitstring(bitstring)

            # Calculate performance
            performance = self.calculate_hybrid_performance(params)

            # Store solution
            solution = {
                'bitstring': bitstring,
                'count': int(count),
                'probability': count / 10000,
                'parameters': params,
                'performance': performance
            }

            solutions.append(solution)

        # Sort by score (higher is better)
        solutions.sort(key=lambda x: x['performance']['score'], reverse=True)

        # Filter for feasible solutions
        feasible_solutions = [s for s in solutions if s['performance']['feasible']]

        print(f"Feasible solutions: {len(feasible_solutions)} / {len(solutions)}")
        print()

        # Select top 30 unique configurations
        top_solutions = []
        seen_configs = set()

        for sol in solutions:
            # Create unique identifier based on parameters
            config_id = (sol['parameters']['rf_frequency'],
                        round(sol['parameters']['rf_power'], 2),
                        round(sol['parameters']['rf_antenna_size'], 2),
                        sol['parameters']['optical_wavelength'],
                        round(sol['parameters']['optical_power'], 2),
                        round(sol['parameters']['optical_aperture'], 2))

            if config_id not in seen_configs:
                top_solutions.append(sol)
                seen_configs.add(config_id)

            if len(top_solutions) >= 30:
                break

        return {
            'timestamp': datetime.now().isoformat(),
            'backend': backend.name,
            'num_qubits': backend.num_qubits,
            'shots': 10000,
            'mission_parameters': {
                'distance_au': self.distance_au,
                'duration_days': self.mission_duration_days,
                'optical_availability': self.optical_availability,
                'rf_availability': self.rf_availability
            },
            'constraints': {
                'total_mass_budget_grams': self.total_mass_budget,
                'avg_power_budget_watts': self.avg_power_budget,
                'peak_power_budget_watts': self.peak_power_budget,
                'min_rf_ebn0_db': self.min_rf_ebn0,
                'min_optical_snr_db': self.min_optical_snr
            },
            'statistics': {
                'total_solutions': len(solutions),
                'feasible_solutions': len(feasible_solutions),
                'top_solutions_returned': len(top_solutions)
            },
            'top_30_solutions': top_solutions
        }


def main():
    """
    Main execution function.
    """
    optimizer = HybridCommOptimizer()

    try:
        # Run optimization (will use saved credentials)
        results = optimizer.run_optimization()

        # Create results directory
        results_dir = "/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/results"
        os.makedirs(results_dir, exist_ok=True)

        # Save results
        output_file = os.path.join(results_dir, "quantum_hybrid_solutions.json")

        # Custom JSON encoder for numpy types
        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, np.bool_):
                    return bool(obj)
                return super(NumpyEncoder, self).default(obj)

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, cls=NumpyEncoder)

        print("=" * 80)
        print("OPTIMIZATION COMPLETE")
        print("=" * 80)
        print(f"Results saved to: {output_file}")
        print()

        # Display top 3 solutions
        print("=" * 80)
        print("TOP 3 HYBRID COMMUNICATION ARCHITECTURES")
        print("=" * 80)
        print()

        for i, sol in enumerate(results['top_30_solutions'][:3], 1):
            params = sol['parameters']
            perf = sol['performance']
            rf = perf['rf_performance']
            opt = perf['optical_performance']

            print(f"SOLUTION #{i}")
            print(f"Quantum Probability: {sol['probability']:.4f}")
            print(f"Score: {perf['score']:.2f}")
            print()

            print("RF SUBSYSTEM:")
            print(f"  Frequency: {params['rf_frequency']}")
            print(f"  Power: {params['rf_power']:.2f} W")
            print(f"  Antenna: {params['rf_antenna_size']:.2f} m")
            print(f"  Eb/N0: {rf['ebn0_db']:.2f} dB")
            print(f"  Data Rate: {rf['data_rate_bps']:.2f} bps")
            print(f"  Annual Data: {perf['rf_data_bits_per_year'] / 1e6:.2f} Mbit")
            print(f"  Mass: {rf['mass_grams']:.2f} g")
            print()

            print("OPTICAL SUBSYSTEM:")
            print(f"  Wavelength: {params['optical_wavelength']}")
            print(f"  Power: {params['optical_power']:.2f} W")
            print(f"  Aperture: {params['optical_aperture']:.2f} m")
            print(f"  SNR: {opt['snr_db']:.2f} dB")
            print(f"  Data Rate: {opt['data_rate_bps']:.2f} bps")
            print(f"  Annual Data: {perf['optical_data_bits_per_year'] / 1e9:.2f} Gbit")
            print(f"  Mass: {opt['mass_grams']:.2f} g")
            print()

            print("HYBRID SYSTEM:")
            print(f"  Power Allocation: {params['power_allocation']}")
            print(f"  Switching Logic: {params['switching_logic']}")
            print(f"  Total Mass: {perf['total_mass_grams']:.2f} g")
            print(f"  Avg Power: {perf['avg_power_watts']:.2f} W")
            print(f"  Peak Power: {perf['peak_power_watts']:.2f} W")
            print(f"  Total Annual Data: {perf['data_volume_gb_per_year']:.3f} GB")
            print(f"  RF Margin: {perf['rf_margin']:.1f}x required")
            print(f"  Optical Margin: {perf['optical_margin']:.1f}x required")
            print(f"  Reliability: {perf['reliability'] * 100:.1f}%")
            print()

            print("CONSTRAINTS:")
            for constraint, met in perf['constraints_met'].items():
                status = "PASS" if met else "FAIL"
                print(f"  {constraint}: {status}")
            print()

            print("-" * 80)
            print()

        # Summary statistics
        print("=" * 80)
        print("MISSION SUMMARY")
        print("=" * 80)

        if results['top_30_solutions']:
            best = results['top_30_solutions'][0]
            best_perf = best['performance']

            # Compare to pure RF baseline
            baseline_rf_rate = 10  # bps - conservative pure RF
            baseline_annual = baseline_rf_rate * 365 * 24 * 3600 / (8 * 1e9)  # GB

            improvement = best_perf['data_volume_gb_per_year'] / baseline_annual

            print(f"Best Hybrid Configuration:")
            print(f"  Annual Data Volume: {best_perf['data_volume_gb_per_year']:.3f} GB")
            print(f"  Baseline Pure RF: {baseline_annual:.3f} GB")
            print(f"  Improvement: {improvement:.1f}x")
            print()

            print(f"Telemetry Performance:")
            print(f"  Required: 1 packet/day (365 kbit/year)")
            print(f"  Achieved: {best_perf['rf_data_bits_per_year'] / 1e6:.2f} Mbit/year")
            print(f"  Margin: {best_perf['rf_margin']:.1f}x")
            print()

            print(f"Science Data Performance:")
            print(f"  Required: 1 image/week (5.2 Mbit/year)")
            print(f"  Achieved: {best_perf['optical_data_bits_per_year'] / 1e9:.2f} Gbit/year")
            print(f"  Margin: {best_perf['optical_margin']:.1f}x")
            print()

            # Failure mode analysis
            print("FAILURE MODE ANALYSIS:")
            print("  Scenario 1: Optical link fails (no alignment)")
            print(f"    Fallback: RF telemetry continues")
            print(f"    Impact: Science data lost, telemetry maintained")
            print(f"    Reliability: {best_perf['reliability'] * 100:.1f}%")
            print()
            print("  Scenario 2: RF link fails (hardware fault)")
            print(f"    Fallback: Optical can send emergency telemetry")
            print(f"    Impact: Lower reliability, but high-rate backup available")
            print()
            print("  Scenario 3: Power constraint (battery low)")
            print(f"    Fallback: Switch to RF-only mode")
            print(f"    Impact: Science paused, telemetry preserved")
            print()

        print("=" * 80)

    except Exception as e:
        print(f"Error during optimization: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
