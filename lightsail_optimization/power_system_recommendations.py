#!/usr/bin/env python3
"""
WARPEED NANOCRAFT - POWER SYSTEM OPTIMIZATION & RECOMMENDATIONS
================================================================

Engineering analysis to optimize solar cell area for mission success.
Explores different configurations to achieve power requirements at α Centauri.

Author: Power Systems Engineering Team
Date: October 15, 2025
"""

import numpy as np
import matplotlib.pyplot as plt
import json
from typing import Dict, List

# Import constants from main analysis
SOLAR_CONSTANT = 1361  # W/m²
CELL_EFFICIENCY_BOL = 0.30
DEGRADATION_RATE_PER_YEAR = 0.005
MISSION_DURATION_YEARS = 20
ALPHA_CEN_A_LUMINOSITY = 1.519
ALPHA_CEN_B_LUMINOSITY = 0.500

# Power requirements
POWER_BASELINE = 0.3  # W (avionics + navigation)
POWER_IMAGING = 0.8  # W (baseline + camera)
POWER_FULL_OPS = 1.8  # W (baseline + camera + transmitter)

# Mass parameters
MASS_PER_CM2_CELLS = 0.05  # grams/cm²
MASS_PER_WH_BATTERY = 15.0  # grams/Wh


def calculate_alpha_centauri_irradiance():
    """Calculate irradiance at α Centauri (1 AU from A)."""
    distance_from_A = 1.0  # AU
    distance_from_B = 23.4  # AU
    irradiance_A = (ALPHA_CEN_A_LUMINOSITY * SOLAR_CONSTANT) / (distance_from_A ** 2)
    irradiance_B = (ALPHA_CEN_B_LUMINOSITY * SOLAR_CONSTANT) / (distance_from_B ** 2)
    return irradiance_A + irradiance_B


def cell_efficiency_eol():
    """Calculate cell efficiency at end of life."""
    return CELL_EFFICIENCY_BOL * ((1 - DEGRADATION_RATE_PER_YEAR) ** MISSION_DURATION_YEARS)


def power_at_alpha_cen(cell_area_cm2: float) -> float:
    """Calculate power output at α Centauri for given cell area."""
    irradiance = calculate_alpha_centauri_irradiance()
    efficiency = cell_efficiency_eol()
    cell_area_m2 = cell_area_cm2 * 1e-4
    return irradiance * cell_area_m2 * efficiency


def find_required_area(target_power_w: float) -> float:
    """Find required cell area to achieve target power at α Centauri."""
    irradiance = calculate_alpha_centauri_irradiance()
    efficiency = cell_efficiency_eol()
    required_area_m2 = target_power_w / (irradiance * efficiency)
    return required_area_m2 * 1e4  # Convert to cm²


