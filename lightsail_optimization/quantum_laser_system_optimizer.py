#!/usr/bin/env python3
"""
QUANTUM LASER SYSTEM OPTIMIZER - IBM TORINO (133 qubits)
========================================================

PURPOSE: Quantum-validated design of phased array laser propulsion system
         for Warpeed lightsail acceleration to 0.50c

APPROACH: Encode laser system parameters in quantum superposition to explore
          optimal configurations for power, coherence, thermal management,
          cost, and manufacturability

TARGET: 100 GW phased array laser system @ 1064nm (Nd:YAG baseline)

AUTHOR: Warpeed Team
DATE: October 16, 2025
QUANTUM BACKEND: IBM Torino (133 qubits)
"""

import numpy as np
import json
from datetime import datetime
from pathlib import Path
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler

# ============================================================================
# IBM QUANTUM CONFIGURATION
# ============================================================================

IBM_API_KEY = 'bFodPcl5hR0To4S_FHWLA0GeYSm82dIQ5zTwUhVoGxwT'

# Configuration for IBM Torino
N_QUBITS = 24  # Increased to encode more laser parameters
N_SHOTS = 5000  # Balance between precision and execution time (~5 min target)

# ============================================================================
# LASER SYSTEM DESIGN SPACE
# ============================================================================

LASER_DESIGN_PARAMETERS = {
    'phased_array': {
        'element_count_range': [100, 500, 1000, 2000, 5000, 10000],  # individual lasers
        'geometry_types': ['square_grid', 'hexagonal', 'fibonacci_spiral', 'optimized_sparse'],
        'element_spacing_m': [0.5, 1.0, 2.0, 5.0],  # spacing between elements
        'total_aperture_m': [10, 50, 100, 200, 500, 1000],  # total array diameter
    },
    'laser_technology': {
        'type': ['Nd_YAG_solid_state', 'Fiber_laser', 'Diode_laser', 'Free_electron_laser'],
        'wavelength_nm': [1064, 1030, 1550, 808],  # primary wavelengths
        'pulse_mode': ['CW', 'pulsed_ns', 'pulsed_ps', 'pulsed_fs'],
        'wall_plug_efficiency': [0.15, 0.25, 0.35, 0.50],  # electrical to optical
    },
    'power_configuration': {
        'power_per_element_kW': [10, 50, 100, 200, 500, 1000],
        'total_system_power_GW': [10, 25, 50, 100, 150, 200],
        'peak_intensity_GW_m2': [1, 5, 10, 50, 100],  # at lightsail
        'acceleration_duration_min': [5, 10, 20, 30, 60],
    },
    'beam_quality': {
        'M2_factor': [1.0, 1.2, 1.5, 2.0],  # 1.0 = perfect Gaussian
        'beam_divergence_urad': [0.1, 0.5, 1.0, 5.0, 10.0],
        'coherence_length_m': [100, 1000, 10000, 100000],
        'atmospheric_transmission': [0.70, 0.80, 0.85, 0.90, 0.95],  # adaptive optics
    },
    'thermal_management': {
        'cooling_system': ['liquid_nitrogen', 'liquid_helium', 'cryogenic_closed_loop', 'water_cooling'],
        'heat_dissipation_MW': [10, 50, 100, 200, 500],
        'operating_temp_K': [77, 150, 273, 300, 350],
        'thermal_stability_mK': [1, 10, 50, 100],  # temperature control precision
    },
    'materials': {
        'laser_crystal': ['Nd_YAG', 'Nd_YVO4', 'Yb_YAG', 'Ti_Sapphire'],
        'optics_substrate': ['Fused_silica', 'Zerodur', 'ULE_glass', 'Single_crystal_sapphire'],
        'coating_type': ['dielectric_multilayer', 'metal_enhanced', 'hybrid_coating'],
        'CAS_numbers': {
            'Nd_YAG': '12005-21-9',
            'Nd_YVO4': '13721-39-6',
            'Yb_YAG': '12005-21-9',  # Same base as Nd:YAG
            'Fused_silica': '60676-86-0',
        }
    },
    'cost_analysis': {
        'cost_per_element_USD': [50000, 100000, 250000, 500000, 1000000],
        'total_system_cost_M_USD': [100, 500, 1000, 2000, 5000, 10000],
        'operating_cost_per_shot_USD': [10000, 50000, 100000, 500000, 1000000],
        'maintenance_cost_annual_M_USD': [1, 5, 10, 25, 50, 100],
    },
    'location': {
        'site_type': ['ground_based_desert', 'high_altitude_mountain', 'space_based_LEO', 'lunar_surface'],
        'altitude_m': [0, 2000, 4000, 400000, 384400000],  # sea level to lunar orbit
        'atmospheric_seeing_arcsec': [0.0, 0.5, 1.0, 2.0, 5.0],  # 0 = space
    },
    'performance_metrics': {
        'lightsail_acceleration_m_s2': [100, 500, 1000, 5000, 10000],
        'final_velocity_fraction_c': [0.10, 0.20, 0.30, 0.40, 0.50],
        'energy_efficiency': [0.30, 0.50, 0.70, 0.85, 0.95],
        'reliability_uptime': [0.90, 0.95, 0.98, 0.99, 0.999],
    }
}

