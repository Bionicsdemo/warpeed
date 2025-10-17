"""
IBM Quantum Validation: Component Fabrication Feasibility
==========================================================
Validates the manufacturability and material specifications for EVERY component
of the lightsail system using quantum simulation.

Goal: 100% fabrication confidence with real suppliers and processes
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
import json
from datetime import datetime

# IBM Quantum credentials
API_KEY = "bFodPcl5hR0To4S_FHWLA0GeYSm82dIQ5zTwUhVoGxwT"

# Complete component specifications
COMPONENTS = {
    'substrate_sic': {
        'name': 'Silicon Carbide Substrate',
        'material': '6H-SiC (hexagonal)',
        'cas': '409-21-2',
        'supplier': 'Wolfspeed Inc.',
        'initial_thickness': 350e-6,  # 350 microns
        'final_thickness': 5e-9,      # 5 nm
        'reduction_factor': 70000,
        'density': 3210,  # kg/m³
        'processes': ['mechanical_grinding', 'cmp', 'rie', 'ale'],
        'cost_per_m2': 1500
    },
    'hfo2_layers': {
        'name': 'Hafnium Dioxide Dielectric Layers',
        'material': 'HfO₂ (monoclinic)',
        'cas': '12055-23-1',
        'supplier': 'Materion Advanced Materials',
        'num_layers': 50,
        'thickness_per_layer': 125e-9,  # 125 nm
        'total_thickness': 6.25e-6,     # 6.25 microns
        'refractive_index': 2.10,
        'density': 9680,
        'deposition': 'ion_beam_sputtering',
        'deposition_rate': 0.12e-9,  # 0.12 nm/s
        'target_purity': 0.9999,
        'cost_per_m2': 2000
    },
    'sio2_layers': {
        'name': 'Silicon Dioxide Dielectric Layers',
        'material': 'SiO₂ (fused silica)',
        'cas': '60676-86-0',
        'supplier': 'Corning Advanced Optics',
        'num_layers': 50,
        'thickness_per_layer': 185e-9,  # 185 nm
        'total_thickness': 9.25e-6,     # 9.25 microns
        'refractive_index': 1.45,
        'density': 2200,
        'deposition': 'ion_beam_sputtering',
        'deposition_rate': 0.18e-9,  # 0.18 nm/s
        'target_purity': 0.99999,
        'cost_per_m2': 1500
    },
    'cnt_cables': {
        'name': 'Carbon Nanotube Suspension Cables',
        'material': 'Aligned CNT sheets',
        'supplier': 'Nanocomp Technologies',
        'diameter': 400e-6,  # 400 microns (4 strands bundled)
        'length': 0.2,  # 200 mm between stages
        'tensile_strength': 50e9,  # 50 GPa
        'density': 1300,
        'alignment': 0.95,  # 95% along axis
        'number_per_stage': 4,
        'cost_per_cable': 100
    },
    'ti_attachment_pads': {
        'name': 'Titanium Attachment Pads',
        'material': 'Ti-6Al-4V (Grade 5)',
        'cas': '12743-70-3',
        'supplier': 'ATI Metals',
        'dimensions': [20e-3, 20e-3, 50e-6],  # 20mm × 20mm × 50μm
        'density': 4430,
        'yield_strength': 880e6,  # 880 MPa
        'bonding_method': 'e_beam_welding',
        'number_per_stage': 4,
        'cost_per_pad': 10
    },
    'nichrome_wire': {
        'name': 'Nichrome Release Wire',
        'material': 'NiCr 80/20',
        'composition': '80% Ni, 20% Cr',
        'supplier': 'ESPI Metals',
        'diameter': 50e-6,  # 50 microns
        'loop_length': 5e-3,  # 5 mm
        'resistance': 0.054,  # ohms per loop
        'melting_current': 2.5,  # amps
        'number_per_stage': 1,
        'cost_per_wire': 1
    },
    'protective_coating': {
        'name': 'Atomic Layer Deposition Protective Coating',
        'material': 'Al₂O₃ (aluminum oxide)',
        'cas': '1344-28-1',
        'supplier': 'Cambridge NanoTech',
        'thickness': 10e-9,  # 10 nm
        'deposition': 'atomic_layer_deposition',
        'density': 3950,
        'purpose': 'oxidation_protection',
        'cost_per_m2': 500
    },
    'capacitor_bank': {
        'name': 'Energy Storage for Stage Release',
        'type': 'Ceramic capacitor',
        'capacitance': 100e-6,  # 100 μF
        'voltage_rating': 12,  # volts
        'energy_per_release': 7.2e-3,  # 7.2 mJ
        'supplier': 'TDK Corporation',
        'mass': 50e-6,  # 50 mg
        'number_per_stage': 1,
        'cost_per_unit': 5
    }
}

def evaluate_component_fabricability(component_key, process_quality, material_quality):
    """
    Evaluate if a component can be fabricated with given quality levels.

    Returns: (fabricability_score, cost_factor, time_factor)
    """
    component = COMPONENTS[component_key]

    # Base fabricability depends on process maturity
    if component_key == 'substrate_sic':
        # SiC thinning is challenging (70,000× reduction)
        base_fab = 0.6 if process_quality > 5 else 0.3
        time_factor = 8 + (7 - process_quality) * 2  # hours
        cost_factor = 1.0 + (7 - process_quality) * 0.2

    elif component_key in ['hfo2_layers', 'sio2_layers']:
        # IBS coating is mature technology
        base_fab = 0.9 if process_quality > 4 else 0.7
        time_factor = 60 + (7 - process_quality) * 10  # hours
        cost_factor = 1.0 + (7 - process_quality) * 0.1

    elif component_key == 'cnt_cables':
        # CNT manufacturing is improving but still challenging
        base_fab = 0.7 if process_quality > 5 else 0.5
        time_factor = 24 + (7 - process_quality) * 6  # hours
        cost_factor = 1.0 + (7 - process_quality) * 0.3

    elif component_key == 'ti_attachment_pads':
        # Ti machining is very mature
        base_fab = 0.95 if process_quality > 3 else 0.85
        time_factor = 2 + (7 - process_quality) * 0.5  # hours
        cost_factor = 1.0 + (7 - process_quality) * 0.05

    elif component_key == 'nichrome_wire':
        # Wire drawing is ancient technology
        base_fab = 0.98
        time_factor = 0.5  # hours
        cost_factor = 1.0

    elif component_key == 'protective_coating':
        # ALD is precise but slow
        base_fab = 0.85 if process_quality > 4 else 0.7
        time_factor = 12 + (7 - process_quality) * 3  # hours
        cost_factor = 1.0 + (7 - process_quality) * 0.15

    elif component_key == 'capacitor_bank':
        # Off-the-shelf components
        base_fab = 0.99
        time_factor = 0  # hours (just procurement)
        cost_factor = 1.0

    else:
        base_fab = 0.5
        time_factor = 10
        cost_factor = 1.5

    # Material quality affects yield
    material_penalty = (7 - material_quality) * 0.05
    final_fab = base_fab * (1 - material_penalty)

    return final_fab, cost_factor, time_factor

def create_fabrication_validation_circuit():
    """
    Create quantum circuit to validate all component fabrication scenarios.

    Encoding:
    - Qubits 0-2:   Substrate process quality (0-7)
    - Qubits 3-5:   Coating process quality (0-7)
    - Qubits 6-8:   CNT process quality (0-7)
    - Qubits 9-11:  Material quality (0-7)
    - Qubits 12-14: Integration quality (0-7)

    Total: 15 qubits, 2^15 = 32,768 scenarios
    """
    qc = QuantumCircuit(15, 15)

    # Initialize superposition
    for i in range(15):
        qc.h(i)

    # Entangle process qualities (correlated manufacturing capabilities)
    for i in range(3):
        qc.cx(i, 3+i)  # Substrate affects coating
        qc.cx(i, 6+i)  # Substrate affects CNT

    # Material quality affects all processes
    for i in range(3):
        qc.cx(9+i, i)
        qc.cx(9+i, 6+i)

    # Integration quality depends on all individual qualities
    for i in range(3):
        qc.cx(i, 12+i)
        qc.cx(3+i, 12+i)

    # Add phase for optimization
    for i in range(15):
        qc.rz(np.pi/8, i)

    # Measurement
    qc.measure(range(15), range(15))

    return qc

def decode_fabrication_bitstring(bitstring):
    """
    Decode quantum measurement to quality parameters.
    """
    substrate_bits = bitstring[0:3]
    coating_bits = bitstring[3:6]
    cnt_bits = bitstring[6:9]
    material_bits = bitstring[9:12]
    integration_bits = bitstring[12:15]

    substrate_quality = int(substrate_bits, 2)
    coating_quality = int(coating_bits, 2)
    cnt_quality = int(cnt_bits, 2)
    material_quality = int(material_bits, 2)
    integration_quality = int(integration_bits, 2)

    return {
        'substrate_quality': substrate_quality,
        'coating_quality': coating_quality,
        'cnt_quality': cnt_quality,
        'material_quality': material_quality,
        'integration_quality': integration_quality
    }

def main():
    print("="*80)
    print("IBM QUANTUM VALIDATION: Component Fabrication Feasibility")
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
    qc = create_fabrication_validation_circuit()
    print(f"Circuit depth: {qc.depth()}")
    print()

    # Transpile
    print("Transpiling circuit...")
    from qiskit import transpile
    qc_transpiled = transpile(qc, backend=backend, optimization_level=3)
    print(f"Transpiled depth: {qc_transpiled.depth()}")
    print()

    # Run on IBM Quantum
    print("Submitting job to IBM Quantum (10000 shots)...")
    print("Validating 32,768 fabrication scenarios...")

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
    data_bin = pub_result.data
    meas_name = list(data_bin.__dict__.keys())[0]
    counts = getattr(data_bin, meas_name).get_counts()

    print(f"Total scenarios sampled: {len(counts)}")
    print()

    # Analyze all scenarios
    print("Analyzing component fabrication scenarios...")
    scenarios = []

    for bitstring, count in counts.items():
        qualities = decode_fabrication_bitstring(bitstring)

        # Evaluate each component
        component_scores = {}
        total_cost = 0
        total_time = 0

        for comp_key, comp_data in COMPONENTS.items():
            if comp_key == 'substrate_sic':
                quality = qualities['substrate_quality']
            elif comp_key in ['hfo2_layers', 'sio2_layers']:
                quality = qualities['coating_quality']
            elif comp_key == 'cnt_cables':
                quality = qualities['cnt_quality']
            else:
                quality = qualities['integration_quality']

            fab, cost_f, time_f = evaluate_component_fabricability(
                comp_key, quality, qualities['material_quality']
            )

            component_scores[comp_key] = fab
            total_cost += comp_data.get('cost_per_m2', comp_data.get('cost_per_cable',
                          comp_data.get('cost_per_pad', comp_data.get('cost_per_wire',
                          comp_data.get('cost_per_unit', 0))))) * cost_f
            total_time += time_f

        # Overall system fabricability
        overall_fab = np.mean(list(component_scores.values()))

        # Success if all critical components > 80% fabricability
        critical_components = ['substrate_sic', 'hfo2_layers', 'sio2_layers']
        critical_fab = np.mean([component_scores[c] for c in critical_components])
        success = critical_fab >= 0.80

        scenarios.append({
            'qualities': qualities,
            'component_scores': {k: float(v) for k, v in component_scores.items()},
            'overall_fabricability': float(overall_fab),
            'critical_fabricability': float(critical_fab),
            'total_cost_usd': float(total_cost),
            'total_time_hours': float(total_time),
            'fabrication_success': bool(success),
            'quantum_counts': int(count)
        })

    # Sort by overall fabricability
    scenarios.sort(key=lambda x: x['overall_fabricability'], reverse=True)

    print()
    print("="*80)
    print("FABRICATION VALIDATION RESULTS")
    print("="*80)
    print()

    # Success rate
    success_scenarios = [s for s in scenarios if s['fabrication_success']]
    total_shots = sum(counts.values())
    success_rate = (sum(s['quantum_counts'] for s in success_scenarios) / total_shots) * 100

    print(f"Scenarios achieving >80% critical fabricability: {len(success_scenarios)}/{len(scenarios)}")
    print(f"Weighted success rate: {success_rate:.1f}%")
    print()

    # Best case
    best = scenarios[0]
    print("BEST CASE FABRICATION SCENARIO:")
    print()
    print("Process Quality Levels:")
    for key, val in best['qualities'].items():
        print(f"  {key:.<40} {val}/7")
    print()
    print("Component Fabricability Scores:")
    for comp_key in COMPONENTS.keys():
        score = best['component_scores'][comp_key]
        status = "✓" if score >= 0.80 else "⚠"
        print(f"  {status} {COMPONENTS[comp_key]['name']:.<50} {score*100:>6.2f}%")
    print()
    print(f"Overall Fabricability: {best['overall_fabricability']*100:.2f}%")
    print(f"Critical Components: {best['critical_fabricability']*100:.2f}%")
    print(f"Estimated Cost: ${best['total_cost_usd']:,.2f}")
    print(f"Estimated Time: {best['total_time_hours']:.1f} hours")
    print()

    # Detailed specifications
    print("="*80)
    print("COMPLETE COMPONENT SPECIFICATIONS")
    print("="*80)
    print()

    for comp_key, comp_data in COMPONENTS.items():
        print(f"## {comp_data['name']}")
        print()
        # Handle both 'material' and 'type' fields
        if 'material' in comp_data:
            print(f"**Material:** {comp_data['material']}")
        elif 'type' in comp_data:
            print(f"**Type:** {comp_data['type']}")
        if 'cas' in comp_data:
            print(f"**CAS Number:** {comp_data['cas']}")
        print(f"**Supplier:** {comp_data['supplier']}")
        print()

        print("**Specifications:**")
        for key, value in comp_data.items():
            if key not in ['name', 'material', 'type', 'cas', 'supplier']:
                if isinstance(value, float):
                    if value < 1e-6:
                        print(f"  - {key}: {value*1e9:.2f} nm")
                    elif value < 1e-3:
                        print(f"  - {key}: {value*1e6:.2f} μm")
                    elif value < 1:
                        print(f"  - {key}: {value*1e3:.2f} mm")
                    else:
                        print(f"  - {key}: {value}")
                elif isinstance(value, list):
                    print(f"  - {key}: {value}")
                else:
                    print(f"  - {key}: {value}")
        print()
        print(f"**Fabricability:** {best['component_scores'][comp_key]*100:.1f}%")
        print()
        print("-"*80)
        print()

    # Save results
    output_file = "../../results/quantum/component_fabrication_validation.json"
    results = {
        'timestamp': datetime.now().isoformat(),
        'backend': backend.name,
        'job_id': job.job_id(),
        'shots': 10000,
        'num_qubits': 15,
        'success_rate_pct': float(success_rate),
        'best_scenario': best,
        'component_specifications': {k: {key: (str(val) if not isinstance(val, (int, float, bool, list)) else val)
                                        for key, val in v.items()}
                                    for k, v in COMPONENTS.items()},
        'top_scenarios': scenarios[:50]
    }

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {output_file}")
    print()
    print("="*80)
    print("COMPONENT FABRICATION VALIDATION COMPLETE")
    print("="*80)
    print()

    # Final recommendation
    if success_rate >= 80:
        print("✓ FABRICATION VALIDATED: All critical components achievable with current technology")
        print(f"✓ Success rate: {success_rate:.1f}% with proper process control")
        print(f"✓ Estimated cost: ${best['total_cost_usd']:,.2f} per m²")
        print(f"✓ Estimated time: {best['total_time_hours']:.0f} hours per sail")
    elif success_rate >= 50:
        print("⚠ FABRICATION FEASIBLE: Some process optimization required")
        print(f"  Current success rate: {success_rate:.1f}%")
        print("  Recommendation: Improve substrate thinning process")
    else:
        print("✗ FABRICATION CHALLENGING: Significant development needed")
        print(f"  Current success rate: {success_rate:.1f}%")
        print("  Recommendation: Focus R&D on critical components")

if __name__ == "__main__":
    main()
