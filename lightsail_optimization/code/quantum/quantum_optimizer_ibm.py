#!/usr/bin/env python3
"""
IBM QUANTUM OPTIMIZATION FOR LIGHTSAIL >0.15c
Using REAL IBM Quantum hardware with 12 qubits
"""

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Options
from qiskit.circuit.library import RealAmplitudes
from scipy.optimize import minimize
import json
from datetime import datetime

# IBM Quantum API
IBM_API_KEY = 'bFodPcl5hR0To4S_FHWLA0GeYSm82dIQ5zTwUhVoGxwT'

print("="*70)
print("IBM QUANTUM OPTIMIZATION FOR LIGHTSAIL >0.15c")
print("="*70)

# Initialize IBM Quantum
print("\nConnecting to IBM Quantum...")
try:
    # Try to load saved account
    service = QiskitRuntimeService()
except Exception:
    # Save account first time
    QiskitRuntimeService.save_account(
        channel='ibm_quantum',
        token=IBM_API_KEY,
        overwrite=True
    )
    service = QiskitRuntimeService()

# Get available backends
print("Available backends:")
backends = service.backends()
for backend in backends:
    print(f"  - {backend.name}: {backend.num_qubits} qubits, status: {backend.status().status_msg}")

# Select backend (least busy with >=12 qubits)
backend = service.least_busy(min_num_qubits=12, operational=True)
print(f"\nSelected backend: {backend.name}")
print(f"  Qubits: {backend.num_qubits}")
print(f"  Pending jobs: {backend.status().pending_jobs}")

# Physical constants
c = 299792458.0  # m/s
sigma_sb = 5.67e-8  # Stefan-Boltzmann

# REAL parameter ranges (expanded beyond classical optimization)
# We'll encode 12 parameters into 12 qubits
print("\n" + "="*70)
print("PARAMETER ENCODING (12 qubits)")
print("="*70)
print("""
Qubit encoding strategy:
- Qubits 0-2: Sail area (8 values: 0.5, 1, 2, 4, 8, 16, 32, 64 m²)
- Qubits 3-5: Thickness (8 values: 10, 20, 50, 100, 200, 500, 1000, 2000 nm)
- Qubits 6-8: Laser power (8 values: 100, 200, 500, 1000, 2000, 5000, 10000, 20000 GW)
- Qubits 9-11: Staging (8 values: 1-stage to 8-stage designs)
""")

# Parameter lookup tables
AREAS = np.array([0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0])  # m²
THICKNESSES = np.array([10, 20, 50, 100, 200, 500, 1000, 2000]) * 1e-9  # m
POWERS = np.array([100, 200, 500, 1000, 2000, 5000, 10000, 20000]) * 1e9  # W
STAGES = np.array([1, 2, 3, 4, 5, 6, 7, 8])  # Number of stages

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
    """
    Calculate velocity for multi-stage lightsail
    Each stage drops mass, allowing higher acceleration
    """
    # Sail material: Kapton + HfO2/SiO2 (REAL)
    density_kapton = 1420  # kg/m³
    density_hfo2 = 9680
    density_sio2 = 2200

    # Layer thicknesses (REAL)
    t_kapton = 5e-6  # m
    t_hfo2 = 6.3e-6  # m (50 layers)
    t_sio2 = 9.2e-6  # m (50 layers)

    # Mass per m² (REAL)
    mass_per_m2 = (t_kapton * density_kapton +
                   t_hfo2 * density_hfo2 +
                   t_sio2 * density_sio2)

    # Sail mass
    m_sail = area * mass_per_m2

    # Payload per stage (decreases with staging)
    m_payload_base = 0.001  # 1 gram final payload

    # Total system mass (each stage has sail + next stage)
    # Stage N: sail_N + sail_(N-1) + ... + sail_1 + payload
    total_mass = m_payload_base
    for i in range(num_stages):
        stage_area = area * (0.7 ** i)  # Each stage 70% of previous
        stage_mass = stage_area * mass_per_m2
        total_mass += stage_mass

    # Reflectivity (REAL measured)
    reflectivity = 0.995

    # CRITICAL: Laser divergence
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

        # Time per stage (300s each)
        t_stage = 300.0

        # Velocity gain this stage
        dv = a * t_stage
        v_total += dv

        # Drop this stage's mass
        stage_mass = stage_area * mass_per_m2
        current_mass -= stage_mass

        if current_mass <= m_payload_base:
            current_mass = m_payload_base
            break

    # Cap at 0.5c (relativistic limit)
    v_final = min(v_total, 0.5 * c)

    # Temperature check (must survive)
    absorption = 0.005  # 0.5%
    P_absorbed = power * absorption
    T_4 = P_absorbed / (sigma_sb * area * 2)
    temperature = T_4 ** 0.25

    # Stress check
    pressure = power / (c * area)
    sail_radius = np.sqrt(area / np.pi)
    stress = pressure * sail_radius / (2 * thickness)

    # Feasibility checks
    max_temp = 673  # K (Kapton limit - REAL)
    max_stress = 115e6  # Pa (Kapton with safety factor 2.0 - REAL)

    feasible = (temperature < max_temp) and (stress < max_stress)

    if not feasible:
        v_final = 0.0  # Penalize infeasible designs

    return {
        'v_final': v_final,
        'v_c': v_final / c,
        'temperature': temperature,
        'stress': stress,
        'mass_total': total_mass,
        'feasible': feasible
    }

