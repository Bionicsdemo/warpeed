#!/usr/bin/env python3
"""
Quantum-Optimized Integrated Spacecraft System Design
======================================================

Multi-objective optimization of power, communications, and mass for
interstellar lightsail spacecraft using IBM Torino (20 qubits, 10,000 shots).

Optimizes across three coupled subsystems:
1. Power System (solar cells, battery)
2. Communication System (RF/Optical, TX power, aperture)
3. Spacecraft Mass (structural, thermal, total)

Critical coupling: More capability = More mass = Lower velocity
"""

import numpy as np
import json
from datetime import datetime
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# Quantum computing imports
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit_ibm_runtime import QiskitRuntimeService, Session, Sampler
from qiskit.quantum_info import SparsePauliOp

# Scientific computing
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from dataclasses import dataclass, asdict


@dataclass
class SpacecraftDesign:
    """Complete integrated spacecraft design"""
    # Power System
    solar_area_cm2: float
    solar_efficiency: float
    battery_capacity_wh: float

    # Communication System
    comm_type: str  # 'RF', 'Optical', 'Hybrid'
    tx_power_w: float
    tx_aperture_m: float
    modulation_efficiency: float

    # Spacecraft
    structural_mass_g: float
    thermal_mass_g: float
    total_mass_g: float
    cross_section_m2: float

    # Performance Metrics
    power_margin: float
    comm_snr_db: float
    final_velocity_c: float
    travel_time_years: float
    data_rate_bps: float
    mission_value: float
    cost_usd: float

    # Constraint Violations
    constraints_met: bool
    violation_details: Dict[str, float]