# ============================================================================
# QUANTUM CIRCUIT DESIGN
# ============================================================================

def create_laser_optimization_circuit(n_qubits=24):
    """
    Create quantum circuit encoding laser system design space

    Qubit allocation (24 qubits):
    - Qubits 0-3:   Phased array configuration (element count, geometry, spacing)
    - Qubits 4-7:   Laser technology (type, wavelength, pulse mode, efficiency)
    - Qubits 8-11:  Power configuration (per-element, total, intensity, duration)
    - Qubits 12-14: Beam quality (M², divergence, coherence)
    - Qubits 15-17: Thermal management (cooling, dissipation, stability)
    - Qubits 18-20: Materials selection (crystal, optics, coatings)
    - Qubits 21-22: Cost optimization (capital, operating)
    - Qubit 23:     Location (ground/space)
    """

    qc = QuantumCircuit(n_qubits, n_qubits)

    # Initialize superposition - explore entire design space
    for i in range(n_qubits):
        qc.h(i)

    # =========================
    # PHASED ARRAY CONFIGURATION (qubits 0-3)
    # =========================
    # Element count encoding
    qc.ry(np.pi/3, 0)  # Bias toward mid-range element counts
    qc.ry(np.pi/4, 1)
    qc.cx(0, 1)

    # Geometry type
    qc.ry(np.pi/5, 2)
    qc.cx(0, 2)
    qc.cx(1, 2)

    # Spacing optimization
    qc.ry(np.pi/6, 3)
    qc.cx(2, 3)

    # =========================
    # LASER TECHNOLOGY (qubits 4-7)
    # =========================
    # Laser type
    qc.ry(np.pi/4, 4)  # Nd:YAG baseline
    qc.ry(np.pi/5, 5)
    qc.cx(4, 5)

    # Wavelength optimization
    qc.ry(np.pi/8, 6)  # Bias toward 1064nm
    qc.cx(4, 6)
    qc.cx(5, 6)

    # Efficiency encoding
    qc.ry(np.pi/3, 7)
    qc.cx(6, 7)

    # =========================
    # POWER CONFIGURATION (qubits 8-11)
    # =========================
    # Power per element
    qc.ry(np.pi/4, 8)
    qc.cx(0, 8)  # Couple to element count
    qc.cx(4, 8)  # Couple to laser type

    # Total system power
    qc.ry(np.pi/3, 9)
    qc.cx(8, 9)
    qc.cx(1, 9)

    # Peak intensity at lightsail
    qc.ry(np.pi/5, 10)
    qc.cx(9, 10)
    qc.cx(3, 10)  # Couple to spacing

    # Acceleration duration
    qc.ry(np.pi/6, 11)
    qc.cx(10, 11)

    # =========================
    # BEAM QUALITY (qubits 12-14)
    # =========================
    # M² factor (beam quality)
    qc.ry(np.pi/8, 12)  # Bias toward perfect Gaussian (M²=1.0)
    qc.cx(4, 12)  # Couple to laser type

    # Beam divergence
    qc.ry(np.pi/10, 13)
    qc.cx(12, 13)
    qc.cx(2, 13)  # Couple to geometry

    # Coherence length
    qc.ry(np.pi/7, 14)
    qc.cx(6, 14)  # Couple to wavelength
    qc.cx(13, 14)

    # =========================
    # THERMAL MANAGEMENT (qubits 15-17)
    # =========================
    # Cooling system type
    qc.ry(np.pi/4, 15)
    qc.cx(9, 15)  # Couple to total power

    # Heat dissipation
    qc.ry(np.pi/3, 16)
    qc.cx(9, 16)  # Directly coupled to power
    qc.cx(15, 16)

    # Thermal stability
    qc.ry(np.pi/6, 17)
    qc.cx(16, 17)
    qc.cx(12, 17)  # Couple to beam quality

    # =========================
    # MATERIALS SELECTION (qubits 18-20)
    # =========================
    # Laser crystal
    qc.ry(np.pi/8, 18)
    qc.cx(4, 18)  # Couple to laser type
    qc.cx(6, 18)  # Couple to wavelength

    # Optics substrate
    qc.ry(np.pi/7, 19)
    qc.cx(17, 19)  # Couple to thermal stability

    # Coating type
    qc.ry(np.pi/6, 20)
    qc.cx(6, 20)  # Couple to wavelength
    qc.cx(19, 20)

    # =========================
    # COST OPTIMIZATION (qubits 21-22)
    # =========================
    # Capital cost
    qc.ry(np.pi/4, 21)
    qc.cx(0, 21)  # Element count
    qc.cx(8, 21)  # Power per element
    qc.cx(18, 21)  # Materials

    # Operating cost
    qc.ry(np.pi/5, 22)
    qc.cx(9, 22)  # Total power
    qc.cx(15, 22)  # Cooling system
    qc.cx(21, 22)

    # =========================
    # LOCATION (qubit 23)
    # =========================
    # Ground vs space-based
    qc.ry(np.pi/6, 23)
    qc.cx(13, 23)  # Couple to beam divergence (atmospheric effects)
    qc.cx(21, 23)  # Couple to cost

    # =========================
    # ENTANGLEMENT LAYERS - System-level optimization
    # =========================
    # Cross-subsystem entanglement for holistic optimization
    qc.cx(9, 16)   # Power → Heat dissipation
    qc.cx(12, 13)  # Beam quality → Divergence
    qc.cx(0, 21)   # Array size → Cost
    qc.cx(7, 22)   # Efficiency → Operating cost
    qc.cx(23, 13)  # Location → Divergence

    # Additional barrier to mark optimization boundary
    qc.barrier()

    # Final rotation layer for fine-tuning
    for i in [0, 4, 8, 12, 15, 18, 21, 23]:
        qc.ry(np.pi/16, i)

    # Measurement
    qc.measure(range(n_qubits), range(n_qubits))

    return qc