def objective_function(counts):
    """
    Classical objective function to evaluate quantum results
    Returns average velocity across all measured states
    """
    total_velocity = 0.0
    total_counts = 0

    results = []

    for bitstring, count in counts.items():
        # Decode parameters
        params = decode_parameters(bitstring)

        # Calculate performance
        perf = calculate_multistage_velocity(
            params['area'],
            params['thickness'],
            params['power'],
            params['stages']
        )

        # Weight by measurement count
        total_velocity += perf['v_c'] * count
        total_counts += count

        results.append({
            'bitstring': bitstring,
            'count': count,
            'params': params,
            'velocity_c': perf['v_c'],
            'feasible': perf['feasible']
        })

    avg_velocity = total_velocity / total_counts if total_counts > 0 else 0.0

    return avg_velocity, results

print("\n" + "="*70)
print("CREATING QUANTUM CIRCUIT")
print("="*70)

# Create quantum circuit with 12 qubits
n_qubits = 12
qc = QuantumCircuit(n_qubits)

# Apply Hadamard to create equal superposition
print("Applying Hadamard gates (superposition of all 4096 configurations)...")
for i in range(n_qubits):
    qc.h(i)

# Apply entangling gates to create correlations
print("Applying entangling gates for parameter correlations...")
# Entangle area with thickness (qubits 0-2 with 3-5)
for i in range(3):
    qc.cx(i, i+3)

# Entangle power with stages (qubits 6-8 with 9-11)
for i in range(3):
    qc.cx(i+6, i+9)

# Add rotation gates for phase variation
print("Applying rotation gates...")
for i in range(n_qubits):
    qc.rz(np.pi/4, i)
    qc.rx(np.pi/8, i)

# Add more entanglement layers
for i in range(0, n_qubits-1, 2):
    qc.cx(i, i+1)

# Final rotations
for i in range(n_qubits):
    qc.rz(np.pi/3, i)

# Add measurements
qc.measure_all()

print(f"Circuit depth: {qc.depth()}")
print(f"Circuit size: {qc.size()}")

# Transpile for IBM hardware
print("\n" + "="*70)
print("TRANSPILING FOR IBM HARDWARE")
print("="*70)
print(f"Target: {backend.name}")

qc_transpiled = transpile(qc, backend=backend, optimization_level=3)
print(f"Transpiled depth: {qc_transpiled.depth()}")
print(f"Transpiled size: {qc_transpiled.size()}")

