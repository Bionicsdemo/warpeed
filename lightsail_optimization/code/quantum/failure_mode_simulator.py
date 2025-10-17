"""
IBM Quantum Simulation: Failure Mode Analysis
==============================================
Analyzes potential failure modes and their probabilities using quantum simulation.
Identifies critical risks and mitigation strategies.

Goal: Achieve 95-100% mission success through risk identification
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
import json
from datetime import datetime

# IBM Quantum credentials
API_KEY = "bFodPcl5hR0To4S_FHWLA0GeYSm82dIQ5zTwUhVoGxwT"

# Failure modes and baseline probabilities
FAILURE_MODES = {
    'coating_delamination': {
        'name': 'Coating Delamination',
        'baseline_prob': 0.05,  # 5%
        'severity': 'CRITICAL',
        'mitigation': 'Improved adhesion layer, thermal cycling tests'
    },
    'thermal_runaway': {
        'name': 'Thermal Runaway (melting)',
        'baseline_prob': 0.02,  # 2%
        'severity': 'CRITICAL',
        'mitigation': 'Real-time temperature monitoring, laser power control'
    },
    'structural_tear': {
        'name': 'Structural Tear/Rip',
        'baseline_prob': 0.03,  # 3%
        'severity': 'CRITICAL',
        'mitigation': 'Reinforced edges, stress testing'
    },
    'stage_separation_fail': {
        'name': 'Stage Separation Failure',
        'baseline_prob': 0.08,  # 8% (highest risk!)
        'severity': 'HIGH',
        'mitigation': 'Redundant nichrome wires, backup pyrotechnic'
    },
    'laser_pointing_loss': {
        'name': 'Laser Pointing Loss',
        'baseline_prob': 0.04,  # 4%
        'severity': 'HIGH',
        'mitigation': 'Active tracking, beacon system'
    },
    'micrometeorite_impact': {
        'name': 'Micrometeorite Impact',
        'baseline_prob': 0.40,  # 40% over 8.7 years!
        'severity': 'MEDIUM',
        'mitigation': 'Launch multiple sails, small cross-section'
    },
    'electronics_failure': {
        'name': 'Electronics Failure (radiation)',
        'baseline_prob': 0.15,  # 15% over 8.7 years
        'severity': 'MEDIUM',
        'mitigation': 'Radiation-hardened components, redundancy'
    },
    'communication_loss': {
        'name': 'Communication Loss',
        'baseline_prob': 0.10,  # 10%
        'severity': 'LOW',
        'mitigation': 'Autonomous operation, backup transmitter'
    }
}

def calculate_mission_success(failure_probs):
    """
    Calculate overall mission success probability given individual failure probabilities.
    Uses fault tree analysis.
    """
    # Critical failures (any one causes total failure)
    critical_success = (
        (1 - failure_probs['coating_delamination']) *
        (1 - failure_probs['thermal_runaway']) *
        (1 - failure_probs['structural_tear'])
    )

    # High-severity failures (can tolerate 1-2 stage failures out of 8)
    stage_success = 1 - (failure_probs['stage_separation_fail']**2)  # At most 2 failures OK
    laser_success = 1 - failure_probs['laser_pointing_loss']

    # Medium-severity (mission can partially succeed)
    data_return_success = (
        (1 - failure_probs['micrometeorite_impact']) *
        (1 - failure_probs['electronics_failure'])
    )

    # Low-severity (affects data return only)
    comm_success = 1 - failure_probs['communication_loss']

    # Overall success (partial credit for partial success)
    full_success = critical_success * stage_success * laser_success * data_return_success * comm_success
    partial_success = critical_success * stage_success * laser_success * 0.5  # Some data even if electronics fail

    total_success = 0.8 * full_success + 0.2 * partial_success

    return total_success, full_success, partial_success

def create_failure_mode_circuit():
    """
    Create quantum circuit to explore failure mode combinations and mitigations.

    Encoding:
    - Qubits 0-2: Coating quality (0-7 scale, affects delamination)
    - Qubits 3-5: Thermal control (0-7 scale, affects thermal runaway)
    - Qubits 6-8: Structural integrity (0-7 scale, affects tearing)
    - Qubits 9-11: Stage separation reliability (0-7 scale)
    - Qubits 12-13: Laser pointing accuracy (0-3 scale)

    Total: 14 qubits
    """
    qc = QuantumCircuit(14, 14)

    # Initialize superposition
    for i in range(14):
        qc.h(i)

    # Entangle related failure modes
    # Coating quality affects thermal performance
    for i in range(3):
        qc.cx(i, 3+i)

    # Structural integrity affects stage separation
    for i in range(3):
        qc.cx(6+i, 9+i)

    # Add phase for failure probability
    for i in range(14):
        qc.rz(np.pi/6, i)

    # Measurement
    qc.measure(range(14), range(14))

    return qc

def decode_failure_bitstring(bitstring):
    """
    Decode quantum measurement to mitigation levels and failure probabilities.
    """
    coating_bits = bitstring[0:3]
    thermal_bits = bitstring[3:6]
    structural_bits = bitstring[6:9]
    separation_bits = bitstring[9:12]
    laser_bits = bitstring[12:14]

    # Convert to mitigation quality (0-7, higher = better)
    coating_quality = int(coating_bits, 2)
    thermal_quality = int(thermal_bits, 2)
    structural_quality = int(structural_bits, 2)
    separation_quality = int(separation_bits, 2)
    laser_quality = int(laser_bits, 2)

    # Calculate failure probabilities with mitigation
    # Better quality → lower failure probability
    failure_probs = {}

    # Coating delamination: 5% baseline, reduce to 0.5% with perfect quality
    failure_probs['coating_delamination'] = 0.05 * (1 - coating_quality/8.0) + 0.005

    # Thermal runaway: 2% baseline, reduce to 0.2% with active control
    failure_probs['thermal_runaway'] = 0.02 * (1 - thermal_quality/8.0) + 0.002

    # Structural tear: 3% baseline, reduce to 0.3% with reinforcement
    failure_probs['structural_tear'] = 0.03 * (1 - structural_quality/8.0) + 0.003

    # Stage separation: 8% baseline, reduce to 1% with redundancy
    failure_probs['stage_separation_fail'] = 0.08 * (1 - separation_quality/8.0) + 0.01

    # Laser pointing: 4% baseline, reduce to 0.4% with active tracking
    failure_probs['laser_pointing_loss'] = 0.04 * (1 - laser_quality/4.0) + 0.004

    # Fixed probabilities (external factors, less controllable)
    failure_probs['micrometeorite_impact'] = 0.40  # Launch multiple for redundancy
    failure_probs['electronics_failure'] = 0.15 * (1 - structural_quality/16.0)  # Radiation shielding helps
    failure_probs['communication_loss'] = 0.10  # Mostly autonomous

    return failure_probs, {
        'coating_quality': coating_quality,
        'thermal_quality': thermal_quality,
        'structural_quality': structural_quality,
        'separation_quality': separation_quality,
        'laser_quality': laser_quality
    }

def main():
    print("="*80)
    print("IBM QUANTUM SIMULATION: Failure Mode Analysis")
    print("="*80)
    print(f"Start time: {datetime.now()}")
    print()

    # Connect to IBM Quantum
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=API_KEY)

    # Select backend
    backend = service.least_busy(min_num_qubits=14, operational=True)
    print(f"Selected backend: {backend.name}")
    print(f"Qubits: {backend.num_qubits}")
    print()

    # Create circuit
    print("Creating quantum circuit (14 qubits)...")
    qc = create_failure_mode_circuit()
    print(f"Circuit depth: {qc.depth()}")
    print()

    # Transpile
    print("Transpiling circuit...")
    from qiskit import transpile
    qc_transpiled = transpile(qc, backend=backend, optimization_level=3)
    print(f"Transpiled depth: {qc_transpiled.depth()}")
    print()

    # Run on IBM Quantum without Session (open plan)
    print("Submitting job to IBM Quantum (10000 shots)...")
    print("Analyzing failure modes and mitigation strategies...")

    sampler = Sampler(mode=backend)
    job = sampler.run([qc_transpiled], shots=10000)

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

    # Analyze scenarios
    print("Analyzing failure scenarios...")
    scenarios = []

    for bitstring, count in counts.items():
        failure_probs, qualities = decode_failure_bitstring(bitstring)
        total_success, full_success, partial_success = calculate_mission_success(failure_probs)

        scenarios.append({
            'mitigation_quality': qualities,
            'failure_probabilities': failure_probs,
            'total_success_prob': float(total_success),
            'full_success_prob': float(full_success),
            'partial_success_prob': float(partial_success),
            'quantum_counts': int(count)
        })

    # Sort by success probability
    scenarios.sort(key=lambda x: x['total_success_prob'], reverse=True)

    print()
    print("="*80)
    print("FAILURE MODE ANALYSIS RESULTS")
    print("="*80)
    print()

    # Best case scenario
    best = scenarios[0]
    print("BEST CASE SCENARIO (Maximum Mitigation):")
    print()
    print("Mitigation Quality:")
    for key, val in best['mitigation_quality'].items():
        print(f"  {key}: {val}/7" if 'laser' not in key else f"  {key}: {val}/3")
    print()
    print("Failure Probabilities:")
    for mode, prob in best['failure_probabilities'].items():
        severity = FAILURE_MODES[mode]['severity']
        print(f"  {FAILURE_MODES[mode]['name']:.<40} {prob*100:>6.2f}% ({severity})")
    print()
    print(f"Total Success Probability: {best['total_success_prob']*100:.2f}%")
    print(f"  Full Success: {best['full_success_prob']*100:.2f}%")
    print(f"  Partial Success: {best['partial_success_prob']*100:.2f}%")
    print()

    # Worst case scenario (still with some mitigation)
    worst = scenarios[-1]
    print("WORST CASE SCENARIO (Minimal Mitigation):")
    print()
    print("Failure Probabilities:")
    for mode, prob in worst['failure_probabilities'].items():
        severity = FAILURE_MODES[mode]['severity']
        print(f"  {FAILURE_MODES[mode]['name']:.<40} {prob*100:>6.2f}% ({severity})")
    print()
    print(f"Total Success Probability: {worst['total_success_prob']*100:.2f}%")
    print()

    # Statistical analysis
    success_probs = [s['total_success_prob'] for s in scenarios]
    avg_success = np.mean(success_probs) * 100
    std_success = np.std(success_probs) * 100

    print("STATISTICAL SUMMARY:")
    print(f"  Average success probability: {avg_success:.2f}% ± {std_success:.2f}%")
    print(f"  Best case: {max(success_probs)*100:.2f}%")
    print(f"  Worst case: {min(success_probs)*100:.2f}%")
    print()

    # Count scenarios achieving 95% success
    high_success = [s for s in scenarios if s['total_success_prob'] >= 0.95]
    print(f"Scenarios achieving ≥95% success: {len(high_success)}/{len(scenarios)} ({len(high_success)/len(scenarios)*100:.1f}%)")
    print()

    # Critical mitigations
    if high_success:
        print("CRITICAL MITIGATIONS REQUIRED FOR 95% SUCCESS:")
        print()
        avg_qualities = {}
        for key in high_success[0]['mitigation_quality'].keys():
            vals = [s['mitigation_quality'][key] for s in high_success]
            avg_qualities[key] = np.mean(vals)
            max_val = 7 if 'laser' not in key else 3
            print(f"  {key:.<40} {avg_qualities[key]:.1f}/{max_val} (minimum)")
        print()

    # Recommendations
    print("="*80)
    print("RECOMMENDED MITIGATION STRATEGIES")
    print("="*80)
    print()

    for mode_key, mode_info in FAILURE_MODES.items():
        print(f"{mode_info['name']} ({mode_info['severity']} severity):")
        print(f"  Baseline probability: {mode_info['baseline_prob']*100:.1f}%")
        if high_success:
            best_mitigated = min([s['failure_probabilities'][mode_key] for s in high_success])
            reduction = (1 - best_mitigated/mode_info['baseline_prob']) * 100
            print(f"  With mitigation: {best_mitigated*100:.2f}% ({reduction:.0f}% reduction)")
        print(f"  Strategy: {mode_info['mitigation']}")
        print()

    # Save results
    output_file = "../../results/quantum/failure_mode_analysis.json"
    results = {
        'timestamp': datetime.now().isoformat(),
        'backend': backend.name,
        'job_id': job.job_id(),
        'shots': 10000,
        'num_qubits': 14,
        'avg_success_pct': float(avg_success),
        'std_success_pct': float(std_success),
        'best_case': best,
        'worst_case': worst,
        'high_success_count': len(high_success),
        'critical_mitigations': avg_qualities if high_success else None,
        'failure_modes': FAILURE_MODES,
        'top_scenarios': scenarios[:50]
    }

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {output_file}")
    print()
    print("="*80)
    print("FAILURE MODE ANALYSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