# ============================================================================
# CONFIGURATION DECODER
# ============================================================================

def decode_laser_configuration(bitstring):
    """
    Decode 24-qubit bitstring into laser system configuration

    Bit allocation:
    - array_bits (0:4) = 4 bits
    - tech_bits (4:8) = 4 bits
    - power_bits (8:12) = 4 bits
    - beam_bits (12:15) = 3 bits
    - thermal_bits (15:18) = 3 bits
    - material_bits (18:21) = 3 bits
    - cost_bits (21:23) = 2 bits
    - location_bit (23) = 1 bit
    """

    # Extract qubit groups
    array_bits = bitstring[0:4]      # 4 bits
    tech_bits = bitstring[4:8]       # 4 bits
    power_bits = bitstring[8:12]     # 4 bits
    beam_bits = bitstring[12:15]     # 3 bits
    thermal_bits = bitstring[15:18]  # 3 bits
    material_bits = bitstring[18:21] # 3 bits
    cost_bits = bitstring[21:23]     # 2 bits
    location_bit = bitstring[23]     # 1 bit

    # Decode each subsystem
    config = {}

    # Phased array (4 bits)
    element_count_idx = int(array_bits[0:2], 2) % len(LASER_DESIGN_PARAMETERS['phased_array']['element_count_range'])
    geometry_idx = int(array_bits[2:4], 2) % len(LASER_DESIGN_PARAMETERS['phased_array']['geometry_types'])

    config['phased_array'] = {
        'element_count': LASER_DESIGN_PARAMETERS['phased_array']['element_count_range'][element_count_idx],
        'geometry': LASER_DESIGN_PARAMETERS['phased_array']['geometry_types'][geometry_idx],
        'spacing_m': LASER_DESIGN_PARAMETERS['phased_array']['element_spacing_m'][int(array_bits[2], 2) % len(LASER_DESIGN_PARAMETERS['phased_array']['element_spacing_m'])],
        'aperture_m': LASER_DESIGN_PARAMETERS['phased_array']['total_aperture_m'][int(array_bits[0:3], 2) % len(LASER_DESIGN_PARAMETERS['phased_array']['total_aperture_m'])]
    }

    # Laser technology (4 bits)
    tech_idx = int(tech_bits[0:2], 2) % len(LASER_DESIGN_PARAMETERS['laser_technology']['type'])
    wavelength_idx = int(tech_bits[2:4], 2) % len(LASER_DESIGN_PARAMETERS['laser_technology']['wavelength_nm'])

    config['laser_technology'] = {
        'type': LASER_DESIGN_PARAMETERS['laser_technology']['type'][tech_idx],
        'wavelength_nm': LASER_DESIGN_PARAMETERS['laser_technology']['wavelength_nm'][wavelength_idx],
        'pulse_mode': LASER_DESIGN_PARAMETERS['laser_technology']['pulse_mode'][int(tech_bits[0:2], 2) % len(LASER_DESIGN_PARAMETERS['laser_technology']['pulse_mode'])],
        'efficiency': LASER_DESIGN_PARAMETERS['laser_technology']['wall_plug_efficiency'][int(tech_bits[2:4], 2) % len(LASER_DESIGN_PARAMETERS['laser_technology']['wall_plug_efficiency'])]
    }

    # Power configuration (4 bits)
    power_per_element_idx = int(power_bits[0:2], 2) % len(LASER_DESIGN_PARAMETERS['power_configuration']['power_per_element_kW'])
    total_power_idx = int(power_bits[2:4], 2) % len(LASER_DESIGN_PARAMETERS['power_configuration']['total_system_power_GW'])

    config['power'] = {
        'per_element_kW': LASER_DESIGN_PARAMETERS['power_configuration']['power_per_element_kW'][power_per_element_idx],
        'total_system_GW': LASER_DESIGN_PARAMETERS['power_configuration']['total_system_power_GW'][total_power_idx],
        'peak_intensity_GW_m2': LASER_DESIGN_PARAMETERS['power_configuration']['peak_intensity_GW_m2'][int(power_bits[0:3], 2) % len(LASER_DESIGN_PARAMETERS['power_configuration']['peak_intensity_GW_m2'])],
        'duration_min': LASER_DESIGN_PARAMETERS['power_configuration']['acceleration_duration_min'][int(power_bits[1:4], 2) % len(LASER_DESIGN_PARAMETERS['power_configuration']['acceleration_duration_min'])]
    }

    # Beam quality (3 bits)
    config['beam_quality'] = {
        'M2_factor': LASER_DESIGN_PARAMETERS['beam_quality']['M2_factor'][int(beam_bits[0:2], 2) % len(LASER_DESIGN_PARAMETERS['beam_quality']['M2_factor'])],
        'divergence_urad': LASER_DESIGN_PARAMETERS['beam_quality']['beam_divergence_urad'][int(beam_bits[0:3], 2) % len(LASER_DESIGN_PARAMETERS['beam_quality']['beam_divergence_urad'])],
        'coherence_length_m': LASER_DESIGN_PARAMETERS['beam_quality']['coherence_length_m'][int(beam_bits[1:3], 2) % len(LASER_DESIGN_PARAMETERS['beam_quality']['coherence_length_m'])],
        'atmospheric_transmission': LASER_DESIGN_PARAMETERS['beam_quality']['atmospheric_transmission'][int(beam_bits[0:3], 2) % len(LASER_DESIGN_PARAMETERS['beam_quality']['atmospheric_transmission'])]
    }

    # Thermal management (3 bits)
    cooling_idx = int(thermal_bits[0:2], 2) % len(LASER_DESIGN_PARAMETERS['thermal_management']['cooling_system'])

    config['thermal'] = {
        'cooling_system': LASER_DESIGN_PARAMETERS['thermal_management']['cooling_system'][cooling_idx],
        'heat_dissipation_MW': LASER_DESIGN_PARAMETERS['thermal_management']['heat_dissipation_MW'][int(thermal_bits[0:3], 2) % len(LASER_DESIGN_PARAMETERS['thermal_management']['heat_dissipation_MW'])],
        'operating_temp_K': LASER_DESIGN_PARAMETERS['thermal_management']['operating_temp_K'][int(thermal_bits[1:3], 2) % len(LASER_DESIGN_PARAMETERS['thermal_management']['operating_temp_K'])],
        'thermal_stability_mK': LASER_DESIGN_PARAMETERS['thermal_management']['thermal_stability_mK'][int(thermal_bits[0:2], 2) % len(LASER_DESIGN_PARAMETERS['thermal_management']['thermal_stability_mK'])]
    }

    # Materials (3 bits)
    crystal_idx = int(material_bits[0:2], 2) % len(LASER_DESIGN_PARAMETERS['materials']['laser_crystal'])
    optics_idx = int(material_bits[1:3], 2) % len(LASER_DESIGN_PARAMETERS['materials']['optics_substrate'])

    config['materials'] = {
        'laser_crystal': LASER_DESIGN_PARAMETERS['materials']['laser_crystal'][crystal_idx],
        'optics_substrate': LASER_DESIGN_PARAMETERS['materials']['optics_substrate'][optics_idx],
        'coating': LASER_DESIGN_PARAMETERS['materials']['coating_type'][int(material_bits[0:2], 2) % len(LASER_DESIGN_PARAMETERS['materials']['coating_type'])],
        'CAS_numbers': LASER_DESIGN_PARAMETERS['materials']['CAS_numbers']
    }

    # Cost (2 bits)
    config['cost'] = {
        'per_element_USD': LASER_DESIGN_PARAMETERS['cost_analysis']['cost_per_element_USD'][int(cost_bits[0:2], 2) % len(LASER_DESIGN_PARAMETERS['cost_analysis']['cost_per_element_USD'])],
        'total_system_M_USD': LASER_DESIGN_PARAMETERS['cost_analysis']['total_system_cost_M_USD'][int(cost_bits, 2) % len(LASER_DESIGN_PARAMETERS['cost_analysis']['total_system_cost_M_USD'])],
        'operating_per_shot_USD': LASER_DESIGN_PARAMETERS['cost_analysis']['operating_cost_per_shot_USD'][int(cost_bits[0:2], 2) % len(LASER_DESIGN_PARAMETERS['cost_analysis']['operating_cost_per_shot_USD'])],
        'maintenance_annual_M_USD': LASER_DESIGN_PARAMETERS['cost_analysis']['maintenance_cost_annual_M_USD'][int(cost_bits, 2) % len(LASER_DESIGN_PARAMETERS['cost_analysis']['maintenance_cost_annual_M_USD'])]
    }

    # Location (1 bit)
    location_idx = int(location_bit) % len(LASER_DESIGN_PARAMETERS['location']['site_type'])
    config['location'] = {
        'site_type': LASER_DESIGN_PARAMETERS['location']['site_type'][location_idx],
        'altitude_m': LASER_DESIGN_PARAMETERS['location']['altitude_m'][location_idx],
        'seeing_arcsec': LASER_DESIGN_PARAMETERS['location']['atmospheric_seeing_arcsec'][location_idx]
    }

    return config