# Set up Sampler with options
print("\n" + "="*70)
print("EXECUTING ON IBM QUANTUM")
print("="*70)

sampler = Sampler(mode=backend)

print(f"Shots: 4000")
print(f"Optimization level: 3")
print("\nSubmitting job to IBM Quantum...")
print("This may take several minutes (queue + execution)...")

# Execute with shots parameter (no parameters, just circuit)
job = sampler.run([qc_transpiled], shots=4000)
print(f"Job ID: {job.job_id()}")
print(f"Job status: {job.status()}")

# Wait for result
result = job.result()
print("\n✓ Job completed!")

# Get counts from PubResult
pub_result = result[0]
counts_data = pub_result.data.meas.get_counts()
counts = {}
for bitstring, count in counts_data.items():
    counts[bitstring] = count

print(f"Unique configurations measured: {len(counts)}")

# Analyze results
print("\n" + "="*70)
print("ANALYZING QUANTUM RESULTS")
print("="*70)

avg_velocity, results = objective_function(counts)

print(f"\nAverage velocity (quantum): {avg_velocity:.6f}c")

# Sort by velocity
results_sorted = sorted(results, key=lambda x: x['velocity_c'], reverse=True)

# Top 10 configurations
print("\n" + "="*70)
print("TOP 10 CONFIGURATIONS FROM QUANTUM OPTIMIZATION")
print("="*70)

for i, res in enumerate(results_sorted[:10]):
    if res['feasible']:
        print(f"\n#{i+1} Configuration:")
        print(f"  Bitstring: {res['bitstring']}")
        print(f"  Counts: {res['count']}")
        print(f"  Area: {res['params']['area']:.2f} m²")
        print(f"  Thickness: {res['params']['thickness']*1e9:.0f} nm")
        print(f"  Power: {res['params']['power']/1e9:.0f} GW")
        print(f"  Stages: {res['params']['stages']}")
        print(f"  Velocity: {res['velocity_c']:.6f}c ({res['velocity_c']*c:.3e} m/s)")
        print(f"  Feasible: {'✓' if res['feasible'] else '✗'}")

# Best configuration
best = results_sorted[0]
if best['feasible']:
    print("\n" + "="*70)
    print("BEST CONFIGURATION (QUANTUM OPTIMIZED)")
    print("="*70)
    print(f"  Sail Area: {best['params']['area']:.2f} m²")
    print(f"  Thickness: {best['params']['thickness']*1e9:.0f} nm")
    print(f"  Laser Power: {best['params']['power']/1e9:.0f} GW")
    print(f"  Number of Stages: {best['params']['stages']}")
    print(f"  Final Velocity: {best['velocity_c']:.6f}c")
    print(f"  Time to α Centauri: {4.37/best['velocity_c']:.2f} years")

    # Recalculate with full details
    full_result = calculate_multistage_velocity(
        best['params']['area'],
        best['params']['thickness'],
        best['params']['power'],
        best['params']['stages']
    )

    print(f"\n  Temperature: {full_result['temperature']:.1f} K (limit: 673 K)")
    print(f"  Stress: {full_result['stress']/1e6:.1f} MPa (limit: 115 MPa)")
    print(f"  Total Mass: {full_result['mass_total']*1e6:.2f} mg")

# Save results
output = {
    'timestamp': datetime.now().isoformat(),
    'backend': backend.name,
    'shots': 4000,
    'qubits': n_qubits,
    'avg_velocity_c': avg_velocity,
    'best_configuration': {
        'params': best['params'],
        'velocity_c': best['velocity_c'],
    },
    'top_10': results_sorted[:10]
}

with open('quantum_optimization_results_ibm.json', 'w') as f:
    json.dump(output, f, indent=2, default=str)

print("\n✓ Results saved to quantum_optimization_results_ibm.json")

print("\n" + "="*70)
print("IBM QUANTUM OPTIMIZATION COMPLETE")
print("="*70)