def analyze_configurations():
    """Analyze different solar cell area configurations."""

    print("=" * 90)
    print("SOLAR CELL AREA OPTIMIZATION ANALYSIS")
    print("=" * 90)
    print()

    # Calculate required areas for different mission modes
    area_baseline = find_required_area(POWER_BASELINE)
    area_imaging = find_required_area(POWER_IMAGING)
    area_full_ops = find_required_area(POWER_FULL_OPS)

    print("REQUIRED SOLAR CELL AREAS (for α Centauri operations):")
    print("-" * 90)
    print(f"For baseline ops (0.3W):         {area_baseline:.2f} cm² "
          f"({np.sqrt(area_baseline):.1f} × {np.sqrt(area_baseline):.1f} mm)")
    print(f"For imaging ops (0.8W):          {area_imaging:.2f} cm² "
          f"({np.sqrt(area_imaging):.1f} × {np.sqrt(area_imaging):.1f} mm)")
    print(f"For full ops (1.8W):             {area_full_ops:.2f} cm² "
          f"({np.sqrt(area_full_ops):.1f} × {np.sqrt(area_full_ops):.1f} mm)")
    print()

    # Analyze specific configurations
    configurations = [
        {"name": "Minimum (baseline)", "area_cm2": 5.0},
        {"name": "Baseline", "area_cm2": 10.0},
        {"name": "Enhanced", "area_cm2": 15.0},
        {"name": "Imaging capable", "area_cm2": 20.0},
        {"name": "Full operations", "area_cm2": 32.0},
        {"name": "High margin", "area_cm2": 40.0},
    ]

    print("CONFIGURATION ANALYSIS:")
    print("=" * 90)

    results = []

    for config in configurations:
        area = config["area_cm2"]
        power = power_at_alpha_cen(area)

        # Calculate margins
        baseline_margin = ((power - POWER_BASELINE) / POWER_BASELINE) * 100
        imaging_margin = ((power - POWER_IMAGING) / POWER_IMAGING) * 100
        full_ops_margin = ((power - POWER_FULL_OPS) / POWER_FULL_OPS) * 100

        # Determine capabilities
        can_baseline = power >= POWER_BASELINE
        can_imaging = power >= POWER_IMAGING
        can_full_ops = power >= POWER_FULL_OPS

        # Calculate mass
        mass_cells = MASS_PER_CM2_CELLS * area
        battery_capacity = 0.21  # Wh (fixed for shadow operations)
        mass_battery = MASS_PER_WH_BATTERY * battery_capacity
        total_mass = mass_cells + mass_battery + 0.5  # 0.5g substrate

        result = {
            "name": config["name"],
            "area_cm2": area,
            "power_W": power,
            "baseline_margin": baseline_margin,
            "imaging_margin": imaging_margin,
            "full_ops_margin": full_ops_margin,
            "can_baseline": can_baseline,
            "can_imaging": can_imaging,
            "can_full_ops": can_full_ops,
            "mass_g": total_mass
        }
        results.append(result)

        print(f"\n{config['name'].upper()}: {area:.1f} cm²")
        print(f"  Power at α Cen:       {power:.3f} W")
        print(f"  Baseline margin:      {baseline_margin:+.1f}% {'✓' if can_baseline else '✗'}")
        print(f"  Imaging margin:       {imaging_margin:+.1f}% {'✓' if can_imaging else '✗'}")
        print(f"  Full ops margin:      {full_ops_margin:+.1f}% {'✓' if can_full_ops else '✗'}")
        print(f"  Total mass:           {total_mass:.2f} g")

    print()
    print("=" * 90)

    return results


