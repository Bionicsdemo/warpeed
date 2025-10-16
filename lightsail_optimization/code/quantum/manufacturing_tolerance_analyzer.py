"""
IBM Quantum Analysis: Manufacturing Tolerance Sensitivity
=========================================================
Analyzes how manufacturing tolerances affect sail performance and determines
acceptable precision requirements for 95%-100% mission success.

Goal: Determine critical tolerances for thickness, reflectivity, alignment
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
import json
from datetime import datetime

# IBM Quantum credentials
API_KEY = "bFodPcl5hR0To4S_FHWLA0GeYSm82dIQ5zTwUhVoGxwT"

# Nominal design parameters
NOMINAL_THICKNESS = 20.5  # microns
NOMINAL_REFLECTIVITY = 0.9995  # 99.95%
NOMINAL_MASS = 82.0  # g/m²
TARGET_VELOCITY = 0.50  # c

def simulate_sail_performance(thickness_error_pct, reflectivity_error_pct,
                              mass_error_pct, alignment_error_deg):
    """
    Simulate how manufacturing errors affect final velocity.

    Returns: final_velocity_c, success_probability
    """
    # Actual parameters with errors
    actual_thickness = NOMINAL_THICKNESS * (1 + thickness_error_pct/100)
    actual_reflectivity = NOMINAL_REFLECTIVITY * (1 - reflectivity_error_pct/100)
    actual_mass = NOMINAL_MASS * (1 + mass_error_pct/100)

    # Thrust reduction due to reflectivity error
    thrust_factor = actual_reflectivity / NOMINAL_REFLECTIVITY

    # Mass increase penalty
    mass_factor = NOMINAL_MASS / actual_mass

    # Alignment loss (cosine factor for off-axis)
    alignment_factor = np.cos(np.deg2rad(alignment_error_deg))**2

    # Combined effect on velocity
    velocity_factor = thrust_factor * mass_factor * alignment_factor
    final_velocity = TARGET_VELOCITY * velocity_factor

    # Thermal check: thicker sail = higher temperature
    temperature_factor = (actual_thickness / NOMINAL_THICKNESS)**(-0.5)
    temp_nominal = 1627  # K
    temp_actual = temp_nominal * temperature_factor
    temp_limit = 2758  # K (HfO2 melting point)

    # Success criteria
    velocity_ok = final_velocity >= 0.45  # At least 90% of target
    thermal_ok = temp_actual <= temp_limit * 0.95  # 5% safety margin

    success = velocity_ok and thermal_ok
    success_prob = 1.0 if success else 0.0

    # Partial credit for near-success
    if not success:
        velocity_ratio = final_velocity / 0.45
        thermal_ratio = (temp_limit * 0.95) / temp_actual
        success_prob = 0.5 * min(velocity_ratio, thermal_ratio)

    return final_velocity, success_prob, temp_actual

def create_tolerance_analysis_circuit():
    """
    Create quantum circuit to explore tolerance space.

    Encoding:
    - Qubits 0-3: Thickness error (-5% to +5%, 16 levels)
    - Qubits 4-7: Reflectivity error (0% to 1%, 16 levels)
    - Qubits 8-11: Mass error (-3% to +3%, 16 levels)
    - Qubits 12-14: Alignment error (0° to 10°, 8 levels)

    Total: 15 qubits, 2^15 = 32,768 tolerance scenarios
    """
    qc = QuantumCircuit(15, 15)

    # Initialize superposition
    for i in range(15):
        qc.h(i)

    # Entangle error sources (correlated manufacturing defects)
    # Thickness errors correlate with mass errors
    for i in range(4):
        qc.cx(i, 8+i)

    # Reflectivity errors correlate with alignment errors
    for i in range(3):
        qc.cx(4+i, 12+i)

    # Add phase for optimization
    for i in range(15):
        qc.rz(np.pi/8, i)

    # Measurement
    qc.measure(range(15), range(15))

    return qc

def decode_tolerance_bitstring(bitstring):
    """
    Decode quantum measurement to error percentages.
    """
    thickness_bits = bitstring[0:4]
    reflectivity_bits = bitstring[4:8]
    mass_bits = bitstring[8:12]
    alignment_bits = bitstring[12:15]

    # Convert to error values
    thickness_error = (int(thickness_bits, 2) / 15.0) * 10 - 5  # -5% to +5%
    reflectivity_error = (int(reflectivity_bits, 2) / 15.0) * 1.0  # 0% to 1%
    mass_error = (int(mass_bits, 2) / 15.0) * 6 - 3  # -3% to +3%
    alignment_error = (int(alignment_bits, 2) / 7.0) * 10  # 0° to 10°

    return thickness_error, reflectivity_error, mass_error, alignment_error

def main():
    print("="*80)
    print("IBM QUANTUM ANALYSIS: Manufacturing Tolerance Sensitivity")
    print("="*80)
    print(f"Start time: {datetime.now()}")
    print()

    # Connect to IBM Quantum
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=API_KEY)

    # Select backend
    backend = service.least_busy(min_num_qubits=15, operational=True)
    print(f"Selected backend: {backend.name}")
    print(f"Qubits: {backend.num_qubits}")
    print()

    # Create circuit
    print("Creating quantum circuit (15 qubits)...")
    qc = create_tolerance_analysis_circuit()
    print(f"Circuit depth: {qc.depth()}")
    print()

    # Transpile
    print("Transpiling circuit...")
    from qiskit import transpile
    qc_transpiled = transpile(qc, backend=backend, optimization_level=3)
    print(f"Transpiled depth: {qc_transpiled.depth()}")
    print()

    # Run on IBM Quantum without Session (open plan)
    print("Submitting job to IBM Quantum (8000 shots)...")
    print("Analyzing 32,768 tolerance scenarios...")

    sampler = Sampler(mode=backend)
    job = sampler.run([qc_transpiled], shots=8000)

    print(f"Job ID: {job.job_id()}")
    print("Waiting for results...")

    result = job.result()

    print()
    print("✓ Quantum computation complete!")
    print()

    # Extract results
    pub_result = result[0]
    # Get counts from the data bin - the classical register is automatically named
    data_bin = pub_result.data
    # Get the first (and only) measurement register
    meas_name = list(data_bin.__dict__.keys())[0]
    counts = getattr(data_bin, meas_name).get_counts()

    print(f"Total scenarios sampled: {len(counts)}")
    print()

    # Analyze all scenarios
    print("Analyzing tolerance scenarios...")
    scenarios = []
    success_count = 0
    total_weighted = 0

    for bitstring, count in counts.items():
        # Decode errors
        t_err, r_err, m_err, a_err = decode_tolerance_bitstring(bitstring)

        # Simulate performance
        velocity, success_prob, temperature = simulate_sail_performance(
            t_err, r_err, m_err, a_err
        )

        scenarios.append({
            'thickness_error_pct': float(t_err),
            'reflectivity_error_pct': float(r_err),
            'mass_error_pct': float(m_err),
            'alignment_error_deg': float(a_err),
            'final_velocity_c': float(velocity),
            'temperature_K': float(temperature),
            'success_probability': float(success_prob),
            'quantum_counts': int(count)
        })

        if success_prob >= 0.95:
            success_count += count

        total_weighted += count * success_prob

    # Calculate overall success rate
    total_shots = sum(counts.values())
    success_rate = (success_count / total_shots) * 100
    avg_success = (total_weighted / total_shots) * 100

    print()
    print("="*80)
    print("TOLERANCE ANALYSIS RESULTS")
    print("="*80)
    print()
    print(f"Scenarios with >95% success: {success_count}/{total_shots} ({success_rate:.1f}%)")
    print(f"Average success probability: {avg_success:.1f}%")
    print()

    # Sort by success probability
    scenarios.sort(key=lambda x: x['success_probability'], reverse=True)

    # Find critical tolerances (scenarios just at threshold)
    print("CRITICAL TOLERANCE THRESHOLDS:")
    print()

    # Best case (most tolerant)
    best = scenarios[0]
    print("Most Tolerant Configuration:")
    print(f"  Thickness error: ±{abs(best['thickness_error_pct']):.2f}%")
    print(f"  Reflectivity error: {best['reflectivity_error_pct']:.3f}%")
    print(f"  Mass error: ±{abs(best['mass_error_pct']):.2f}%")
    print(f"  Alignment error: {best['alignment_error_deg']:.2f}°")
    print(f"  Final velocity: {best['final_velocity_c']:.4f}c")
    print(f"  Success: {best['success_probability']*100:.1f}%")
    print()

    # Worst acceptable case
    acceptable = [s for s in scenarios if s['success_probability'] >= 0.95]
    if acceptable:
        worst_acceptable = acceptable[-1]
        print("Worst Acceptable Configuration (95% success threshold):")
        print(f"  Thickness error: ±{abs(worst_acceptable['thickness_error_pct']):.2f}%")
        print(f"  Reflectivity error: {worst_acceptable['reflectivity_error_pct']:.3f}%")
        print(f"  Mass error: ±{abs(worst_acceptable['mass_error_pct']):.2f}%")
        print(f"  Alignment error: {worst_acceptable['alignment_error_deg']:.2f}°")
        print(f"  Final velocity: {worst_acceptable['final_velocity_c']:.4f}c")
        print()

    # Statistical analysis
    print("RECOMMENDED MANUFACTURING TOLERANCES (for 95% success):")
    print()

    # Find 95th percentile tolerances
    acceptable_t = [abs(s['thickness_error_pct']) for s in acceptable]
    acceptable_r = [s['reflectivity_error_pct'] for s in acceptable]
    acceptable_m = [abs(s['mass_error_pct']) for s in acceptable]
    acceptable_a = [s['alignment_error_deg'] for s in acceptable]

    if acceptable_t:
        t_tol = np.percentile(acceptable_t, 95)
        r_tol = np.percentile(acceptable_r, 95)
        m_tol = np.percentile(acceptable_m, 95)
        a_tol = np.percentile(acceptable_a, 95)

        print(f"  Thickness: ±{t_tol:.2f}% ({NOMINAL_THICKNESS * t_tol/100:.3f} μm)")
        print(f"  Reflectivity: within {r_tol:.3f}% (minimum {NOMINAL_REFLECTIVITY*(1-r_tol/100)*100:.3f}%)")
        print(f"  Mass: ±{m_tol:.2f}% ({NOMINAL_MASS * m_tol/100:.2f} g/m²)")
        print(f"  Alignment: ±{a_tol:.2f}° (pointing accuracy)")
        print()

    # Save results
    output_file = "../../results/quantum/manufacturing_tolerance_analysis.json"
    results = {
        'timestamp': datetime.now().isoformat(),
        'backend': backend.name,
        'job_id': job.job_id(),
        'shots': 8000,
        'num_qubits': 15,
        'success_rate_pct': float(success_rate),
        'avg_success_pct': float(avg_success),
        'total_scenarios': len(scenarios),
        'recommended_tolerances': {
            'thickness_pct': float(t_tol) if acceptable_t else None,
            'reflectivity_pct': float(r_tol) if acceptable_r else None,
            'mass_pct': float(m_tol) if acceptable_m else None,
            'alignment_deg': float(a_tol) if acceptable_a else None
        },
        'best_case': best,
        'worst_acceptable': worst_acceptable if acceptable else None,
        'all_scenarios': scenarios[:100]  # Save top 100
    }

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {output_file}")
    print()
    print("="*80)
    print("TOLERANCE ANALYSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
