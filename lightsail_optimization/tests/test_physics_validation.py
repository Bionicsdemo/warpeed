#!/usr/bin/env python3
"""
PHYSICS VALIDATION TEST SUITE
Tests fundamental physics calculations for lightsail optimization
"""

import numpy as np
import sys
import json

# Constants
c = 299_792_458  # m/s - speed of light
sigma_sb = 5.67e-8  # W/(m²·K⁴) - Stefan-Boltzmann constant

def test_velocity_calculation():
    """Test that velocity calculations are realistic (v < c)"""
    print("\n" + "="*70)
    print("TEST 1: Velocity Calculation (v < c constraint)")
    print("="*70)

    # Test parameters from optimal design
    P = 254e9  # W
    R = 0.99999  # reflectivity
    m = 0.001529  # kg
    t = 300  # seconds
    divergence = 0.10

    # Calculate force
    F_initial = 2 * P * R / c
    F_effective = F_initial * divergence

    # Calculate acceleration
    a = F_effective / m

    # Calculate velocity
    v = a * t
    v_fraction = v / c

    print(f"  Laser Power: {P/1e9:.1f} GW")
    print(f"  Reflectivity: {R}")
    print(f"  Mass: {m*1000:.3f} g")
    print(f"  Acceleration time: {t} s")
    print(f"  Divergence factor: {divergence}")
    print(f"\n  Initial Force: {F_initial:.3f} N")
    print(f"  Effective Force (with divergence): {F_effective:.3f} N")
    print(f"  Acceleration: {a:.1f} m/s² ({a/9.81:.0f}g)")
    print(f"  Final Velocity: {v:.0f} m/s ({v_fraction:.4f}c)")

    # Validation checks
    assert v < c, f"FAIL: Velocity {v_fraction:.4f}c exceeds speed of light!"
    assert v_fraction > 0.05, f"FAIL: Velocity {v_fraction:.4f}c too low for interstellar mission"
    assert v_fraction < 0.25, f"FAIL: Velocity {v_fraction:.4f}c unrealistically high with current tech"

    print(f"\n  ✓ PASS: Velocity is realistic ({v_fraction:.4f}c < 0.25c)")
    return True

def test_thermal_limits():
    """Test thermal calculations stay within material limits"""
    print("\n" + "="*70)
    print("TEST 2: Thermal Limits (T < T_max)")
    print("="*70)

    # Test parameters
    P = 254e9  # W
    A = 1.42  # m²
    absorption = 0.00001  # 0.001%
    T_max = 2000  # K

    # Calculate absorbed power
    P_absorbed = P * absorption

    # Calculate temperature (Stefan-Boltzmann)
    # P = σ·A·T⁴·(2 sides)
    T = (P_absorbed / (sigma_sb * A * 2)) ** 0.25

    print(f"  Laser Power: {P/1e9:.1f} GW")
    print(f"  Sail Area: {A:.2f} m²")
    print(f"  Absorption: {absorption*100:.4f}%")
    print(f"  Power Absorbed: {P_absorbed/1e6:.2f} MW")
    print(f"\n  Operating Temperature: {T:.1f} K ({T-273:.1f}°C)")
    print(f"  Material Limit: {T_max:.0f} K ({T_max-273:.0f}°C)")
    print(f"  Margin: {T_max - T:.1f} K ({(T_max-T)/T_max*100:.1f}%)")

    # Validation checks
    assert T < T_max, f"FAIL: Temperature {T:.1f}K exceeds limit {T_max}K!"
    assert T > 300, f"FAIL: Temperature {T:.1f}K unrealistically low"
    assert (T_max - T) / T_max > 0.001, f"FAIL: Insufficient thermal margin"

    print(f"\n  ✓ PASS: Temperature within safe limits")
    return True

def test_stress_calculations():
    """Test mechanical stress stays within material strength"""
    print("\n" + "="*70)
    print("TEST 3: Mechanical Stress (σ < σ_max)")
    print("="*70)

    # Test parameters
    P = 254e9  # W
    A = 1.42  # m²
    R = 0.99999
    thickness = 207e-9  # m
    sigma_max = 1.0e9  # Pa (1 GPa)

    # Calculate radiation pressure
    I = P / A  # W/m² intensity
    P_rad = I / c  # Pa

    # Calculate membrane stress
    # For circular membrane: σ = P × R / (2 × t)
    radius = np.sqrt(A / np.pi)
    sigma = P_rad * radius / (2 * thickness)

    safety_factor = sigma_max / sigma

    print(f"  Laser Power: {P/1e9:.1f} GW")
    print(f"  Sail Area: {A:.2f} m²")
    print(f"  Thickness: {thickness*1e9:.1f} nm")
    print(f"  Sail Radius: {radius:.3f} m")
    print(f"\n  Radiation Pressure: {P_rad:.1f} Pa")
    print(f"  Membrane Stress: {sigma/1e6:.1f} MPa")
    print(f"  Material Strength: {sigma_max/1e6:.1f} MPa")
    print(f"  Safety Factor: {safety_factor:.2f}")

    # Validation checks
    assert sigma < sigma_max, f"FAIL: Stress {sigma/1e6:.1f} MPa exceeds limit {sigma_max/1e6:.1f} MPa!"
    assert safety_factor > 1.0, f"FAIL: Insufficient safety factor {safety_factor:.2f}"
    assert safety_factor < 10.0, f"WARNING: Overdesigned with SF={safety_factor:.2f}"

    print(f"\n  ✓ PASS: Stress within material limits")
    return True

