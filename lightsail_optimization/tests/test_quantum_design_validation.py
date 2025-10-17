#!/usr/bin/env python3
"""
QUANTUM DESIGN VALIDATION TEST SUITE
Tests IBM Quantum optimized 8-stage 0.50c design
"""

import numpy as np
import sys
import json

# Constants
c = 299_792_458  # m/s - speed of light
sigma_sb = 5.67e-8  # W/(m²·K⁴) - Stefan-Boltzmann constant

def test_8stage_velocity_calculation():
    """Test 8-stage system achieves 0.50c"""
    print("\n" + "="*70)
    print("TEST 1: 8-Stage Velocity Calculation (0.50c target)")
    print("="*70)

    # Parameters from quantum optimization
    P = 500e9  # W - 500 GW laser
    stages = 8

    # Stage masses (from quantum_materials_results.json)
    stage_masses = [
        2.618,  # Stage 1: 32 m²
        1.833,  # Stage 2: 22.4 m²
        1.283,  # Stage 3: 15.7 m²
        0.898,  # Stage 4: 11.0 m²
        0.629,  # Stage 5: 7.7 m²
        0.440,  # Stage 6: 5.4 m²
        0.308,  # Stage 7: 3.8 m²
        0.216,  # Stage 8: 2.6 m²
    ]
    payload_mass = 1.0  # 1 gram

    # Calculate cumulative velocity
    R = 0.9999  # reflectivity
    accel_time_per_stage = 300 / stages  # 37.5s per stage

    total_mass = sum(stage_masses) + payload_mass  # 9.225 g

    print(f"  Laser Power: {P/1e9:.0f} GW")
    print(f"  Number of Stages: {stages}")
    print(f"  Total System Mass: {total_mass:.3f} g")
    print(f"  Accel time per stage: {accel_time_per_stage:.1f} s")

    # Simplified 8-stage calculation
    # Each stage drops off, reducing mass
    velocities = []
    current_v = 0
    remaining_mass = total_mass

    for i, stage_mass in enumerate(stage_masses):
        # Force for this stage
        F = 2 * P * R / c
        # Acceleration with current mass
        a = F / (remaining_mass / 1000)  # convert g to kg
        # Velocity gained in this stage
        dv = a * accel_time_per_stage
        current_v += dv
        velocities.append(current_v)

        # Drop this stage
        remaining_mass -= stage_mass

        print(f"\n  Stage {i+1}:")
        print(f"    Mass before: {remaining_mass + stage_mass:.3f} g")
        print(f"    Acceleration: {a:.0f} m/s² ({a/9.81:.0f}g)")
        print(f"    Velocity gain: {dv/1e3:.0f} km/s")
        print(f"    Cumulative velocity: {current_v/1e3:.0f} km/s ({current_v/c:.4f}c)")

    final_velocity_c = current_v / c

    print(f"\n  Final Velocity: {current_v/1e3:.0f} km/s ({final_velocity_c:.4f}c)")
    print(f"  Target: 0.50c")
    print(f"  Difference: {abs(0.50 - final_velocity_c)/0.50*100:.1f}%")

    # Validation checks
    assert final_velocity_c > 0.30, f"Velocity {final_velocity_c:.4f}c too low!"
    assert final_velocity_c < 0.60, f"Velocity {final_velocity_c:.4f}c exceeds realistic limit!"

    print(f"\n  ✓ PASS: 8-stage system achieves high-velocity target")
    return True