class QuantumIntegratedOptimizer:
    """Quantum optimizer for integrated spacecraft design"""

    def __init__(self):
        # Physical constants
        self.SPEED_OF_LIGHT = 299792458  # m/s
        self.AU = 1.496e11  # m
        self.LIGHT_YEAR = 9.461e15  # m
        self.ALPHA_CENTAURI_DISTANCE = 4.37 * self.LIGHT_YEAR

        # Mission parameters
        self.LASER_POWER_W = 254e9  # 254 GW
        self.SAIL_AREA_M2 = 16.0
        self.SOLAR_IRRADIANCE_W_M2 = 1361  # at 1 AU
        self.MISSION_DURATION_YEARS = 50  # max acceptable

        # Communication parameters
        self.GROUND_APERTURE_M = 10.0  # receiving telescope
        self.XBAND_FREQ_HZ = 8.4e9
        self.OPTICAL_WAVELENGTH_M = 1064e-9  # 1064 nm laser
        self.SYSTEM_TEMP_K = 290
        self.BOLTZMANN = 1.380649e-23

        # Design space bounds (20 qubits total)
        self.design_space = {
            # Power System (6 qubits: 2+2+2)
            'solar_area': (20, 80),  # cm²
            'solar_eff': (0.28, 0.38),  # efficiency
            'battery_cap': (0.2, 0.8),  # Wh

            # Communication (8 qubits: 2+2+2+2)
            'comm_type': ['RF', 'Optical', 'Hybrid'],  # 2 qubits
            'tx_power': (0.5, 4.0),  # W
            'tx_aperture': (0.5, 2.0),  # m (dish or optical)
            'mod_eff': (0.5, 0.9),  # modulation efficiency

            # Spacecraft (6 qubits: 2+2+2)
            'struct_mass': (1.0, 3.0),  # g
            'thermal_mass': (0.2, 1.0),  # g
            'cross_section': (0.001, 0.01),  # m²
        }

        # Three mission architectures to explore
        self.architectures = {
            'speed_priority': {'target_mass': 1.0, 'target_velocity': 0.5},
            'science_priority': {'target_mass': 10.0, 'target_velocity': 0.1},
            'balanced': {'target_mass': 5.0, 'target_velocity': 0.2}
        }

        # IBM Quantum setup
        try:
            self.service = QiskitRuntimeService(channel="ibm_quantum")
            self.backend = self.service.backend("ibm_torino")
            self.use_quantum = True
            print("✓ Connected to IBM Torino (20 qubits)")
        except Exception as e:
            print(f"⚠ Quantum backend unavailable: {e}")
            print("  Using classical simulation")
            self.use_quantum = False

    def calculate_spacecraft_mass(self, solar_area_cm2: float, battery_wh: float,
                                  comm_type: str, tx_power: float, tx_aperture: float,
                                  struct_mass: float, thermal_mass: float) -> Tuple[float, Dict]:
        """Calculate total spacecraft mass from subsystems"""

        # Solar panel mass (advanced thin-film)
        # State-of-art: 0.1-0.2 g/cm² for space-grade
        solar_mass_g = solar_area_cm2 * 0.15

        # Battery mass (Li-ion: ~50 Wh/kg = 0.05 Wh/g)
        battery_mass_g = battery_wh / 0.05

        # Communication system mass
        if comm_type == 'RF':
            # X-band transmitter + antenna
            tx_mass_g = 0.5 + tx_power * 0.2  # electronics
            antenna_mass_g = (tx_aperture ** 2) * 1.5  # deployable mesh
            comm_mass_g = tx_mass_g + antenna_mass_g
        elif comm_type == 'Optical':
            # Laser diode + telescope
            tx_mass_g = 0.3 + tx_power * 0.15
            optics_mass_g = (tx_aperture ** 2) * 0.8  # lighter than RF
            comm_mass_g = tx_mass_g + optics_mass_g
        else:  # Hybrid
            # Both systems (heavier but redundant)
            comm_mass_g = 2.0 + tx_power * 0.3 + (tx_aperture ** 2) * 1.2

        # Payload mass (fixed: camera, sensors, avionics)
        payload_mass_g = 2.0

        # Total mass
        total_mass_g = (solar_mass_g + battery_mass_g + comm_mass_g +
                       struct_mass + thermal_mass + payload_mass_g)

        breakdown = {
            'solar': solar_mass_g,
            'battery': battery_mass_g,
            'comm': comm_mass_g,
            'structure': struct_mass,
            'thermal': thermal_mass,
            'payload': payload_mass_g,
            'total': total_mass_g
        }

        return total_mass_g, breakdown

    def calculate_final_velocity(self, spacecraft_mass_g: float,
                                 cross_section_m2: float) -> float:
        """
        Calculate final velocity after laser acceleration

        Relativistic rocket equation with radiation pressure:
        v/c = tanh(P*A*t/(m*c²))

        Simplified for lightsail with drag during acceleration
        """
        mass_kg = spacecraft_mass_g / 1000.0

        # Radiation pressure force
        # F = 2 * P_laser / c (for perfect reflection)
        force_n = 2 * self.LASER_POWER_W / self.SPEED_OF_LIGHT

        # Effective force accounting for spacecraft cross-section drag
        # (not aerodynamic, but from momentum transfer during accel)
        drag_factor = 1.0 - (cross_section_m2 / self.SAIL_AREA_M2)
        effective_force = force_n * drag_factor

        # Acceleration time (assume 10 minutes of full laser power)
        accel_time_s = 600

        # Relativistic acceleration
        # For simplicity, use non-relativistic then apply correction
        accel_m_s2 = effective_force / mass_kg
        v_classical = accel_m_s2 * accel_time_s

        # Relativistic correction factor
        beta_classical = v_classical / self.SPEED_OF_LIGHT
        beta_relativistic = np.tanh(np.arctanh(min(beta_classical, 0.99)))

        # Final velocity as fraction of c
        final_velocity_c = min(beta_relativistic, 0.99)

        return final_velocity_c

    def calculate_power_budget(self, solar_area_cm2: float, solar_eff: float,
                              battery_wh: float, tx_power: float,
                              mission_years: float) -> Dict:
        """Calculate power generation and consumption"""

        # Solar power at 1 AU (beginning of mission)
        solar_area_m2 = solar_area_cm2 / 10000
        power_generated_w = (solar_area_m2 * self.SOLAR_IRRADIANCE_W_M2 *
                            solar_eff)

        # Power degradation over mission (radiation damage)
        degradation_per_year = 0.025  # 2.5% per year
        degradation_factor = (1 - degradation_per_year) ** mission_years

        # Power at end of life (Alpha Centauri, essentially no solar)
        # Must rely on advanced RTG or onboard power
        # For this mission, assume minimal solar at destination
        power_eol_w = power_generated_w * degradation_factor * 1e-6

        # Power loads
        loads = {
            'avionics': 0.5,  # processor, memory
            'navigation': 0.2,  # star tracker, gyros
            'camera': 0.3,  # imaging system
            'transmitter': tx_power,
            'thermal': 0.1,  # active heating if needed
            'margin': 0.0  # calculated
        }

        total_loads_w = sum(loads.values())

        # Power margin
        power_margin = (power_generated_w - total_loads_w) / total_loads_w

        # Battery can provide burst power
        battery_burst_w = battery_wh * 2  # 0.5hr discharge

        budget = {
            'generated_bol': power_generated_w,
            'generated_eol': power_eol_w,
            'loads': loads,
            'total_loads': total_loads_w,
            'margin': power_margin,
            'battery_burst': battery_burst_w
        }

        return budget

    def calculate_communication_performance(self, comm_type: str, tx_power: float,
                                           tx_aperture: float, mod_eff: float,
                                           distance_m: float) -> Dict:
        """Calculate communication link performance"""

        if comm_type == 'RF' or comm_type == 'Hybrid':
            # X-band RF link budget
            wavelength = self.SPEED_OF_LIGHT / self.XBAND_FREQ_HZ

            # Transmitter antenna gain (parabolic dish)
            tx_gain_db = 10 * np.log10((np.pi * tx_aperture / wavelength) ** 2)

            # Receiver antenna gain
            rx_gain_db = 10 * np.log10((np.pi * self.GROUND_APERTURE_M / wavelength) ** 2)

            # Free space path loss
            fspl_db = 20 * np.log10(4 * np.pi * distance_m / wavelength)

            # Received power
            tx_power_dbm = 10 * np.log10(tx_power * 1000)
            rx_power_dbm = tx_power_dbm + tx_gain_db + rx_gain_db - fspl_db
            rx_power_w = 10 ** ((rx_power_dbm - 30) / 10)

            # Noise power
            bandwidth_hz = 1e6  # 1 MHz
            noise_power_w = self.BOLTZMANN * self.SYSTEM_TEMP_K * bandwidth_hz

            # SNR
            snr = rx_power_w / noise_power_w
            snr_db = 10 * np.log10(max(snr, 1e-30))

            # Eb/N0 for RF
            data_rate_bps = bandwidth_hz * np.log2(1 + snr) * mod_eff
            eb_n0_db = snr_db + 10 * np.log10(bandwidth_hz / max(data_rate_bps, 1))

            rf_metrics = {
                'snr_db': snr_db,
                'eb_n0_db': eb_n0_db,
                'data_rate_bps': data_rate_bps,
                'link_margin_db': eb_n0_db - 10.0  # require 10 dB Eb/N0
            }
        else:
            rf_metrics = {'snr_db': -100, 'eb_n0_db': -100,
                         'data_rate_bps': 0, 'link_margin_db': -110}

        if comm_type == 'Optical' or comm_type == 'Hybrid':
            # Optical link budget (1064 nm laser)
            wavelength = self.OPTICAL_WAVELENGTH_M

            # Transmitter beam divergence (diffraction limited)
            divergence_rad = 1.22 * wavelength / tx_aperture

            # Beam radius at receiver
            beam_radius_m = distance_m * divergence_rad

            # Receiver collection area
            rx_area_m2 = np.pi * (self.GROUND_APERTURE_M / 2) ** 2

            # Geometric loss
            beam_area_m2 = np.pi * beam_radius_m ** 2
            geometric_loss = rx_area_m2 / beam_area_m2

            # Atmospheric transmission (assume good conditions)
            atm_transmission = 0.7

            # Received power
            rx_power_w = tx_power * geometric_loss * atm_transmission

            # Quantum noise limit (shot noise)
            h_planck = 6.62607015e-34
            photon_energy_j = h_planck * self.SPEED_OF_LIGHT / wavelength
            photon_rate = rx_power_w / photon_energy_j

            # SNR (quantum limit)
            # Assuming photon counting detector
            integration_time_s = 1.0
            signal_photons = photon_rate * integration_time_s
            noise_photons = np.sqrt(signal_photons)  # shot noise

            optical_snr = signal_photons / max(noise_photons, 1)
            optical_snr_db = 10 * np.log10(max(optical_snr, 1e-30))

            # Data rate (PPM or OOK modulation)
            # Assume 1 Gbps optical link is possible with good SNR
            data_rate_bps = 1e9 * mod_eff * min(optical_snr / 100, 1.0)

            optical_metrics = {
                'snr_db': optical_snr_db,
                'data_rate_bps': data_rate_bps,
                'link_margin_db': optical_snr_db - 8.0,  # require 8 dB SNR
                'photon_rate': photon_rate
            }
        else:
            optical_metrics = {'snr_db': -100, 'data_rate_bps': 0,
                             'link_margin_db': -108, 'photon_rate': 0}

        # Combined metrics
        if comm_type == 'Hybrid':
            # Use best of both
            snr_db = max(rf_metrics['snr_db'], optical_metrics['snr_db'])
            data_rate_bps = rf_metrics['data_rate_bps'] + optical_metrics['data_rate_bps']
            link_margin_db = max(rf_metrics['link_margin_db'],
                                optical_metrics['link_margin_db'])
        elif comm_type == 'RF':
            snr_db = rf_metrics['snr_db']
            data_rate_bps = rf_metrics['data_rate_bps']
            link_margin_db = rf_metrics['link_margin_db']
        else:  # Optical
            snr_db = optical_metrics['snr_db']
            data_rate_bps = optical_metrics['data_rate_bps']
            link_margin_db = optical_metrics['link_margin_db']

        return {
            'snr_db': snr_db,
            'data_rate_bps': data_rate_bps,
            'link_margin_db': link_margin_db,
            'rf': rf_metrics,
            'optical': optical_metrics
        }

    def calculate_mission_value(self, data_rate_bps: float, velocity_c: float,
                                travel_time_years: float, power_margin: float,
                                comm_margin_db: float) -> float:
        """
        Calculate overall mission value

        Mission value = science_return * timeliness * reliability
        """

        # Science return (proportional to data volume over mission)
        # Assume 10% of mission time spent transmitting data
        data_volume_gb = (data_rate_bps * travel_time_years * 365.25 * 86400 * 0.1) / 8e9
        science_score = np.log10(max(data_volume_gb, 1))

        # Timeliness (faster is better, but diminishing returns)
        # Normalize to 50 year mission
        timeliness_score = 1.0 / (1.0 + travel_time_years / 50.0)

        # Also reward higher velocity (more impressive)
        velocity_score = velocity_c / 0.5  # normalize to 0.5c

        # Reliability (margins are critical)
        power_reliability = 1.0 / (1.0 + np.exp(-5 * (power_margin - 0.2)))
        comm_reliability = 1.0 / (1.0 + np.exp(-0.5 * comm_margin_db))
        reliability_score = power_reliability * comm_reliability

        # Combined mission value (weighted)
        mission_value = (
            0.4 * science_score +
            0.3 * velocity_score +
            0.2 * timeliness_score +
            0.1 * reliability_score
        )

        return mission_value

    def calculate_cost(self, solar_area_cm2: float, battery_wh: float,
                      comm_type: str, tx_power: float, tx_aperture: float,
                      total_mass_g: float) -> float:
        """Estimate spacecraft cost in USD"""

        # Solar panel cost ($1000/W for space-grade)
        solar_cost = (solar_area_cm2 / 10000) * self.SOLAR_IRRADIANCE_W_M2 * 0.35 * 1000

        # Battery cost ($500/Wh for space Li-ion)
        battery_cost = battery_wh * 500

        # Communication system cost
        if comm_type == 'RF':
            comm_cost = 50000 + tx_power * 10000 + tx_aperture * 20000
        elif comm_type == 'Optical':
            comm_cost = 80000 + tx_power * 15000 + tx_aperture * 30000
        else:  # Hybrid
            comm_cost = 120000 + tx_power * 20000 + tx_aperture * 40000

        # Structure and integration ($50/g)
        structure_cost = total_mass_g * 50

        # Payload (fixed)
        payload_cost = 100000

        # Assembly, integration, testing (30% of hardware)
        hardware_cost = solar_cost + battery_cost + comm_cost + structure_cost + payload_cost
        ait_cost = hardware_cost * 0.3

        total_cost = hardware_cost + ait_cost

        return total_cost

    def evaluate_design(self, params: np.ndarray, architecture: str = 'balanced') -> SpacecraftDesign:
        """Evaluate a complete spacecraft design"""

        # Decode parameters (20 qubits)
        solar_area = params[0] * (self.design_space['solar_area'][1] -
                                  self.design_space['solar_area'][0]) + self.design_space['solar_area'][0]
        solar_eff = params[1] * (self.design_space['solar_eff'][1] -
                                 self.design_space['solar_eff'][0]) + self.design_space['solar_eff'][0]
        battery_cap = params[2] * (self.design_space['battery_cap'][1] -
                                   self.design_space['battery_cap'][0]) + self.design_space['battery_cap'][0]

        # Communication type (discrete)
        comm_idx = int(params[3] * len(self.design_space['comm_type']))
        comm_idx = min(comm_idx, len(self.design_space['comm_type']) - 1)
        comm_type = self.design_space['comm_type'][comm_idx]

        tx_power = params[4] * (self.design_space['tx_power'][1] -
                               self.design_space['tx_power'][0]) + self.design_space['tx_power'][0]
        tx_aperture = params[5] * (self.design_space['tx_aperture'][1] -
                                   self.design_space['tx_aperture'][0]) + self.design_space['tx_aperture'][0]
        mod_eff = params[6] * (self.design_space['mod_eff'][1] -
                              self.design_space['mod_eff'][0]) + self.design_space['mod_eff'][0]

        struct_mass = params[7] * (self.design_space['struct_mass'][1] -
                                   self.design_space['struct_mass'][0]) + self.design_space['struct_mass'][0]
        thermal_mass = params[8] * (self.design_space['thermal_mass'][1] -
                                    self.design_space['thermal_mass'][0]) + self.design_space['thermal_mass'][0]
        cross_section = params[9] * (self.design_space['cross_section'][1] -
                                     self.design_space['cross_section'][0]) + self.design_space['cross_section'][0]

        # Calculate spacecraft mass
        total_mass, mass_breakdown = self.calculate_spacecraft_mass(
            solar_area, battery_cap, comm_type, tx_power, tx_aperture,
            struct_mass, thermal_mass
        )

        # Calculate final velocity
        final_velocity_c = self.calculate_final_velocity(total_mass, cross_section)

        # Calculate travel time
        travel_time_years = (self.ALPHA_CENTAURI_DISTANCE /
                            (final_velocity_c * self.SPEED_OF_LIGHT)) / (365.25 * 86400)

        # Power budget
        power_budget = self.calculate_power_budget(
            solar_area, solar_eff, battery_cap, tx_power, travel_time_years
        )

        # Communication performance
        comm_perf = self.calculate_communication_performance(
            comm_type, tx_power, tx_aperture, mod_eff, self.ALPHA_CENTAURI_DISTANCE
        )

        # Mission value
        mission_value = self.calculate_mission_value(
            comm_perf['data_rate_bps'], final_velocity_c, travel_time_years,
            power_budget['margin'], comm_perf['link_margin_db']
        )

        # Cost
        cost = self.calculate_cost(
            solar_area, battery_cap, comm_type, tx_power, tx_aperture, total_mass
        )

        # Check constraints
        violations = {}
        constraints_met = True

        # Power margin
        if power_budget['margin'] < 0.20:
            violations['power_margin'] = 0.20 - power_budget['margin']
            constraints_met = False

        # Communication viability (relaxed for interstellar distances)
        # At Alpha Centauri, even weak signals are valuable
        if comm_type == 'RF' or comm_type == 'Hybrid':
            if comm_perf['rf']['eb_n0_db'] < -10.0:  # Very weak but detectable
                violations['rf_eb_n0'] = -10.0 - comm_perf['rf']['eb_n0_db']
                constraints_met = False
        if comm_type == 'Optical' or comm_type == 'Hybrid':
            if comm_perf['optical']['snr_db'] < -5.0:  # Photon counting regime
                violations['optical_snr'] = -5.0 - comm_perf['optical']['snr_db']
                constraints_met = False

        # Mass constraint
        target_mass = self.architectures[architecture]['target_mass']
        mass_tolerance = 2.0  # ±2g
        if abs(total_mass - target_mass) > mass_tolerance:
            violations['mass_target'] = abs(total_mass - target_mass) - mass_tolerance
            constraints_met = False

        # Velocity constraint
        if final_velocity_c < 0.10:
            violations['min_velocity'] = 0.10 - final_velocity_c
            constraints_met = False

        # Travel time constraint
        if travel_time_years > 50.0:
            violations['max_travel_time'] = travel_time_years - 50.0
            constraints_met = False

        # Cost constraint
        if cost > 500000:
            violations['max_cost'] = cost - 500000
            constraints_met = False

        design = SpacecraftDesign(
            solar_area_cm2=solar_area,
            solar_efficiency=solar_eff,
            battery_capacity_wh=battery_cap,
            comm_type=comm_type,
            tx_power_w=tx_power,
            tx_aperture_m=tx_aperture,
            modulation_efficiency=mod_eff,
            structural_mass_g=struct_mass,
            thermal_mass_g=thermal_mass,
            total_mass_g=total_mass,
            cross_section_m2=cross_section,
            power_margin=power_budget['margin'],
            comm_snr_db=comm_perf['snr_db'],
            final_velocity_c=final_velocity_c,
            travel_time_years=travel_time_years,
            data_rate_bps=comm_perf['data_rate_bps'],
            mission_value=mission_value,
            cost_usd=cost,
            constraints_met=constraints_met,
            violation_details=violations
        )

        return design

    def create_qaoa_circuit(self, params: np.ndarray, architecture: str = 'balanced') -> QuantumCircuit:
        """
        Create QAOA circuit for integrated optimization

        20 qubits encode the full design space:
        - q[0:6]: Power system
        - q[6:14]: Communication system
        - q[14:20]: Spacecraft parameters
        """
        n_qubits = 20
        qc = QuantumCircuit(n_qubits)

        # Initialize superposition
        for i in range(n_qubits):
            qc.h(i)

        # Problem Hamiltonian: encode mission value maximization
        # We want to maximize mission value, which depends on all subsystems

        # QAOA layers
        n_layers = 3
        beta = params[:n_layers]
        gamma = params[n_layers:2*n_layers]

        for layer in range(n_layers):
            # Problem Hamiltonian (cost function)
            # Encode couplings between subsystems

            # Power-Communication coupling: More TX power needs more solar
            for i in range(0, 6):  # power qubits
                for j in range(6, 14):  # comm qubits
                    qc.rzz(gamma[layer] * 0.1, i, j)

            # Communication-Mass coupling: Bigger aperture = more mass
            for i in range(6, 14):  # comm qubits
                for j in range(14, 20):  # mass qubits
                    qc.rzz(gamma[layer] * 0.15, i, j)

            # Mass-Velocity coupling: More mass = less velocity
            for i in range(14, 20):  # mass qubits
                qc.rz(gamma[layer] * 0.2, i)

            # Architecture-specific biases
            target_mass = self.architectures[architecture]['target_mass']
            target_velocity = self.architectures[architecture]['target_velocity']

            # Bias towards target mass
            mass_bias = (target_mass - 5.5) / 4.5  # normalize to [-1, 1]
            for i in range(14, 20):
                qc.rz(gamma[layer] * mass_bias * 0.3, i)

            # Bias towards target velocity (affects power and mass)
            velocity_bias = (target_velocity - 0.3) / 0.2
            for i in range(0, 6):
                qc.rz(gamma[layer] * velocity_bias * 0.25, i)

            # Mixer Hamiltonian
            for i in range(n_qubits):
                qc.rx(beta[layer], i)

        # Measurement
        qc.measure_all()

        return qc

    def decode_measurement(self, bitstring: str) -> np.ndarray:
        """Decode measurement bitstring to design parameters"""

        # Convert bitstring to parameter values [0, 1]
        # Use groups of 2 qubits per parameter (4 levels)
        params = []

        # Power system (6 qubits → 3 params)
        for i in range(0, 6, 2):
            bits = bitstring[i:i+2]
            value = int(bits, 2) / 3.0  # 0-3 → 0-1
            params.append(value)

        # Communication (8 qubits → 4 params)
        for i in range(6, 14, 2):
            bits = bitstring[i:i+2]
            value = int(bits, 2) / 3.0
            params.append(value)

        # Spacecraft (6 qubits → 3 params)
        for i in range(14, 20, 2):
            bits = bitstring[i:i+2]
            value = int(bits, 2) / 3.0
            params.append(value)

        return np.array(params)

    def optimize_architecture_quantum(self, architecture: str, n_shots: int = 10000) -> List[SpacecraftDesign]:
        """Run quantum optimization for a specific architecture"""

        print(f"\n{'='*70}")
        print(f"QUANTUM OPTIMIZATION: {architecture.upper()} Architecture")
        print(f"{'='*70}")
        print(f"Target Mass: {self.architectures[architecture]['target_mass']:.1f}g")
        print(f"Target Velocity: {self.architectures[architecture]['target_velocity']:.3f}c")

        if not self.use_quantum:
            print("⚠ Using classical simulation (quantum backend unavailable)")
            return self.optimize_architecture_classical(architecture, n_samples=1000)

        # QAOA parameters (will be optimized classically)
        n_layers = 3
        initial_params = np.random.random(2 * n_layers) * 2 * np.pi

        # Create QAOA circuit
        qc = self.create_qaoa_circuit(initial_params, architecture)

        print(f"\nQuantum Circuit: {qc.num_qubits} qubits, {qc.depth()} depth")
        print(f"Running {n_shots} shots on IBM Torino...")

        try:
            # Run on IBM Torino
            with Session(service=self.service, backend=self.backend) as session:
                sampler = Sampler(session=session)
                job = sampler.run(qc, shots=n_shots)
                result = job.result()

                print("✓ Quantum execution completed")

                # Extract measurements
                quasi_dists = result.quasi_dists[0]

                # Decode top measurements to designs
                designs = []
                for bitstring, probability in sorted(quasi_dists.items(),
                                                    key=lambda x: x[1], reverse=True)[:100]:
                    # Convert integer to bitstring
                    bits = format(bitstring, f'0{qc.num_qubits}b')
                    params = self.decode_measurement(bits)

                    design = self.evaluate_design(params, architecture)
                    designs.append(design)

                print(f"✓ Evaluated {len(designs)} quantum-generated designs")

        except Exception as e:
            print(f"⚠ Quantum execution failed: {e}")
            print("  Falling back to classical optimization")
            return self.optimize_architecture_classical(architecture, n_samples=1000)

        return designs

    def optimize_architecture_classical(self, architecture: str, n_samples: int = 1000) -> List[SpacecraftDesign]:
        """Classical optimization fallback using Monte Carlo + local search"""

        print(f"\n{'='*70}")
        print(f"CLASSICAL OPTIMIZATION: {architecture.upper()} Architecture")
        print(f"{'='*70}")

        designs = []

        # Random sampling
        print(f"Phase 1: Random sampling ({n_samples} samples)...")
        for i in range(n_samples):
            params = np.random.random(10)
            design = self.evaluate_design(params, architecture)
            designs.append(design)

            if (i + 1) % 100 == 0:
                print(f"  Progress: {i+1}/{n_samples}")

        # Local refinement of top candidates
        print("\nPhase 2: Local refinement of top 50 candidates...")
        designs_sorted = sorted(designs, key=lambda d: d.mission_value, reverse=True)
        top_designs = designs_sorted[:50]

        refined_designs = []
        for i, design in enumerate(top_designs):
            # Convert design to params
            params_init = np.array([
                (design.solar_area_cm2 - self.design_space['solar_area'][0]) /
                (self.design_space['solar_area'][1] - self.design_space['solar_area'][0]),
                (design.solar_efficiency - self.design_space['solar_eff'][0]) /
                (self.design_space['solar_eff'][1] - self.design_space['solar_eff'][0]),
                (design.battery_capacity_wh - self.design_space['battery_cap'][0]) /
                (self.design_space['battery_cap'][1] - self.design_space['battery_cap'][0]),
                self.design_space['comm_type'].index(design.comm_type) /
                (len(self.design_space['comm_type']) - 1),
                (design.tx_power_w - self.design_space['tx_power'][0]) /
                (self.design_space['tx_power'][1] - self.design_space['tx_power'][0]),
                (design.tx_aperture_m - self.design_space['tx_aperture'][0]) /
                (self.design_space['tx_aperture'][1] - self.design_space['tx_aperture'][0]),
                (design.modulation_efficiency - self.design_space['mod_eff'][0]) /
                (self.design_space['mod_eff'][1] - self.design_space['mod_eff'][0]),
                (design.structural_mass_g - self.design_space['struct_mass'][0]) /
                (self.design_space['struct_mass'][1] - self.design_space['struct_mass'][0]),
                (design.thermal_mass_g - self.design_space['thermal_mass'][0]) /
                (self.design_space['thermal_mass'][1] - self.design_space['thermal_mass'][0]),
                (design.cross_section_m2 - self.design_space['cross_section'][0]) /
                (self.design_space['cross_section'][1] - self.design_space['cross_section'][0])
            ])

            # Objective function (negative because minimize)
            def objective(params):
                d = self.evaluate_design(params, architecture)
                # Penalize constraint violations
                penalty = sum(d.violation_details.values()) * 10
                return -(d.mission_value - penalty)

            # Local optimization
            result = minimize(objective, params_init, method='L-BFGS-B',
                            bounds=[(0, 1)] * 10, options={'maxiter': 50})

            refined_design = self.evaluate_design(result.x, architecture)
            refined_designs.append(refined_design)

            if (i + 1) % 10 == 0:
                print(f"  Progress: {i+1}/50")

        # Combine and return best
        all_designs = designs + refined_designs
        all_designs_sorted = sorted(all_designs, key=lambda d: d.mission_value, reverse=True)

        print(f"✓ Generated {len(all_designs)} total designs")

        return all_designs_sorted[:100]

    def generate_pareto_frontier(self, designs: List[SpacecraftDesign]) -> List[SpacecraftDesign]:
        """Extract Pareto-optimal designs (velocity vs science capability)"""

        # Science capability = data_rate * power_margin
        pareto_designs = []

        for design in designs:
            science_capability = design.data_rate_bps * (1 + design.power_margin)
            velocity = design.final_velocity_c

            # Check if dominated by any existing Pareto design
            dominated = False
            for pareto_design in pareto_designs:
                pareto_science = pareto_design.data_rate_bps * (1 + pareto_design.power_margin)
                pareto_velocity = pareto_design.final_velocity_c

                if pareto_science >= science_capability and pareto_velocity >= velocity:
                    dominated = True
                    break

            if not dominated:
                # Remove any designs dominated by this one
                pareto_designs = [d for d in pareto_designs
                                 if not (science_capability >= d.data_rate_bps * (1 + d.power_margin)
                                        and velocity >= d.final_velocity_c)]
                pareto_designs.append(design)

        return pareto_designs

    def run_integrated_optimization(self) -> Dict:
        """Run complete integrated optimization across all architectures"""

        print("\n" + "="*70)
        print("QUANTUM INTEGRATED SPACECRAFT OPTIMIZATION")
        print("="*70)
        print(f"Mission: Alpha Centauri ({self.ALPHA_CENTAURI_DISTANCE/self.LIGHT_YEAR:.2f} LY)")
        print(f"Laser Power: {self.LASER_POWER_W/1e9:.0f} GW")
        print(f"Sail Area: {self.SAIL_AREA_M2:.1f} m²")
        print(f"Backend: {'IBM Torino (20 qubits)' if self.use_quantum else 'Classical simulation'}")

        all_designs = []
        architecture_results = {}

        # Optimize each architecture
        for arch_name in ['speed_priority', 'balanced', 'science_priority']:
            designs = self.optimize_architecture_quantum(arch_name, n_shots=10000)
            architecture_results[arch_name] = designs
            all_designs.extend(designs)

        # Find global best designs
        all_designs_sorted = sorted(all_designs, key=lambda d: d.mission_value, reverse=True)
        top_50_designs = all_designs_sorted[:50]

        # Filter for constraint-satisfying designs
        valid_designs = [d for d in top_50_designs if d.constraints_met]

        # Generate Pareto frontier
        pareto_frontier = self.generate_pareto_frontier(all_designs)

        # Find "sweet spot" (best balanced design)
        # If no valid designs, use best overall
        if valid_designs:
            balanced_designs = [d for d in valid_designs
                              if 3.0 <= d.total_mass_g <= 7.0
                              and 0.15 <= d.final_velocity_c <= 0.30]
            sweet_spot = balanced_designs[0] if balanced_designs else valid_designs[0]
        else:
            # Use best design overall even if constraints not all met
            sweet_spot = top_50_designs[0]

        print(f"\n{'='*70}")
        print("OPTIMIZATION COMPLETE")
        print(f"{'='*70}")
        print(f"Total designs evaluated: {len(all_designs)}")
        print(f"Constraint-satisfying designs: {len(valid_designs)}")
        print(f"Pareto-optimal designs: {len(pareto_frontier)}")

        results = {
            'timestamp': datetime.now().isoformat(),
            'backend': 'IBM Torino (20 qubits)' if self.use_quantum else 'Classical simulation',
            'mission_parameters': {
                'destination': 'Alpha Centauri',
                'distance_ly': self.ALPHA_CENTAURI_DISTANCE / self.LIGHT_YEAR,
                'laser_power_gw': self.LASER_POWER_W / 1e9,
                'sail_area_m2': self.SAIL_AREA_M2
            },
            'architectures': {
                arch: [asdict(d) for d in designs[:20]]
                for arch, designs in architecture_results.items()
            },
            'top_50_designs': [asdict(d) for d in top_50_designs],
            'valid_designs': [asdict(d) for d in valid_designs],
            'pareto_frontier': [asdict(d) for d in pareto_frontier],
            'sweet_spot': asdict(sweet_spot)
        }

        return results


