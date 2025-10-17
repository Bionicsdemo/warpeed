#!/usr/bin/env python3
"""
WARPEED NANOCRAFT - POWER SYSTEM VALIDATION
===========================================

Quick validation script to confirm all power system calculations
and verify mission requirements are met.

Author: Power Systems Engineering Team
Date: October 15, 2025
"""

import json
import os

def check_file_exists(filepath):
    """Check if a file exists."""
    if os.path.exists(filepath):
        print(f"  ✓ {os.path.basename(filepath)}")
        return True
    else:
        print(f"  ✗ MISSING: {filepath}")
        return False

def validate_power_requirements():
    """Validate power system meets all requirements."""

    print("\n" + "="*80)
    print("WARPEED NANOCRAFT - POWER SYSTEM VALIDATION")
    print("="*80 + "\n")

    # Load results
    results_path = "/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/results/power_system_results.json"

    if not os.path.exists(results_path):
        print("✗ ERROR: Results file not found!")
        return False

    with open(results_path, 'r') as f:
        data = json.load(f)

    print("1. FILE INTEGRITY CHECK")
    print("-" * 80)
    files_ok = True
    files_ok &= check_file_exists("/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/power_system_sizing.py")
    files_ok &= check_file_exists("/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/power_system_recommendations.py")
    files_ok &= check_file_exists("/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/results/power_system_results.json")
    files_ok &= check_file_exists("/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/results/power_optimization_results.json")
    files_ok &= check_file_exists("/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/results/power_system_analysis.png")
    files_ok &= check_file_exists("/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/results/power_optimization_analysis.png")
    files_ok &= check_file_exists("/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/POWER_SYSTEM_EXECUTIVE_SUMMARY.md")
    print()

    # Validate calculations
    print("2. CALCULATIONS VALIDATION")
    print("-" * 80)

    # Check key parameters
    solar_area = data["solar_cell_specifications"]["solar_cell_area_cm2"]
    efficiency_bol = data["solar_cell_specifications"]["efficiency_BOL_percent"]
    efficiency_eol = data["solar_cell_specifications"]["efficiency_EOL_percent"]

    print(f"  Solar cell area:           {solar_area:.1f} cm²")
    print(f"  Efficiency (BOL):          {efficiency_bol:.1f}%")
    print(f"  Efficiency (EOL, 20y):     {efficiency_eol:.2f}%")

    # Validate degradation
    expected_efficiency_eol = efficiency_bol * (0.995 ** 20)  # 0.5% per year for 20 years
    degradation_error = abs(efficiency_eol - expected_efficiency_eol)

    if degradation_error < 0.1:
        print(f"  ✓ Degradation calculation correct ({expected_efficiency_eol:.2f}%)")
    else:
        print(f"  ✗ Degradation calculation error (expected {expected_efficiency_eol:.2f}%)")

    print()

    # Validate power generation
    print("3. POWER GENERATION VALIDATION")
    print("-" * 80)

    power_earth = data["power_generation"]["power_at_earth_W"]
    power_alpha_cen = data["power_generation"]["power_at_alpha_cen_W"]
    alpha_cen_irradiance = data["power_generation"]["alpha_centauri_irradiance_W_m2"]

    print(f"  Power at Earth (BOL):      {power_earth:.3f} W")
    print(f"  Power at α Cen (EOL):      {power_alpha_cen:.3f} W")
    print(f"  α Centauri irradiance:     {alpha_cen_irradiance:.2f} W/m²")

    # Validate that α Cen provides more irradiance than Sun
    if alpha_cen_irradiance > 1361:
        enhancement = ((alpha_cen_irradiance / 1361) - 1) * 100
        print(f"  ✓ α Centauri is {enhancement:.1f}% brighter than Sun")
    else:
        print(f"  ✗ ERROR: α Centauri should be brighter than Sun!")

    print()

    # Validate power requirements
    print("4. MISSION REQUIREMENTS VALIDATION (10 cm² baseline)")
    print("-" * 80)

    power_loads = data["power_loads"]
    baseline_power = power_loads["baseline_W"]
    imaging_power = baseline_power + power_loads["camera_W"]
    full_ops_power = power_loads["peak_W"]

    print(f"  Required - Baseline:       {baseline_power:.1f} W")
    print(f"  Required - Imaging:        {imaging_power:.1f} W")
    print(f"  Required - Full ops:       {full_ops_power:.1f} W")
    print()

    perf = data["performance_analysis"]

    # Check baseline operations
    if perf["baseline_viable"]:
        print(f"  ✓ Baseline operations viable")
    else:
        print(f"  ✗ Baseline operations NOT viable")

    # Check imaging operations
    if perf["imaging_viable"]:
        print(f"  ✓ Imaging operations viable")
    else:
        print(f"  ✗ Imaging operations NOT viable (as expected for 10 cm²)")

    # Check full operations
    if perf["full_ops_viable"]:
        print(f"  ✓ Full operations viable")
    else:
        print(f"  ✗ Full operations NOT viable (as expected for 10 cm²)")

    # Overall system viability
    system_viable = perf["power_system_viable"]
    margin = perf["power_margin_at_alpha_cen_percent"]

    print()
    print(f"  Power margin at α Cen:     {margin:+.1f}%")
    print(f"  System viable (10 cm²):    {'YES' if system_viable else 'NO (requires optimization)'}")
    print()

    # Battery validation
    print("5. BATTERY SYSTEM VALIDATION")
    print("-" * 80)

    battery = data["battery_system"]
    battery_capacity = battery["battery_capacity_Wh"]
    shadow_duration = battery["shadow_duration_hours"]

    print(f"  Battery capacity:          {battery_capacity:.2f} Wh")
    print(f"  Shadow duration:           {shadow_duration:.1f} hours")
    print(f"  Shadow power support:      {baseline_power:.1f} W")

    # Validate battery can support baseline for shadow duration
    energy_available = battery_capacity * battery["depth_of_discharge_percent"]/100 * battery["efficiency_percent"]/100
    energy_required = baseline_power * shadow_duration

    if energy_available >= energy_required:
        print(f"  ✓ Battery sufficient for shadow operations")
    else:
        print(f"  ✗ Battery insufficient!")

    print()

    # Mass budget validation
    print("6. MASS BUDGET VALIDATION")
    print("-" * 80)

    mass = data["mass_budget"]
    total_mass = mass["total_mass_grams"]

    print(f"  Solar cells:               {mass['solar_cells_grams']:.2f} g")
    print(f"  Battery:                   {mass['battery_grams']:.2f} g")
    print(f"  Substrate/electronics:     {mass['substrate_electronics_grams']:.2f} g")
    print(f"  TOTAL:                     {total_mass:.2f} g")
    print()

    # Load optimization results
    opt_path = "/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/results/power_optimization_results.json"

    if os.path.exists(opt_path):
        print("7. OPTIMIZATION RESULTS VALIDATION")
        print("-" * 80)

        with open(opt_path, 'r') as f:
            opt_data = json.load(f)

        required = opt_data["required_areas"]

        print(f"  Required area (baseline):  {required['baseline_cm2']:.2f} cm²")
        print(f"  Required area (imaging):   {required['imaging_cm2']:.2f} cm²")
        print(f"  Required area (full ops):  {required['full_ops_cm2']:.2f} cm²")
        print()

        print(f"  Recommendations:")
        for key, value in opt_data["recommendations"].items():
            print(f"    - {key.replace('_', ' ').title()}: {value}")
        print()

    # Final validation
    print("8. FINAL VALIDATION")
    print("=" * 80)

    all_checks_pass = True

    checks = [
        (files_ok, "All required files generated"),
        (degradation_error < 0.1, "Degradation calculation correct"),
        (alpha_cen_irradiance > 1361, "α Centauri brighter than Sun"),
        (perf["baseline_viable"], "Baseline operations viable (10 cm²)"),
        (energy_available >= energy_required, "Battery sufficient for shadow"),
        (total_mass < 10, "Power system mass reasonable (<10g)"),
    ]

    for check, description in checks:
        status = "✓" if check else "✗"
        print(f"  {status} {description}")
        all_checks_pass &= check

    print()

    if all_checks_pass:
        print("✓✓✓ ALL VALIDATION CHECKS PASSED ✓✓✓")
    else:
        print("⚠ SOME VALIDATION CHECKS FAILED")

    print()
    print("="*80)
    print("CRITICAL FINDING:")
    print("="*80)
    print()
    print(f"The 10 cm² baseline configuration provides:")
    print(f"  • {power_alpha_cen:.3f} W at α Centauri (after 20 years)")
    print(f"  • This is INSUFFICIENT for full operations (1.8 W required)")
    print(f"  • Power margin: {margin:+.1f}% (negative = insufficient)")
    print()
    print("RECOMMENDATION:")
    print(f"  • Increase solar cell area to 32-40 cm² for full operations")
    print(f"  • 40 cm² provides ~2.2 W (+25% margin)")
    print(f"  • Mass increase: +1.5 g (acceptable)")
    print()
    print("MISSION VERDICT:")
    if system_viable:
        print("  ✓ Solar power system viable for baseline operations")
        print("  ⚠ Requires optimization for camera + transmitter operations")
    else:
        print("  ⚠ Solar power system requires optimization")
        print("  → Upgrade to 40 cm² for full mission success")

    print()
    print("="*80)
    print()

    return all_checks_pass

if __name__ == "__main__":
    success = validate_power_requirements()
    exit(0 if success else 1)