# ============================================================================
# QUALITY SCORING
# ============================================================================

def calculate_quality_score(config):
    """
    Calculate quality score for laser configuration based on mission requirements

    Scoring criteria:
    - Power efficiency (20%)
    - Beam quality (20%)
    - Cost effectiveness (20%)
    - Thermal stability (15%)
    - Manufacturing feasibility (15%)
    - System reliability (10%)
    """

    score = 0.0
    details = {}

    # Power efficiency (0-20 points)
    efficiency = config['laser_technology']['efficiency']
    power_score = (efficiency / 0.50) * 20  # Normalize to max 50% efficiency
    score += power_score
    details['power_efficiency'] = power_score

    # Beam quality (0-20 points)
    M2 = config['beam_quality']['M2_factor']
    divergence = config['beam_quality']['divergence_urad']
    beam_score = (2.0 / M2) * 10  # Perfect Gaussian = 10 points
    beam_score += (10.0 / divergence) * 10  # Lower divergence = better
    beam_score = min(beam_score, 20)
    score += beam_score
    details['beam_quality'] = beam_score

    # Cost effectiveness (0-20 points)
    # Favor configurations with reasonable cost (not too cheap = unrealistic, not too expensive)
    total_cost = config['cost']['total_system_M_USD']
    if total_cost >= 500 and total_cost <= 5000:
        cost_score = 20
    elif total_cost < 500:
        cost_score = (total_cost / 500) * 15  # Penalize unrealistically cheap
    else:
        cost_score = (10000 / total_cost) * 15  # Penalize too expensive
    score += cost_score
    details['cost_effectiveness'] = cost_score

    # Thermal stability (0-15 points)
    thermal_stability_mK = config['thermal']['thermal_stability_mK']
    thermal_score = (100 / (thermal_stability_mK + 1)) * 15
    thermal_score = min(thermal_score, 15)
    score += thermal_score
    details['thermal_stability'] = thermal_score

    # Manufacturing feasibility (0-15 points)
    # Favor proven technologies and reasonable element counts
    element_count = config['phased_array']['element_count']
    if element_count >= 1000 and element_count <= 5000:
        manuf_score = 15  # Sweet spot
    elif element_count < 1000:
        manuf_score = (element_count / 1000) * 12
    else:
        manuf_score = (10000 / element_count) * 12

    # Bonus for Nd:YAG (proven technology)
    if 'Nd_YAG' in config['laser_technology']['type']:
        manuf_score += 3

    score += manuf_score
    details['manufacturing_feasibility'] = manuf_score

    # System reliability (0-10 points)
    # Ground-based = more reliable, proven cooling systems
    if config['location']['site_type'] == 'ground_based_desert':
        reliability_score = 8
    elif config['location']['site_type'] == 'high_altitude_mountain':
        reliability_score = 7
    elif config['location']['site_type'] == 'space_based_LEO':
        reliability_score = 5
    else:
        reliability_score = 3

    # Bonus for liquid nitrogen cooling (proven, reliable)
    if config['thermal']['cooling_system'] == 'liquid_nitrogen':
        reliability_score += 2

    score += min(reliability_score, 10)
    details['system_reliability'] = min(reliability_score, 10)

    return score, details

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 80)
    print("QUANTUM LASER SYSTEM OPTIMIZER - IBM TORINO")
    print("=" * 80)
    print(f"\nQuantum Backend: IBM Torino (133 qubits)")
    print(f"Circuit Depth: 24 qubits")
    print(f"Shots: {N_SHOTS}")
    print(f"Target Execution Time: < 5 minutes")
    print("\nObjective: Design phased array laser propulsion system for 0.50c lightsail\n")

    # Connect to IBM Quantum
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService(channel='ibm_cloud', token=IBM_API_KEY)
    backend = service.backend('ibm_torino')

    print(f"✓ Connected to: {backend.name}")
    print(f"  Qubits: {backend.num_qubits}")
    print(f"  Quantum Volume: {backend.quantum_volume if hasattr(backend, 'quantum_volume') else 'N/A'}")

    # Create quantum circuit
    print("\nCreating quantum circuit for laser optimization...")
    qc = create_laser_optimization_circuit(N_QUBITS)

    print(f"✓ Circuit created")
    print(f"  Depth: {qc.depth()}")
    print(f"  Gates: {qc.size()}")
    print(f"  Qubits: {qc.num_qubits}")

    # Transpile for IBM Torino
    print("\nTranspiling for IBM Torino architecture...")
    transpiled_qc = transpile(qc, backend=backend, optimization_level=3)

    print(f"✓ Transpiled")
    print(f"  Optimized depth: {transpiled_qc.depth()}")
    print(f"  Optimized gates: {transpiled_qc.size()}")

    # Execute on IBM Torino
    print(f"\n🚀 Submitting job to IBM Torino ({N_SHOTS} shots)...")
    print("This will take approximately 3-5 minutes...\n")

    start_time = datetime.now()

    sampler = Sampler(mode=backend)
    job = sampler.run([transpiled_qc], shots=N_SHOTS)

    print(f"Job ID: {job.job_id()}")
    print(f"Status: {job.status()}")

    # Wait for completion
    result = job.result()

    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds()

    print(f"\n✓ Quantum execution completed in {execution_time:.2f} seconds")

    # Parse results
    print("\nParsing quantum measurement results...")
    pub_result = result[0]
    data_bin = pub_result.data

    if hasattr(data_bin, 'c'):
        bit_array = data_bin.c
    elif hasattr(data_bin, 'meas'):
        bit_array = data_bin.meas
    else:
        raise AttributeError("Cannot find measurement data in result")

    counts_dict = bit_array.get_counts()
    counts = {bitstring: counts_dict[bitstring] for bitstring in counts_dict}

    print(f"✓ Measured {len(counts)} unique laser configurations")

    # Decode and score configurations
    print("\nDecoding and scoring configurations...")
    configurations = []

    for bitstring, count in counts.items():
        config = decode_laser_configuration(bitstring)
        quality_score, score_details = calculate_quality_score(config)

        configurations.append({
            'bitstring': bitstring,
            'count': count,
            'probability': count / N_SHOTS,
            'quality_score': quality_score,
            'score_details': score_details,
            'configuration': config
        })

    # Sort by quality score
    configurations.sort(key=lambda x: x['quality_score'], reverse=True)

    print(f"✓ Ranked {len(configurations)} configurations by quality score")

    # Display TOP 10
    print("\n" + "=" * 80)
    print("TOP 10 LASER SYSTEM CONFIGURATIONS")
    print("=" * 80)

    for i, cfg in enumerate(configurations[:10], 1):
        print(f"\n{'='*80}")
        print(f"RANK #{i} - Quality Score: {cfg['quality_score']:.2f}/100")
        print(f"{'='*80}")
        print(f"Probability: {cfg['probability']*100:.3f}% ({cfg['count']} shots)")
        print(f"Bitstring: {cfg['bitstring']}")

        config = cfg['configuration']

        print("\n📡 PHASED ARRAY:")
        print(f"  Elements: {config['phased_array']['element_count']:,}")
        print(f"  Geometry: {config['phased_array']['geometry']}")
        print(f"  Spacing: {config['phased_array']['spacing_m']} m")
        print(f"  Total Aperture: {config['phased_array']['aperture_m']} m")

        print("\n🔬 LASER TECHNOLOGY:")
        print(f"  Type: {config['laser_technology']['type']}")
        print(f"  Wavelength: {config['laser_technology']['wavelength_nm']} nm")
        print(f"  Pulse Mode: {config['laser_technology']['pulse_mode']}")
        print(f"  Wall-Plug Efficiency: {config['laser_technology']['efficiency']*100:.1f}%")

        print("\n⚡ POWER CONFIGURATION:")
        print(f"  Per Element: {config['power']['per_element_kW']} kW")
        print(f"  Total System: {config['power']['total_system_GW']} GW")
        print(f"  Peak Intensity: {config['power']['peak_intensity_GW_m2']} GW/m²")
        print(f"  Acceleration Duration: {config['power']['duration_min']} minutes")

        print("\n✨ BEAM QUALITY:")
        print(f"  M² Factor: {config['beam_quality']['M2_factor']}")
        print(f"  Divergence: {config['beam_quality']['divergence_urad']} µrad")
        print(f"  Coherence Length: {config['beam_quality']['coherence_length_m']:,} m")
        print(f"  Atmospheric Transmission: {config['beam_quality']['atmospheric_transmission']*100:.1f}%")

        print("\n🌡️  THERMAL MANAGEMENT:")
        print(f"  Cooling: {config['thermal']['cooling_system']}")
        print(f"  Heat Dissipation: {config['thermal']['heat_dissipation_MW']} MW")
        print(f"  Operating Temp: {config['thermal']['operating_temp_K']} K")
        print(f"  Thermal Stability: ±{config['thermal']['thermal_stability_mK']} mK")

        print("\n🧪 MATERIALS:")
        print(f"  Laser Crystal: {config['materials']['laser_crystal']}")
        print(f"  Optics Substrate: {config['materials']['optics_substrate']}")
        print(f"  Coating: {config['materials']['coating']}")

        print("\n💰 COST ANALYSIS:")
        print(f"  Per Element: ${config['cost']['per_element_USD']:,}")
        print(f"  Total System: ${config['cost']['total_system_M_USD']:,}M")
        print(f"  Operating Cost/Shot: ${config['cost']['operating_per_shot_USD']:,}")
        print(f"  Annual Maintenance: ${config['cost']['maintenance_annual_M_USD']}M")

        print("\n🌍 LOCATION:")
        print(f"  Site Type: {config['location']['site_type']}")
        print(f"  Altitude: {config['location']['altitude_m']:,} m")
        print(f"  Seeing: {config['location']['seeing_arcsec']} arcsec")

        print("\n📊 SCORE BREAKDOWN:")
        for criterion, score in cfg['score_details'].items():
            print(f"  {criterion}: {score:.2f}")

    # Save results
    output_dir = Path('/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/results/quantum')
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'laser_system_optimization_{timestamp}.json'

    output_data = {
        'metadata': {
            'timestamp': timestamp,
            'backend': backend.name,
            'n_qubits': N_QUBITS,
            'n_shots': N_SHOTS,
            'execution_time_seconds': execution_time,
            'job_id': job.job_id(),
            'unique_configurations': len(configurations),
        },
        'top_10_configurations': configurations[:10],
        'all_configurations': configurations,
        'quantum_circuit_info': {
            'depth': qc.depth(),
            'gates': qc.size(),
            'transpiled_depth': transpiled_qc.depth(),
            'transpiled_gates': transpiled_qc.size(),
        }
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n💾 Results saved to: {output_file}")
    print(f"   File size: {output_file.stat().st_size / (1024*1024):.2f} MB")

    print("\n" + "=" * 80)
    print("QUANTUM OPTIMIZATION COMPLETE")
    print("=" * 80)
    print(f"\n✅ Generated {len(configurations)} unique laser configurations")
    print(f"✅ Execution time: {execution_time:.2f} seconds")
    print(f"✅ TOP configuration quality score: {configurations[0]['quality_score']:.2f}/100")
    print(f"✅ Results ready for engineering documentation\n")

if __name__ == '__main__':
    main()