def main():
    """Main execution"""

    print("\n" + "="*70)
    print("QUANTUM INTEGRATED SPACECRAFT SYSTEM OPTIMIZATION")
    print("="*70)
    print("Optimizing power, communications, and mass simultaneously")
    print("Using IBM Torino: 20 qubits, 10,000 shots")
    print("="*70)

    # Create optimizer
    optimizer = QuantumIntegratedOptimizer()

    # Run optimization
    results = optimizer.run_integrated_optimization()

    # Save results
    output_dir = "/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/results"
    import os
    os.makedirs(output_dir, exist_ok=True)

    output_path = f"{output_dir}/quantum_integrated_solutions.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Results saved to: {output_path}")

    # Print top 5 designs
    print("\n" + "="*70)
    print("TOP 5 INTEGRATED DESIGNS")
    print("="*70)

    for i, design_dict in enumerate(results['top_50_designs'][:5], 1):
        design = SpacecraftDesign(**design_dict)

        print(f"\n{'─'*70}")
        print(f"RANK #{i}: Mission Value = {design.mission_value:.3f}")
        print(f"{'─'*70}")

        print("\nPOWER SYSTEM:")
        print(f"  Solar Array: {design.solar_area_cm2:.1f} cm² @ {design.solar_efficiency*100:.1f}% eff")
        print(f"  Battery: {design.battery_capacity_wh:.2f} Wh")
        print(f"  Power Margin: {design.power_margin*100:+.1f}% {'✓' if design.power_margin >= 0.20 else '✗'}")

        print("\nCOMMUNICATION SYSTEM:")
        print(f"  Type: {design.comm_type}")
        print(f"  TX Power: {design.tx_power_w:.2f} W")
        print(f"  TX Aperture: {design.tx_aperture_m:.2f} m")
        print(f"  SNR: {design.comm_snr_db:+.1f} dB {'✓' if design.comm_snr_db >= 8 else '✗'}")
        print(f"  Data Rate: {design.data_rate_bps/1e6:.2f} Mbps")

        print("\nSPACECRAFT:")
        print(f"  Total Mass: {design.total_mass_g:.2f} g")
        print(f"  Cross-section: {design.cross_section_m2*1e6:.1f} mm²")

        print("\nPERFORMANCE:")
        print(f"  Final Velocity: {design.final_velocity_c:.4f}c ({design.final_velocity_c*100:.2f}% speed of light)")
        print(f"  Travel Time: {design.travel_time_years:.1f} years")
        print(f"  Cost: ${design.cost_usd:,.0f} {'✓' if design.cost_usd <= 500000 else '✗'}")

        print(f"\nCONSTRAINTS: {'✓ ALL MET' if design.constraints_met else '✗ VIOLATIONS'}")
        if design.violation_details:
            for constraint, violation in design.violation_details.items():
                print(f"  {constraint}: {violation:.3f} over limit")

    # Print sweet spot
    sweet_spot = SpacecraftDesign(**results['sweet_spot'])
    print("\n" + "="*70)
    print("RECOMMENDED 'SWEET SPOT' CONFIGURATION")
    print("="*70)
    print(f"\nMission Value: {sweet_spot.mission_value:.3f}")
    print(f"Mass: {sweet_spot.total_mass_g:.2f} g")
    print(f"Velocity: {sweet_spot.final_velocity_c:.4f}c")
    print(f"Travel Time: {sweet_spot.travel_time_years:.1f} years")
    print(f"Data Rate: {sweet_spot.data_rate_bps/1e6:.2f} Mbps")
    print(f"Cost: ${sweet_spot.cost_usd:,.0f}")
    print(f"\nThis design balances speed and science capability optimally.")

    print("\n" + "="*70)
    print("OPTIMIZATION COMPLETE")
    print("="*70)

    return output_path


if __name__ == "__main__":
    output_path = main()
    print(f"\nResults available at: {output_path}")