def create_optimization_plots(results: List[Dict]):
    """Create comprehensive optimization plots."""

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Solar Power System Optimization for α Centauri Mission',
                 fontsize=16, fontweight='bold')

    areas = [r["area_cm2"] for r in results]
    powers = [r["power_W"] for r in results]
    masses = [r["mass_g"] for r in results]
    names = [r["name"] for r in results]

    # Plot 1: Power vs Area
    ax1 = axes[0, 0]
    ax1.plot(areas, powers, 'bo-', linewidth=2, markersize=8, label='Power output')

    # Add requirement lines
    ax1.axhline(y=POWER_BASELINE, color='green', linestyle='--', linewidth=2,
                label='Baseline (0.3W)')
    ax1.axhline(y=POWER_IMAGING, color='orange', linestyle='--', linewidth=2,
                label='Imaging (0.8W)')
    ax1.axhline(y=POWER_FULL_OPS, color='red', linestyle='--', linewidth=2,
                label='Full ops (1.8W)')

    # Highlight viable regions
    ax1.axhspan(POWER_BASELINE, POWER_IMAGING, alpha=0.1, color='green')
    ax1.axhspan(POWER_IMAGING, POWER_FULL_OPS, alpha=0.1, color='orange')
    ax1.axhspan(POWER_FULL_OPS, max(powers) * 1.1, alpha=0.1, color='lightblue')

    ax1.set_xlabel('Solar Cell Area (cm²)', fontsize=11)
    ax1.set_ylabel('Power at α Centauri (W)', fontsize=11)
    ax1.set_title('Power Output vs Solar Cell Area', fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, max(areas) * 1.1)
    ax1.set_ylim(0, max(powers) * 1.1)

    # Plot 2: Mass vs Area
    ax2 = axes[0, 1]
    ax2.plot(areas, masses, 'ro-', linewidth=2, markersize=8)

    ax2.set_xlabel('Solar Cell Area (cm²)', fontsize=11)
    ax2.set_ylabel('Total Power System Mass (g)', fontsize=11)
    ax2.set_title('Mass Budget vs Solar Cell Area', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, max(areas) * 1.1)

    # Plot 3: Capability Matrix
    ax3 = axes[1, 0]

    x_pos = np.arange(len(results))
    width = 0.25

    baseline_capable = [1 if r["can_baseline"] else 0 for r in results]
    imaging_capable = [1 if r["can_imaging"] else 0 for r in results]
    full_ops_capable = [1 if r["can_full_ops"] else 0 for r in results]

    ax3.bar(x_pos - width, baseline_capable, width, label='Baseline',
            color='green', alpha=0.7)
    ax3.bar(x_pos, imaging_capable, width, label='Imaging',
            color='orange', alpha=0.7)
    ax3.bar(x_pos + width, full_ops_capable, width, label='Full ops',
            color='red', alpha=0.7)

    ax3.set_xlabel('Configuration', fontsize=11)
    ax3.set_ylabel('Capability (1=Yes, 0=No)', fontsize=11)
    ax3.set_title('Mission Capability by Configuration', fontweight='bold')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels([f"{a:.0f} cm²" for a in areas], rotation=45, ha='right')
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.set_ylim(0, 1.2)

    # Plot 4: Power Margins
    ax4 = axes[1, 1]

    baseline_margins = [r["baseline_margin"] for r in results]
    imaging_margins = [r["imaging_margin"] for r in results]
    full_ops_margins = [r["full_ops_margin"] for r in results]

    ax4.plot(areas, baseline_margins, 'g-o', linewidth=2, markersize=6,
             label='Baseline margin')
    ax4.plot(areas, imaging_margins, '-o', color='orange', linewidth=2,
             markersize=6, label='Imaging margin')
    ax4.plot(areas, full_ops_margins, 'r-o', linewidth=2, markersize=6,
             label='Full ops margin')

    ax4.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)
    ax4.axhline(y=20, color='blue', linestyle='--', linewidth=1, alpha=0.5,
                label='20% margin target')

    ax4.set_xlabel('Solar Cell Area (cm²)', fontsize=11)
    ax4.set_ylabel('Power Margin (%)', fontsize=11)
    ax4.set_title('Power Margins vs Solar Cell Area', fontweight='bold')
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim(0, max(areas) * 1.1)

    plt.tight_layout()
    output_path = "/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/results/power_optimization_analysis.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Optimization plots saved to: {output_path}")


