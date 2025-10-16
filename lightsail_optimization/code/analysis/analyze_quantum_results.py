#!/usr/bin/env python3
"""
ANALYZE IBM QUANTUM RESULTS
Job ID: d3nht31fk6qs73e8vkb0 (already completed)
"""

import numpy as np
from qiskit_ibm_runtime import QiskitRuntimeService
import json
from datetime import datetime

# IBM Quantum API
IBM_API_KEY = 'bFodPcl5hR0To4S_FHWLA0GeYSm82dIQ5zTwUhVoGxwT'

print("="*70)
print("ANALYZING IBM QUANTUM RESULTS - JOB d3nht31fk6qs73e8vkb0")
print("="*70)

# Initialize
service = QiskitRuntimeService()

# Retrieve completed job
job_id = 'd3nht31fk6qs73e8vkb0'
print(f"\nRetrieving job: {job_id}")
job = service.job(job_id)

print(f"Status: {job.status()}")
print(f"Backend: {job.backend().name}")

# Get result
result = job.result()
pub_result = result[0]
counts_data = pub_result.data.meas.get_counts()

counts = {}
for bitstring, count in counts_data.items():
    counts[bitstring] = count

print(f"Total shots: {sum(counts.values())}")
print(f"Unique configurations: {len(counts)}")

# Physical constants
c = 299792458.0  # m/s
sigma_sb = 5.67e-8

# Parameter lookup tables
AREAS = np.array([0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0])  # m²
THICKNESSES = np.array([10, 20, 50, 100, 200, 500, 1000, 2000]) * 1e-9  # m
POWERS = np.array([100, 200, 500, 1000, 2000, 5000, 10000, 20000]) * 1e9  # W
STAGES = np.array([1, 2, 3, 4, 5, 6, 7, 8])

def decode_parameters(bitstring):
    """Decode 12-bit string to physical parameters"""
    area_idx = int(bitstring[0:3], 2)
    thick_idx = int(bitstring[3:6], 2)
    power_idx = int(bitstring[6:9], 2)
    stage_idx = int(bitstring[9:12], 2)

    return {
        'area': AREAS[area_idx],
        'thickness': THICKNESSES[thick_idx],
        'power': POWERS[power_idx],
        'stages': STAGES[stage_idx]
    }

def calculate_multistage_velocity(area, thickness, power, num_stages):
    """Calculate velocity for multi-stage lightsail"""
    # Sail material: Kapton + HfO2/SiO2 (REAL)
    density_kapton = 1420  # kg/m³
    density_hfo2 = 9680
    density_sio2 = 2200

    # Layer thicknesses (REAL)
    t_kapton = 5e-6  # m
    t_hfo2 = 6.3e-6  # m
    t_sio2 = 9.2e-6  # m

    # Mass per m²
    mass_per_m2 = (t_kapton * density_kapton +
                   t_hfo2 * density_hfo2 +
                   t_sio2 * density_sio2)

    # Sail mass
    m_sail = area * mass_per_m2

    # Payload
    m_payload_base = 0.001  # 1 gram

    # Total system mass
    total_mass = m_payload_base
    for i in range(num_stages):
        stage_area = area * (0.7 ** i)
        stage_mass = stage_area * mass_per_m2
        total_mass += stage_mass

    # Reflectivity (REAL)
    reflectivity = 0.995

    # Laser divergence
    divergence_factor = 0.10

    # Velocity accumulation through stages
    v_total = 0.0
    current_mass = total_mass

    for stage in range(num_stages):
        # Force on current stage
        stage_area = area * (0.7 ** stage)
        F = 2.0 * power * reflectivity * divergence_factor / c

        # Acceleration
        a = F / current_mass

        # Time per stage
        t_stage = 300.0  # seconds

        # Velocity gain
        dv = a * t_stage
        v_total += dv

        # Drop mass
        stage_mass = stage_area * mass_per_m2
        current_mass -= stage_mass

        if current_mass <= m_payload_base:
            current_mass = m_payload_base
            break

    # Cap at 0.5c
    v_final = min(v_total, 0.5 * c)

    # Temperature check
    absorption = 0.005
    P_absorbed = power * absorption
    T_4 = P_absorbed / (sigma_sb * area * 2)
    temperature = T_4 ** 0.25

    # Stress check
    pressure = power / (c * area)
    sail_radius = np.sqrt(area / np.pi)
    stress = pressure * sail_radius / (2 * thickness)

    # Feasibility
    max_temp = 673  # K (Kapton)
    max_stress = 115e6  # Pa

    feasible = (temperature < max_temp) and (stress < max_stress)

    if not feasible:
        v_final = 0.0

    return {
        'v_final': v_final,
        'v_c': v_final / c,
        'temperature': temperature,
        'stress': stress,
        'mass_total': total_mass,
        'feasible': feasible
    }