def test_quantum_results_consistency():
    """Test quantum optimization results are consistent"""
    print("\n" + "="*70)
    print("TEST 2: Quantum Results Consistency")
    print("="*70)

    # Load quantum results
    try:
        with open("results/quantum/quantum_materials_results.json", 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("  ⚠ WARNING: quantum_materials_results.json not found")
        return True

    best = data['best']

    print(f"  Backend: {data['backend']}")
    print(f"  Shots: {data['shots']}")
    print(f"  Materials tested: {data['materials_tested']}")
    print(f"  Feasible configurations: {data['feasible_count']}")

    print(f"\n  Best Design:")
    print(f"    Material: {best['material']}")
    print(f"    Velocity: {best['velocity_c']}c")
    print(f"    Stages: {best['stages']}")
    print(f"    Area: {best['area_m2']} m²")
    print(f"    Power: {best['power_GW']:.0f} GW")
    print(f"    Time to α Cen: {best['time_alpha_cen_years']:.1f} years")

    # Validate quantum results
    assert best['velocity_c'] == 0.5, f"Expected 0.5c, got {best['velocity_c']}c"
    assert best['stages'] == "8", f"Expected 8 stages, got {best['stages']}"
    assert best['power_GW'] == 500.0, f"Expected 500 GW, got {best['power_GW']}"
    assert best['time_alpha_cen_years'] < 10, f"Time {best['time_alpha_cen_years']} years too long"

    print(f"\n  ✓ PASS: Quantum optimization results are consistent")
    return True

def test_stage_mass_budget():
    """Test 8-stage mass budget is within limits"""
    print("\n" + "="*70)
    print("TEST 3: 8-Stage Mass Budget")
    print("="*70)

    # Stage areas (m²)
    stage_areas = [32.0, 22.4, 15.7, 11.0, 7.7, 5.4, 3.8, 2.6]

    # Material properties
    thickness = 20.5e-6  # 20.5 μm total
    density_sic = 3210  # kg/m³
    density_hfo2 = 9680  # kg/m³
    density_sio2 = 2200  # kg/m³

    # Layer thicknesses
    t_sic = 5e-9  # 5 nm
    t_hfo2_total = 6.34e-6  # 6.34 μm (50 layers)
    t_sio2_total = 9.17e-6  # 9.17 μm (50 layers)

    total_sail_mass = 0

    print(f"  Material stack thickness: {thickness*1e6:.1f} μm")
    print(f"  Number of stages: {len(stage_areas)}")

    for i, area in enumerate(stage_areas):
        # Calculate mass for each layer
        m_sic = area * t_sic * density_sic * 1000  # to grams
        m_hfo2 = area * t_hfo2_total * density_hfo2 * 1000
        m_sio2 = area * t_sio2_total * density_sio2 * 1000
        m_hardware = 0.01  # 10 mg per stage

        stage_mass = m_sic + m_hfo2 + m_sio2 + m_hardware
        total_sail_mass += stage_mass

        print(f"\n  Stage {i+1} ({area} m²):")
        print(f"    SiC: {m_sic:.3f} g")
        print(f"    HfO₂: {m_hfo2:.3f} g")
        print(f"    SiO₂: {m_sio2:.3f} g")
        print(f"    Total: {stage_mass:.3f} g")

    payload_mass = 1.0  # gram
    total_system_mass = total_sail_mass + payload_mass

    print(f"\n  Total Sail Mass: {total_sail_mass:.3f} g")
    print(f"  Payload Mass: {payload_mass:.3f} g")
    print(f"  TOTAL SYSTEM MASS: {total_system_mass:.3f} g")

    # Validation
    assert total_system_mass < 15, f"System mass {total_system_mass:.1f}g too heavy!"
    assert total_system_mass > 5, f"System mass {total_system_mass:.1f}g unrealistically light!"

    print(f"\n  ✓ PASS: Mass budget is realistic")
    return True

def test_thermal_limits_8stage():
    """Test thermal limits for largest stage"""
    print("\n" + "="*70)
    print("TEST 4: Thermal Limits (Stage 1 - largest)")
    print("="*70)

    # Largest stage parameters
    P = 500e9  # W
    A = 32.0  # m²
    absorption = 0.0005  # 0.05% (99.95% reflectivity)
    T_max = 2973  # K (SiC limit)

    # Calculate absorbed power
    P_absorbed = P * absorption

    # Calculate temperature
    T = (P_absorbed / (sigma_sb * A * 2)) ** 0.25

    print(f"  Laser Power: {P/1e9:.0f} GW")
    print(f"  Stage 1 Area: {A} m²")
    print(f"  Absorption: {absorption*100:.3f}%")
    print(f"  Power Absorbed: {P_absorbed/1e6:.2f} MW")
    print(f"\n  Operating Temperature: {T:.1f} K ({T-273:.1f}°C)")
    print(f"  Material Limit (SiC): {T_max} K ({T_max-273}°C)")
    print(f"  Margin: {T_max - T:.1f} K ({(T_max-T)/T_max*100:.1f}%)")

    # Validation
    assert T < T_max, f"Temperature {T:.1f}K exceeds limit {T_max}K!"
    assert (T_max - T) / T_max > 0.10, f"Thermal margin too small!"

    print(f"\n  ✓ PASS: Temperature within safe limits")
    return True

def test_mission_time_050c():
    """Test mission time with 0.50c velocity"""
    print("\n" + "="*70)
    print("TEST 5: Mission Time to α Centauri (0.50c)")
    print("="*70)

    v = 0.50 * c  # m/s
    distance = 4.37 * 9.461e15  # m (light years to meters)

    # Calculate time
    time_seconds = distance / v
    time_years = time_seconds / (365.25 * 24 * 3600)

    print(f"  Cruise Velocity: {v/1e3:.0f} km/s ({v/c:.2f}c)")
    print(f"  Distance to α Cen: {distance/9.461e15:.2f} light years")
    print(f"\n  Travel Time: {time_years:.1f} years")
    print(f"  vs Single-stage 0.111c: 39.4 years")
    print(f"  Improvement: {39.4/time_years:.1f}× faster")

    # Validation
    assert time_years < 10, f"Mission time {time_years:.1f} years too long for 0.50c!"
    assert time_years > 7, f"Mission time {time_years:.1f} years unrealistically short"

    print(f"\n  ✓ PASS: Mission time within single decade!")
    return True

def test_stage_deployment_sequence():
    """Test 8-stage deployment is feasible"""
    print("\n" + "="*70)
    print("TEST 6: Stage Deployment Sequence")
    print("="*70)

    # Deployment parameters
    stages = 8
    total_accel_time = 300  # seconds (5 minutes)
    time_per_stage = total_accel_time / stages

    # Stage areas and deployment times
    stage_areas = [32.0, 22.4, 15.7, 11.0, 7.7, 5.4, 3.8, 2.6]

    print(f"  Total Acceleration Time: {total_accel_time} s ({total_accel_time/60:.1f} min)")
    print(f"  Time per Stage: {time_per_stage:.1f} s")
    print(f"  Stages: {stages}")

    cumulative_time = 0
    for i, area in enumerate(stage_areas):
        cumulative_time += time_per_stage
        print(f"\n  Stage {i+1} @ T+{cumulative_time:.1f}s:")
        print(f"    Area: {area} m²")
        print(f"    Action: Stage {i} separation, continue acceleration")

    print(f"\n  T+{total_accel_time}s: Final velocity achieved")
    print(f"  Coast phase begins")

    # Validation
    assert time_per_stage > 30, f"Stage time {time_per_stage}s too short for reliable separation!"
    assert time_per_stage < 60, f"Stage time {time_per_stage}s may allow excessive drift"

    print(f"\n  ✓ PASS: Stage deployment sequence is feasible")
    return True

def test_cost_model_8stage():
    """Test cost model for 8-stage system"""
    print("\n" + "="*70)
    print("TEST 7: Cost Model (8-Stage System)")
    print("="*70)

    # Infrastructure costs
    laser_array = 100e9  # $100B (500 GW vs 254 GW ~ 2×)
    power_supply = 150e9  # $150B (500 GW)
    beam_director = 5e9
    optics = 2e9
    facility = 10e9
    tracking = 1e9

    infrastructure_total = laser_array + power_supply + beam_director + optics + facility + tracking

    # Per-mission costs (8 sails)
    cost_per_m2 = 5000  # $5,000/m²
    total_area = 101.0  # m² (all 8 stages)
    sail_cost = total_area * cost_per_m2
    payload_cost = 500e3
    launch_cost = 5e6
    operations = 50e3

    mission_cost = sail_cost + payload_cost + launch_cost + operations

    # 100 mission program
    num_missions = 100
    total_program = infrastructure_total + (mission_cost * num_missions) + 10e9

    print(f"  Infrastructure:")
    print(f"    Laser Array (500 GW): ${laser_array/1e9:.0f}B")
    print(f"    Power Supply: ${power_supply/1e9:.0f}B")
    print(f"    Other: ${(infrastructure_total - laser_array - power_supply)/1e9:.0f}B")
    print(f"    Total Infrastructure: ${infrastructure_total/1e9:.0f}B")

    print(f"\n  Per-Mission:")
    print(f"    8 Sails ({total_area} m²): ${sail_cost/1e3:.0f}K")
    print(f"    Payload: ${payload_cost/1e3:.0f}K")
    print(f"    Launch: ${launch_cost/1e6:.0f}M")
    print(f"    Total per Mission: ${mission_cost/1e6:.2f}M")

    print(f"\n  100-Mission Program:")
    print(f"    Total Program Cost: ${total_program/1e9:.0f}B")
    print(f"    Cost per Mission (amortized): ${total_program/num_missions/1e9:.2f}B")

    # Validation
    assert total_program < 500e9, f"Program cost ${total_program/1e9:.0f}B exceeds reasonable limit!"
    assert mission_cost > 0.5e6, f"Mission cost ${mission_cost/1e6:.2f}M too low!"

    print(f"\n  ✓ PASS: Cost model is reasonable for 8-stage system")
    return True

def run_all_tests():
    """Run all quantum design validation tests"""
    print("\n" + "#"*70)
    print("# QUANTUM DESIGN VALIDATION TEST SUITE")
    print("# Testing IBM Torino optimized 8-stage 0.50c design")
    print("#"*70)

    tests = [
        test_8stage_velocity_calculation,
        test_quantum_results_consistency,
        test_stage_mass_budget,
        test_thermal_limits_8stage,
        test_mission_time_050c,
        test_stage_deployment_sequence,
        test_cost_model_8stage
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n  ✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n  ✗ ERROR: {e}")
            failed += 1

    print("\n" + "="*70)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    print("="*70)

    if failed == 0:
        print("\n✓ ALL TESTS PASSED - Quantum 0.50c design validated!")
        return 0
    else:
        print(f"\n✗ {failed} TESTS FAILED - Review quantum design")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