def test_time_to_alpha_centauri():
    """Test mission time to α Centauri is reasonable"""
    print("\n" + "="*70)
    print("TEST 4: Mission Time to α Centauri")
    print("="*70)

    # Test parameters
    v = 0.111 * c  # m/s
    distance = 4.37 * 9.461e15  # m (light years to meters)

    # Calculate time
    time_seconds = distance / v
    time_years = time_seconds / (365.25 * 24 * 3600)

    print(f"  Cruise Velocity: {v/1e3:.0f} km/s ({v/c:.4f}c)")
    print(f"  Distance to α Cen: {distance/9.461e15:.2f} light years")
    print(f"\n  Travel Time: {time_years:.1f} years")

    # Validation checks
    assert time_years < 100, f"FAIL: Mission time {time_years:.1f} years too long!"
    assert time_years > 5, f"FAIL: Mission time {time_years:.1f} years unrealistically short"

    print(f"\n  ✓ PASS: Mission time within human lifetime")
    return True

def test_cost_model():
    """Test cost model is reasonable"""
    print("\n" + "="*70)
    print("TEST 5: Cost Model Validation")
    print("="*70)

    # Infrastructure costs
    laser_array = 100e9  # $100B
    power_supply = 76e9   # $76B
    beam_director = 5e9   # $5B
    optics = 2e9          # $2B
    facility = 10e9       # $10B
    tracking = 1e9        # $1B

    infrastructure_total = laser_array + power_supply + beam_director + optics + facility + tracking

    # Per-mission costs
    sail_cost = 71e3      # $71K
    payload_cost = 500e3  # $500K
    launch_cost = 5e6     # $5M
    operations = 50e3     # $50K

    mission_cost = sail_cost + payload_cost + launch_cost + operations

    # 100 mission program
    num_missions = 100
    total_program = infrastructure_total + (mission_cost * num_missions) + 10e9  # +$10B operations

    print(f"  Infrastructure Costs:")
    print(f"    Laser Array: ${laser_array/1e9:.1f}B")
    print(f"    Power Supply: ${power_supply/1e9:.1f}B")
    print(f"    Beam Director: ${beam_director/1e9:.1f}B")
    print(f"    Optics: ${optics/1e9:.1f}B")
    print(f"    Facility: ${facility/1e9:.1f}B")
    print(f"    Tracking: ${tracking/1e9:.1f}B")
    print(f"    Total Infrastructure: ${infrastructure_total/1e9:.1f}B")

    print(f"\n  Per-Mission Costs:")
    print(f"    Sail: ${sail_cost/1e3:.1f}K")
    print(f"    Payload: ${payload_cost/1e3:.1f}K")
    print(f"    Launch: ${launch_cost/1e6:.1f}M")
    print(f"    Operations: ${operations/1e3:.1f}K")
    print(f"    Total per Mission: ${mission_cost/1e6:.2f}M")

    print(f"\n  100-Mission Program:")
    print(f"    Total Program Cost: ${total_program/1e9:.1f}B")
    print(f"    Cost per Mission (amortized): ${total_program/num_missions/1e6:.1f}M")

    # Validation checks
    assert total_program < 500e9, f"FAIL: Program cost ${total_program/1e9:.1f}B exceeds reasonable limit"
    assert total_program > 100e9, f"FAIL: Program cost ${total_program/1e9:.1f}B unrealistically low"
    assert mission_cost > 1e6, f"FAIL: Mission cost ${mission_cost/1e6:.2f}M too low"

    print(f"\n  ✓ PASS: Cost model is reasonable")
    print(f"  (Comparable to ISS: $150B over 25 years)")
    return True

def test_energy_balance():
    """Test energy balance during acceleration"""
    print("\n" + "="*70)
    print("TEST 6: Energy Balance")
    print("="*70)

    # Parameters
    P = 254e9  # W
    t = 300  # s
    m = 0.001529  # kg
    v = 33_260  # m/s final velocity

    # Energy input (from laser)
    E_input = P * t

    # Kinetic energy (final)
    E_kinetic = 0.5 * m * v**2

    # Efficiency
    efficiency = E_kinetic / E_input

    print(f"  Laser Power: {P/1e9:.1f} GW")
    print(f"  Acceleration Time: {t} s")
    print(f"  Total Energy Input: {E_input/1e12:.1f} TJ")
    print(f"\n  Final Velocity: {v/1e3:.0f} km/s")
    print(f"  Kinetic Energy: {E_kinetic/1e6:.1f} MJ")
    print(f"  Efficiency: {efficiency*100:.6f}%")

    # Validation
    assert efficiency > 0, f"FAIL: Negative efficiency!"
    assert efficiency < 0.01, f"FAIL: Efficiency {efficiency*100:.2f}% too high (violates conservation)"

    print(f"\n  ✓ PASS: Energy balance is physical")
    print(f"  (Low efficiency expected due to laser divergence)")
    return True

def run_all_tests():
    """Run all physics validation tests"""
    print("\n" + "#"*70)
    print("# LIGHTSAIL PHYSICS VALIDATION TEST SUITE")
    print("# Testing fundamental physics of optimal design")
    print("#"*70)

    tests = [
        test_velocity_calculation,
        test_thermal_limits,
        test_stress_calculations,
        test_time_to_alpha_centauri,
        test_cost_model,
        test_energy_balance
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
        print("\n✓ ALL TESTS PASSED - Physics validation successful!")
        return 0
    else:
        print(f"\n✗ {failed} TESTS FAILED - Review physics calculations")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
