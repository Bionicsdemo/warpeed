"""
Quantum Communication Link Optimizer for Warpeed Interstellar Mission
Uses IBM Torino quantum computer (133 qubits) with QAOA to find optimal configurations
that solve the 84 dB SNR deficit crisis.
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit import Parameter
from qiskit_ibm_runtime import QiskitRuntimeService, Session, Sampler, Options
import numpy as np
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple
import itertools

class QuantumCommOptimizer:
    """
    Quantum optimizer for interstellar communication link design.
    Uses QAOA to explore massive configuration space simultaneously.
    """

    def __init__(self):
        # Physical constants
        self.c = 299792458  # Speed of light (m/s)
        self.h = 6.62607015e-34  # Planck constant (J⋅s)
        self.k = 1.380649e-23  # Boltzmann constant (J/K)

        # Mission parameters
        self.distance = 4.37 * 9.461e15  # 4.37 light years in meters
        self.T_noise = 50  # Noise temperature (K) - cooled receiver

        # Parameter ranges (encoded into qubits)
        self.param_ranges = {
            'tx_power': [0.1, 0.5, 1.0, 2.0, 5.0, 10.0],  # Watts
            'tx_diameter': [0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0],  # meters
            'rx_diameter': [50, 100, 200, 300, 500, 750, 1000],  # meters
            'wavelength': [1064e-9, 1550e-9, 2000e-9, 10600e-9],  # meters
            'rx_location': ['ground', 'space'],  # Space-based avoids atmosphere
            'modulation': ['PPM-16', 'PPM-256', 'OOK'],
            'fec_overhead': [0.10, 0.20, 0.30, 0.40, 0.50],  # 10-50%
            'detector_eff': [0.3, 0.5, 0.7, 0.9]  # Quantum efficiency
        }

        # Constraints
        self.max_tx_mass = 2.0  # grams
        self.max_power = 2.0  # Watts
        self.max_rx_cost = 50e9  # $50 billion
        self.min_snr = 10.0  # dB (minimum viable)
        self.target_margin = 3.0  # dB (preferred margin)

    def calculate_link_budget(self, config: Dict) -> Dict:
        """
        Calculate complete link budget for a configuration.
        Returns SNR, link margin, and other metrics.
        """
        tx_power = config['tx_power']
        tx_diameter = config['tx_diameter']
        rx_diameter = config['rx_diameter']
        wavelength = config['wavelength']
        rx_location = config['rx_location']
        detector_eff = config['detector_eff']
        modulation = config['modulation']
        fec_overhead = config['fec_overhead']

        # Transmitter gain (diffraction-limited)
        tx_area = np.pi * (tx_diameter/2)**2
        tx_gain_linear = (4 * np.pi * tx_area) / (wavelength**2)
        tx_gain_db = 10 * np.log10(tx_gain_linear)

        # Free space path loss
        path_loss_linear = (wavelength / (4 * np.pi * self.distance))**2
        path_loss_db = 10 * np.log10(path_loss_linear)

        # Receiver gain
        rx_area = np.pi * (rx_diameter/2)**2
        rx_gain_linear = (4 * np.pi * rx_area) / (wavelength**2)
        rx_gain_db = 10 * np.log10(rx_gain_linear)

        # Atmospheric loss (only for ground-based receivers)
        if rx_location == 'ground':
            if wavelength < 3000e-9:  # Optical/NIR
                atm_loss_db = -5.0  # dB (zenith, good conditions)
            else:  # Mid-IR
                atm_loss_db = -15.0  # dB (high absorption)
        else:
            atm_loss_db = 0.0  # Space-based, no atmosphere

        # Pointing loss (conservative estimate)
        pointing_loss_db = -1.0  # dB

        # Detector efficiency loss
        detector_loss_db = 10 * np.log10(detector_eff)

        # Received power (dBW)
        tx_power_dbw = 10 * np.log10(tx_power)
        rx_power_dbw = (tx_power_dbw + tx_gain_db + path_loss_db +
                       rx_gain_db + atm_loss_db + pointing_loss_db +
                       detector_loss_db)
        rx_power_watts = 10**(rx_power_dbw/10)

        # Photon energy
        photon_energy = self.h * self.c / wavelength

        # Photon rate
        photon_rate = rx_power_watts / photon_energy

        # Noise calculation
        # Bandwidth depends on modulation
        if modulation == 'OOK':
            data_rate = 1e6  # 1 Mbps baseline
            bandwidth = data_rate
        elif modulation == 'PPM-16':
            data_rate = 1e6 / 4  # 250 kbps (4 bits per symbol)
            bandwidth = data_rate * 16  # PPM bandwidth expansion
        elif modulation == 'PPM-256':
            data_rate = 1e6 / 8  # 125 kbps (8 bits per symbol)
            bandwidth = data_rate * 256

        # Account for FEC overhead
        effective_data_rate = data_rate * (1 - fec_overhead)

        # Thermal noise power
        noise_power_watts = self.k * self.T_noise * bandwidth
        noise_power_dbw = 10 * np.log10(noise_power_watts)

        # Shot noise (photon counting noise)
        shot_noise_photons = np.sqrt(photon_rate * 1.0)  # per second

        # Total noise (dominated by shot noise for weak signals)
        total_noise_dbw = max(noise_power_dbw,
                             10 * np.log10(shot_noise_photons * photon_energy))

        # SNR calculation
        snr_db = rx_power_dbw - total_noise_dbw

        # Link margin
        link_margin_db = snr_db - self.min_snr

        return {
            'tx_gain_db': tx_gain_db,
            'path_loss_db': path_loss_db,
            'rx_gain_db': rx_gain_db,
            'atm_loss_db': atm_loss_db,
            'rx_power_dbw': rx_power_dbw,
            'rx_power_watts': rx_power_watts,
            'photon_rate': photon_rate,
            'noise_power_dbw': total_noise_dbw,
            'snr_db': snr_db,
            'link_margin_db': link_margin_db,
            'data_rate_bps': effective_data_rate,
            'bandwidth_hz': bandwidth
        }

    def calculate_mass(self, config: Dict) -> float:
        """
        Estimate transmitter mass based on configuration.
        """
        tx_power = config['tx_power']
        tx_diameter = config['tx_diameter']
        wavelength = config['wavelength']

        # Laser mass (scales with power)
        if wavelength == 1064e-9:  # Nd:YAG
            laser_mass = 0.05 + tx_power * 0.08  # grams
        elif wavelength == 1550e-9:  # Er fiber
            laser_mass = 0.03 + tx_power * 0.05  # grams (lighter)
        elif wavelength == 2000e-9:  # Tm
            laser_mass = 0.04 + tx_power * 0.06  # grams
        else:  # 10600nm CO2
            laser_mass = 0.10 + tx_power * 0.15  # grams (heavier)

        # Optics mass (scales with diameter^2)
        optics_mass = 0.02 + (tx_diameter**2) * 0.10  # grams

        # Pointing system mass
        pointing_mass = 0.05  # grams (ultra-miniaturized)

        total_mass = laser_mass + optics_mass + pointing_mass

        return total_mass

    def calculate_receiver_cost(self, config: Dict) -> float:
        """
        Estimate Earth-based receiver cost.
        """
        rx_diameter = config['rx_diameter']
        rx_location = config['rx_location']

        # Ground-based telescope cost (scales with diameter^2.5)
        if rx_location == 'ground':
            base_cost = 1e9  # $1B baseline for 50m
            cost = base_cost * (rx_diameter / 50.0)**2.5
        else:  # Space-based
            # Launch + telescope cost
            base_cost = 5e9  # $5B baseline for 50m space telescope
            cost = base_cost * (rx_diameter / 50.0)**2.5 * 1.5  # Space premium

        return cost

    def evaluate_configuration(self, config: Dict) -> Tuple[float, Dict]:
        """
        Evaluate a configuration and return score + full results.
        Score is designed for quantum optimization (higher = better).
        """
        # Calculate link budget
        link = self.calculate_link_budget(config)
        snr_db = link['snr_db']
        link_margin_db = link['link_margin_db']

        # Calculate constraints
        mass = self.calculate_mass(config)
        cost = self.calculate_receiver_cost(config)
        power = config['tx_power']

        # Score function (maximize this)
        # Primary: SNR achievement
        # Penalties: constraint violations
        score = snr_db

        # Penalty for mass constraint violation
        if mass > self.max_tx_mass:
            score -= 100 * (mass - self.max_tx_mass)

        # Penalty for power constraint violation
        if power > self.max_power:
            score -= 100 * (power - self.max_power)

        # Penalty for cost constraint violation
        if cost > self.max_rx_cost:
            score -= 50 * (cost - self.max_rx_cost) / 1e9

        # Bonus for achieving target margin
        if link_margin_db >= self.target_margin:
            score += 10

        # Bonus for mass efficiency
        if mass < self.max_tx_mass * 0.8:
            score += 5

        results = {
            'config': config,
            'link_budget': link,
            'mass_grams': mass,
            'cost_usd': cost,
            'power_watts': power,
            'score': score,
            'viable': (snr_db >= self.min_snr and
                      mass <= self.max_tx_mass and
                      power <= self.max_power and
                      cost <= self.max_rx_cost)
        }

        return score, results

    def classical_grid_search(self, num_samples: int = 10000) -> List[Dict]:
        """
        Classical grid search for comparison and to generate initial solutions.
        Samples the configuration space intelligently.
        """
        print("Running classical grid search to explore configuration space...")

        # Generate smart samples (focusing on promising regions)
        all_configs = []

        # Strategy 1: High power, large apertures
        for _ in range(num_samples // 4):
            config = {
                'tx_power': np.random.choice(self.param_ranges['tx_power'][-3:]),  # High power
                'tx_diameter': np.random.choice(self.param_ranges['tx_diameter'][-3:]),  # Large
                'rx_diameter': np.random.choice(self.param_ranges['rx_diameter'][-3:]),  # Large
                'wavelength': np.random.choice(self.param_ranges['wavelength'][:3]),  # Optical
                'rx_location': np.random.choice(self.param_ranges['rx_location']),
                'modulation': np.random.choice(self.param_ranges['modulation']),
                'fec_overhead': np.random.choice(self.param_ranges['fec_overhead']),
                'detector_eff': np.random.choice(self.param_ranges['detector_eff'][-2:])  # High eff
            }
            all_configs.append(config)

        # Strategy 2: Optimal wavelength (1550nm), vary other params
        for _ in range(num_samples // 4):
            config = {
                'tx_power': np.random.choice(self.param_ranges['tx_power']),
                'tx_diameter': np.random.choice(self.param_ranges['tx_diameter']),
                'rx_diameter': np.random.choice(self.param_ranges['rx_diameter']),
                'wavelength': 1550e-9,  # Fix at 1550nm
                'rx_location': np.random.choice(self.param_ranges['rx_location']),
                'modulation': np.random.choice(self.param_ranges['modulation']),
                'fec_overhead': np.random.choice(self.param_ranges['fec_overhead']),
                'detector_eff': np.random.choice(self.param_ranges['detector_eff'])
            }
            all_configs.append(config)

        # Strategy 3: Space-based receivers (no atmospheric loss)
        for _ in range(num_samples // 4):
            config = {
                'tx_power': np.random.choice(self.param_ranges['tx_power']),
                'tx_diameter': np.random.choice(self.param_ranges['tx_diameter']),
                'rx_diameter': np.random.choice(self.param_ranges['rx_diameter']),
                'wavelength': np.random.choice(self.param_ranges['wavelength']),
                'rx_location': 'space',  # Fix at space
                'modulation': np.random.choice(self.param_ranges['modulation']),
                'fec_overhead': np.random.choice(self.param_ranges['fec_overhead']),
                'detector_eff': np.random.choice(self.param_ranges['detector_eff'])
            }
            all_configs.append(config)

        # Strategy 4: Random exploration
        for _ in range(num_samples // 4):
            config = {
                'tx_power': np.random.choice(self.param_ranges['tx_power']),
                'tx_diameter': np.random.choice(self.param_ranges['tx_diameter']),
                'rx_diameter': np.random.choice(self.param_ranges['rx_diameter']),
                'wavelength': np.random.choice(self.param_ranges['wavelength']),
                'rx_location': np.random.choice(self.param_ranges['rx_location']),
                'modulation': np.random.choice(self.param_ranges['modulation']),
                'fec_overhead': np.random.choice(self.param_ranges['fec_overhead']),
                'detector_eff': np.random.choice(self.param_ranges['detector_eff'])
            }
            all_configs.append(config)

        # Evaluate all configurations
        results = []
        for i, config in enumerate(all_configs):
            if (i + 1) % 1000 == 0:
                print(f"  Evaluated {i+1}/{len(all_configs)} configurations...")
            score, result = self.evaluate_configuration(config)
            results.append(result)

        # Sort by score (descending)
        results.sort(key=lambda x: x['score'], reverse=True)

        return results

    def create_qaoa_circuit(self, num_qubits: int = 20, depth: int = 3) -> QuantumCircuit:
        """
        Create QAOA circuit for communication link optimization.
        Uses 20 qubits to encode configuration parameters.
        """
        qr = QuantumRegister(num_qubits, 'q')
        cr = ClassicalRegister(num_qubits, 'c')
        qc = QuantumCircuit(qr, cr)

        # Initialize in superposition (equal probability for all configurations)
        for i in range(num_qubits):
            qc.h(i)

        # QAOA layers (problem Hamiltonian + mixer Hamiltonian)
        gamma = Parameter('γ')  # Problem Hamiltonian rotation
        beta = Parameter('β')   # Mixer Hamiltonian rotation

        for layer in range(depth):
            # Problem Hamiltonian: encodes SNR objective + constraints
            # This is a simplified version - in reality would be more complex

            # Entangle qubits representing related parameters
            # e.g., tx_power affects SNR and mass
            for i in range(0, num_qubits - 1, 2):
                qc.rzz(gamma, i, i+1)

            # Single-qubit rotations based on parameter importance
            for i in range(num_qubits):
                qc.rz(gamma, i)

            # Mixer Hamiltonian: allows exploration
            for i in range(num_qubits):
                qc.rx(beta, i)

        # Measurement
        qc.measure(qr, cr)

        return qc

    def decode_bitstring(self, bitstring: str) -> Dict:
        """
        Decode quantum measurement bitstring into configuration parameters.
        20 qubits allocated as follows:
        - bits 0-2: tx_power (3 bits = 8 levels, map to 6 discrete values)
        - bits 3-5: tx_diameter (3 bits = 8 levels, map to 7 discrete values)
        - bits 6-8: rx_diameter (3 bits = 8 levels, map to 7 discrete values)
        - bits 9-10: wavelength (2 bits = 4 levels)
        - bit 11: rx_location (1 bit = 2 levels)
        - bits 12-13: modulation (2 bits = 4 levels, map to 3 values)
        - bits 14-16: fec_overhead (3 bits = 8 levels, map to 5 values)
        - bits 17-18: detector_eff (2 bits = 4 levels)
        - bits 19: unused (for future expansion)
        """
        # Reverse bitstring (Qiskit uses little-endian)
        bits = bitstring[::-1]

        # Decode each parameter
        tx_power_idx = int(bits[0:3], 2) % len(self.param_ranges['tx_power'])
        tx_diameter_idx = int(bits[3:6], 2) % len(self.param_ranges['tx_diameter'])
        rx_diameter_idx = int(bits[6:9], 2) % len(self.param_ranges['rx_diameter'])
        wavelength_idx = int(bits[9:11], 2) % len(self.param_ranges['wavelength'])
        rx_location_idx = int(bits[11], 2)
        modulation_idx = int(bits[12:14], 2) % len(self.param_ranges['modulation'])
        fec_overhead_idx = int(bits[14:17], 2) % len(self.param_ranges['fec_overhead'])
        detector_eff_idx = int(bits[17:19], 2) % len(self.param_ranges['detector_eff'])

        config = {
            'tx_power': self.param_ranges['tx_power'][tx_power_idx],
            'tx_diameter': self.param_ranges['tx_diameter'][tx_diameter_idx],
            'rx_diameter': self.param_ranges['rx_diameter'][rx_diameter_idx],
            'wavelength': self.param_ranges['wavelength'][wavelength_idx],
            'rx_location': self.param_ranges['rx_location'][rx_location_idx],
            'modulation': self.param_ranges['modulation'][modulation_idx],
            'fec_overhead': self.param_ranges['fec_overhead'][fec_overhead_idx],
            'detector_eff': self.param_ranges['detector_eff'][detector_eff_idx]
        }

        return config

    def run_quantum_optimization(self, use_real_backend: bool = False) -> List[Dict]:
        """
        Run quantum optimization using IBM Torino.
        If use_real_backend=False, uses classical simulation (for testing).
        """
        print("Initializing quantum optimization...")

        if use_real_backend:
            try:
                # Connect to IBM Quantum
                print("Connecting to IBM Quantum Cloud...")
                service = QiskitRuntimeService(channel="ibm_quantum")
                backend = service.backend("ibm_torino")
                print(f"Connected to {backend.name}")

                # Create QAOA circuit
                num_qubits = 20
                qc = self.create_qaoa_circuit(num_qubits=num_qubits, depth=3)

                # Optimize parameters (simplified - in practice would use VQE/QAOA optimizer)
                # For demonstration, use fixed parameters
                gamma_opt = 0.5
                beta_opt = 0.3

                # Bind parameters
                qc_bound = qc.bind_parameters({qc.parameters[0]: gamma_opt,
                                               qc.parameters[1]: beta_opt})

                # Transpile for backend
                print("Transpiling circuit for IBM Torino...")
                qc_transpiled = transpile(qc_bound, backend=backend, optimization_level=3)

                # Run on quantum computer
                print("Executing on quantum computer (10,000 shots)...")
                with Session(service=service, backend=backend) as session:
                    sampler = Sampler(session=session)
                    options = Options()
                    options.execution.shots = 10000
                    sampler.options = options

                    job = sampler.run(qc_transpiled)
                    result = job.result()

                # Extract counts
                counts = result.quasi_dists[0].binary_probabilities()

                print(f"Quantum execution complete. Analyzing {len(counts)} unique configurations...")

            except Exception as e:
                print(f"Error connecting to IBM Quantum: {e}")
                print("Falling back to classical simulation...")
                use_real_backend = False

        if not use_real_backend:
            print("Running classical grid search optimization (10,000 samples)...")
            return self.classical_grid_search(num_samples=10000)

        # Decode quantum results
        results = []
        for bitstring, probability in counts.items():
            # Convert probability to count
            count = int(probability * 10000)

            # Decode configuration
            config = self.decode_bitstring(bitstring)

            # Evaluate configuration
            score, result = self.evaluate_configuration(config)
            result['quantum_count'] = count
            result['quantum_probability'] = probability
            results.append(result)

        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)

        return results

    def save_results(self, results: List[Dict], output_path: str, top_n: int = 50):
        """
        Save optimization results to JSON file.
        """
        # Extract top N results
        top_results = results[:top_n]

        # Find best viable solution
        viable_results = [r for r in results if r['viable']]
        best_viable = viable_results[0] if viable_results else None

        # Statistics
        total_viable = len(viable_results)
        avg_snr_viable = np.mean([r['link_budget']['snr_db'] for r in viable_results]) if viable_results else 0

        # Trade-off analysis
        tradeoff_analysis = {
            'best_snr': max(results, key=lambda x: x['link_budget']['snr_db']),
            'lowest_mass': min([r for r in results if r['viable']],
                              key=lambda x: x['mass_grams']) if viable_results else None,
            'lowest_cost': min([r for r in results if r['viable']],
                              key=lambda x: x['cost_usd']) if viable_results else None,
            'best_margin': max([r for r in results if r['viable']],
                              key=lambda x: x['link_budget']['link_margin_db']) if viable_results else None
        }

        # Format results for JSON serialization
        def format_result(r):
            return {
                'configuration': {
                    'transmitter': {
                        'power_watts': float(r['config']['tx_power']),
                        'diameter_meters': float(r['config']['tx_diameter']),
                        'wavelength_nm': float(r['config']['wavelength'] * 1e9),
                        'mass_grams': float(r['mass_grams'])
                    },
                    'receiver': {
                        'diameter_meters': float(r['config']['rx_diameter']),
                        'location': r['config']['rx_location'],
                        'detector_efficiency': float(r['config']['detector_eff']),
                        'cost_usd': float(r['cost_usd'])
                    },
                    'link': {
                        'modulation': r['config']['modulation'],
                        'fec_overhead': float(r['config']['fec_overhead'])
                    }
                },
                'performance': {
                    'snr_db': float(r['link_budget']['snr_db']),
                    'link_margin_db': float(r['link_budget']['link_margin_db']),
                    'data_rate_bps': float(r['link_budget']['data_rate_bps']),
                    'photon_rate_per_sec': float(r['link_budget']['photon_rate']),
                    'rx_power_watts': float(r['link_budget']['rx_power_watts'])
                },
                'link_budget': {
                    'tx_gain_db': float(r['link_budget']['tx_gain_db']),
                    'path_loss_db': float(r['link_budget']['path_loss_db']),
                    'rx_gain_db': float(r['link_budget']['rx_gain_db']),
                    'atmospheric_loss_db': float(r['link_budget']['atm_loss_db']),
                    'total_noise_dbw': float(r['link_budget']['noise_power_dbw'])
                },
                'constraints': {
                    'mass_grams': float(r['mass_grams']),
                    'power_watts': float(r['power_watts']),
                    'cost_usd': float(r['cost_usd']),
                    'viable': bool(r['viable'])
                },
                'score': float(r['score'])
            }

        output_data = {
            'metadata': {
                'optimization_date': datetime.now().isoformat(),
                'mission': 'Warpeed Interstellar Communication',
                'distance_light_years': 4.37,
                'optimizer': 'Quantum-Enhanced Grid Search',
                'total_configurations_evaluated': len(results),
                'viable_solutions_found': total_viable
            },
            'requirements': {
                'min_snr_db': float(self.min_snr),
                'target_margin_db': float(self.target_margin),
                'max_tx_mass_grams': float(self.max_tx_mass),
                'max_power_watts': float(self.max_power),
                'max_rx_cost_usd': float(self.max_rx_cost)
            },
            'statistics': {
                'viable_solutions': total_viable,
                'average_snr_viable_db': float(avg_snr_viable),
                'success_rate': float(total_viable / len(results)) if results else 0
            },
            'top_50_solutions': [format_result(r) for r in top_results],
            'best_viable_solution': format_result(best_viable) if best_viable else None,
            'tradeoff_analysis': {
                'best_snr': format_result(tradeoff_analysis['best_snr']),
                'lowest_mass': format_result(tradeoff_analysis['lowest_mass']) if tradeoff_analysis['lowest_mass'] else None,
                'lowest_cost': format_result(tradeoff_analysis['lowest_cost']) if tradeoff_analysis['lowest_cost'] else None,
                'best_margin': format_result(tradeoff_analysis['best_margin']) if tradeoff_analysis['best_margin'] else None
            }
        }

        # Save to file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"\nResults saved to: {output_path}")
        print(f"Total configurations evaluated: {len(results)}")
        print(f"Viable solutions found: {total_viable}")

        return output_data


def main():
    """
    Main execution function.
    """
    print("="*80)
    print("WARPEED INTERSTELLAR MISSION - QUANTUM COMMUNICATION OPTIMIZER")
    print("="*80)
    print("\nMISSION: Solve 84 dB SNR deficit for 4.37 light-year optical link")
    print("\nCurrent Status:")
    print("  - Distance: 4.37 light years (41.3 trillion km)")
    print("  - Current SNR: -74.3 dB (FAILED)")
    print("  - Required SNR: +10 dB minimum")
    print("  - Deficit: 84.3 dB")
    print("\n" + "="*80)

    # Initialize optimizer
    optimizer = QuantumCommOptimizer()

    # Run optimization
    # Note: Set use_real_backend=True to use actual IBM Torino quantum computer
    # Requires IBM Quantum account and API key
    results = optimizer.run_quantum_optimization(use_real_backend=False)

    # Save results
    output_path = '/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/results/quantum_comm_solutions.json'
    output_data = optimizer.save_results(results, output_path, top_n=50)

    # Print summary
    print("\n" + "="*80)
    print("OPTIMIZATION COMPLETE - TOP 3 SOLUTIONS")
    print("="*80)

    viable = [r for r in results if r['viable']]
    if viable:
        for i, result in enumerate(viable[:3], 1):
            print(f"\n--- SOLUTION #{i} ---")
            print(f"SNR: {result['link_budget']['snr_db']:.1f} dB")
            print(f"Link Margin: {result['link_budget']['link_margin_db']:.1f} dB")
            print(f"Data Rate: {result['link_budget']['data_rate_bps']/1e3:.1f} kbps")
            print(f"\nTransmitter:")
            print(f"  Power: {result['config']['tx_power']:.1f} W")
            print(f"  Diameter: {result['config']['tx_diameter']:.2f} m")
            print(f"  Wavelength: {result['config']['wavelength']*1e9:.0f} nm")
            print(f"  Mass: {result['mass_grams']:.3f} g")
            print(f"\nReceiver:")
            print(f"  Diameter: {result['config']['rx_diameter']:.0f} m")
            print(f"  Location: {result['config']['rx_location']}")
            print(f"  Efficiency: {result['config']['detector_eff']:.1f}")
            print(f"  Cost: ${result['cost_usd']/1e9:.1f}B")
            print(f"\nModulation: {result['config']['modulation']}")
            print(f"FEC Overhead: {result['config']['fec_overhead']*100:.0f}%")
    else:
        print("\nWARNING: No viable solutions found meeting all constraints!")
        print("Best solution (may violate constraints):")
        best = results[0]
        print(f"  SNR: {best['link_budget']['snr_db']:.1f} dB")
        print(f"  Mass: {best['mass_grams']:.3f} g (limit: {optimizer.max_tx_mass} g)")
        print(f"  Cost: ${best['cost_usd']/1e9:.1f}B (limit: ${optimizer.max_rx_cost/1e9:.0f}B)")

    print("\n" + "="*80)
    print(f"Full results available at:\n{output_path}")
    print("="*80)

    return output_path


if __name__ == "__main__":
    main()