# Analyze all results
print("\n" + "="*70)
print("ANALYZING ALL CONFIGURATIONS")
print("="*70)

results = []
for bitstring, count in counts.items():
    params = decode_parameters(bitstring)
    perf = calculate_multistage_velocity(
        params['area'],
        params['thickness'],
        params['power'],
        params['stages']
    )

    results.append({
        'bitstring': bitstring,
        'count': count,
        'params': params,
        'velocity_c': perf['v_c'],
        'temperature': perf['temperature'],
        'stress': perf['stress'],
        'feasible': perf['feasible']
    })

# Sort by velocity
results_sorted = sorted(results, key=lambda x: x['velocity_c'], reverse=True)

# Filter feasible only
feasible_results = [r for r in results_sorted if r['feasible']]

print(f"\nFeasible configurations: {len(feasible_results)}")

if len(feasible_results) > 0:
    print("\n" + "="*70)
    print("TOP 10 FEASIBLE CONFIGURATIONS (QUANTUM OPTIMIZED)")
    print("="*70)

    for i, res in enumerate(feasible_results[:10]):
        print(f"\n#{i+1}")
        print(f"  Bitstring: {res['bitstring']}")
        print(f"  Quantum counts: {res['count']} (out of {sum(counts.values())})")
        print(f"  Area: {res['params']['area']:.2f} m²")
        print(f"  Thickness: {res['params']['thickness']*1e9:.0f} nm")
        print(f"  Power: {res['params']['power']/1e9:.0f} GW")
        print(f"  Stages: {res['params']['stages']}")
        print(f"  VELOCITY: {res['velocity_c']:.6f}c ({res['velocity_c']*c:.3e} m/s)")
        print(f"  Temperature: {res['temperature']:.1f} K (limit: 673 K)")
        print(f"  Stress: {res['stress']/1e6:.1f} MPa (limit: 115 MPa)")
        print(f"  Time to α Cen: {4.37/res['velocity_c']:.2f} years" if res['velocity_c'] > 0 else "  N/A")

    # Best configuration
    best = feasible_results[0]
    print("\n" + "="*70)
    print("BEST CONFIGURATION (IBM QUANTUM OPTIMIZED)")
    print("="*70)
    print(f"  Sail Area: {best['params']['area']:.2f} m²")
    print(f"  Thickness: {best['params']['thickness']*1e9:.0f} nm")
    print(f"  Laser Power: {best['params']['power']/1e9:.0f} GW")
    print(f"  Number of Stages: {best['params']['stages']}")
    print(f"  FINAL VELOCITY: {best['velocity_c']:.6f}c")
    print(f"  TIME TO α CENTAURI: {4.37/best['velocity_c']:.2f} years")
    print(f"  Quantum measurement count: {best['count']}")

    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'job_id': job_id,
        'backend': job.backend().name,
        'shots': sum(counts.values()),
        'feasible_count': len(feasible_results),
        'best_velocity_c': best['velocity_c'],
        'best_config': {
            'area_m2': best['params']['area'],
            'thickness_nm': best['params']['thickness'] * 1e9,
            'power_GW': best['params']['power'] / 1e9,
            'stages': best['params']['stages'],
            'velocity_c': best['velocity_c'],
            'time_to_alpha_cen_years': 4.37 / best['velocity_c'] if best['velocity_c'] > 0 else None,
            'temperature_K': best['temperature'],
            'stress_MPa': best['stress'] / 1e6,
            'quantum_counts': best['count']
        },
        'top_10_feasible': feasible_results[:10]
    }

    with open('quantum_results_analyzed.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print("\n✓ Results saved to quantum_results_analyzed.json")

else:
    print("\n❌ NO FEASIBLE CONFIGURATIONS FOUND")
    print("All configurations violate either:")
    print("  - Temperature limit (673 K for Kapton)")
    print("  - Stress limit (115 MPa with safety factor)")

print("\n" + "="*70)
print("QUANTUM ANALYSIS COMPLETE")
print("="*70)