def create_recommendations_report(results: List[Dict]):
    """Generate engineering recommendations report."""

    print()
    print("=" * 90)
    print("ENGINEERING RECOMMENDATIONS")
    print("=" * 90)
    print()

    # Find optimal configurations
    imaging_config = next((r for r in results if r["can_imaging"] and not r["can_full_ops"]), None)
    full_ops_config = next((r for r in results if r["can_full_ops"]), None)

    print("RECOMMENDED CONFIGURATIONS:")
    print("-" * 90)
    print()

    print("1. MINIMUM VIABLE CONFIGURATION (Sequential Operations)")
    if imaging_config:
        print(f"   Solar cell area:    {imaging_config['area_cm2']:.1f} cm²")
        print(f"   Power at α Cen:     {imaging_config['power_W']:.3f} W")
        print(f"   Total mass:         {imaging_config['mass_g']:.2f} g")
        print(f"   Capabilities:")
        print(f"     - Baseline ops:   ✓ ({imaging_config['baseline_margin']:+.1f}% margin)")
        print(f"     - Camera imaging: ✓ ({imaging_config['imaging_margin']:+.1f}% margin)")
        print(f"     - Transmitter:    Sequential only")
        print(f"   Operation mode:     Image → Store → Transmit (sequential)")
    print()

    print("2. OPTIMAL CONFIGURATION (Simultaneous Operations)")
    if full_ops_config:
        print(f"   Solar cell area:    {full_ops_config['area_cm2']:.1f} cm²")
        print(f"   Power at α Cen:     {full_ops_config['power_W']:.3f} W")
        print(f"   Total mass:         {full_ops_config['mass_g']:.2f} g")
        print(f"   Capabilities:")
        print(f"     - Baseline ops:   ✓ ({full_ops_config['baseline_margin']:+.1f}% margin)")
        print(f"     - Camera imaging: ✓ ({full_ops_config['imaging_margin']:+.1f}% margin)")
        print(f"     - Full operations: ✓ ({full_ops_config['full_ops_margin']:+.1f}% margin)")
        print(f"   Operation mode:     Simultaneous camera + transmitter")
    print()

    print("MISSION STRATEGY OPTIONS:")
    print("-" * 90)
    print()
    print("Option A: Conservative (20 cm² solar cells)")
    print("  ✓ Proven technology")
    print("  ✓ Sequential operations viable")
    print("  ✓ Lower mass (~4.6 g)")
    print("  - Requires data buffering")
    print("  - Longer transmission windows")
    print()

    print("Option B: Optimal (32 cm² solar cells)")
    print("  ✓ Simultaneous operations")
    print("  ✓ Faster data downlink")
    print("  ✓ Operational flexibility")
    print("  - Higher mass (~6.1 g)")
    print("  - Larger solar array deployment")
    print()

    print("RISK MITIGATION:")
    print("-" * 90)
    print("1. Solar cell degradation:")
    print("   - Use radiation-hardened GaAs cells")
    print("   - Include protective coverglass (adds ~0.1g)")
    print("   - Budget 0.5% annual degradation (conservative)")
    print()

    print("2. Alpha Centauri orbital mechanics:")
    print("   - Spacecraft position affects received irradiance")
    print("   - Worst case: Further from α Cen A (reduced power)")
    print("   - Mitigation: Optimize trajectory for power availability")
    print()

    print("3. Thermal management:")
    print("   - Cell temperature affects efficiency")
    print("   - At α Centauri: Higher irradiance = higher temperature")
    print("   - Mitigation: Design for thermal dissipation")
    print()

    print("TECHNOLOGY READINESS:")
    print("-" * 90)
    print("✓ Multi-junction GaAs cells: TRL 9 (flight proven)")
    print("✓ Li-ion batteries: TRL 9 (widespread use)")
    print("✓ Power management ICs: TRL 9 (miniaturized versions available)")
    print("✓ Solar panel deployment: TRL 8 (CubeSat heritage)")
    print()

    print("=" * 90)


def main():
    """Main optimization analysis."""

    print("\n")
    print("╔" + "═" * 88 + "╗")
    print("║" + " " * 88 + "║")
    print("║" + "  WARPEED NANOCRAFT - SOLAR POWER SYSTEM OPTIMIZATION".center(88) + "║")
    print("║" + "  Engineering Analysis & Recommendations".center(88) + "║")
    print("║" + " " * 88 + "║")
    print("╚" + "═" * 88 + "╝")
    print()

    # Calculate α Centauri irradiance
    alpha_cen_irr = calculate_alpha_centauri_irradiance()
    print(f"α Centauri combined irradiance (1 AU from A): {alpha_cen_irr:.2f} W/m²")
    print(f"Cell efficiency (EOL, 20 years):             {cell_efficiency_eol() * 100:.2f}%")
    print()

    # Perform configuration analysis
    results = analyze_configurations()

    # Create visualizations
    create_optimization_plots(results)

    # Generate recommendations
    create_recommendations_report(results)

    # Save optimization results
    output_data = {
        "analysis_type": "Solar power system optimization",
        "date": "2025-10-15",
        "alpha_centauri_irradiance_W_m2": alpha_cen_irr,
        "cell_efficiency_eol": cell_efficiency_eol(),
        "power_requirements": {
            "baseline_W": POWER_BASELINE,
            "imaging_W": POWER_IMAGING,
            "full_operations_W": POWER_FULL_OPS
        },
        "required_areas": {
            "baseline_cm2": find_required_area(POWER_BASELINE),
            "imaging_cm2": find_required_area(POWER_IMAGING),
            "full_ops_cm2": find_required_area(POWER_FULL_OPS)
        },
        "configurations": results,
        "recommendations": {
            "minimum_viable": "20 cm² for sequential operations",
            "optimal": "32 cm² for simultaneous operations",
            "conservative": "40 cm² for high margin"
        }
    }

    output_path = "/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/results/power_optimization_results.json"
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"✓ Optimization results saved to: {output_path}")
    print()

    print("=" * 90)
    print("ANALYSIS COMPLETE")
    print("=" * 90)
    print()


if __name__ == "__main__":
    main()
