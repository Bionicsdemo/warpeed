#!/usr/bin/env python3
"""
Analyze and Visualize Quantum Integrated Spacecraft Results
============================================================

Comprehensive analysis of the quantum optimization results including:
- Pareto frontier visualization
- Trade space analysis
- Sensitivity analysis
- Risk assessment
- Architecture comparison
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import seaborn as sns
from typing import Dict, List
import pandas as pd

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['font.size'] = 10


def load_results(filepath: str) -> Dict:
    """Load optimization results"""
    with open(filepath, 'r') as f:
        return json.load(f)


def create_comprehensive_analysis(results: Dict, output_dir: str):
    """Create comprehensive analysis plots"""

    # Extract data
    top_designs = results['top_50_designs']
    pareto_frontier = results['pareto_frontier']
    sweet_spot = results['sweet_spot']

    # Create DataFrame for easier analysis
    df = pd.DataFrame(top_designs)

    # Create figure with subplots
    fig = plt.figure(figsize=(20, 16))
    gs = GridSpec(4, 3, figure=fig, hspace=0.3, wspace=0.3)

    # 1. Pareto Frontier: Velocity vs Science Capability
    ax1 = fig.add_subplot(gs[0, :])
    velocities = df['final_velocity_c'].values
    science_capability = df['data_rate_bps'].values * (1 + df['power_margin'].values)

    # Plot all designs
    scatter = ax1.scatter(velocities * 100, science_capability / 1e6,
                         c=df['total_mass_g'], s=100, alpha=0.6,
                         cmap='viridis', edgecolors='black', linewidth=0.5)

    # Plot Pareto frontier
    if pareto_frontier:
        pareto_df = pd.DataFrame(pareto_frontier)
        pareto_v = pareto_df['final_velocity_c'].values
        pareto_s = pareto_df['data_rate_bps'].values * (1 + pareto_df['power_margin'].values)
        indices = np.argsort(pareto_v)
        ax1.plot(pareto_v[indices] * 100, pareto_s[indices] / 1e6,
                'r-', linewidth=2, label='Pareto Frontier', zorder=10)

    # Plot sweet spot
    sweet_v = sweet_spot['final_velocity_c']
    sweet_s = sweet_spot['data_rate_bps'] * (1 + sweet_spot['power_margin'])
    ax1.scatter([sweet_v * 100], [sweet_s / 1e6],
               marker='*', s=500, c='red', edgecolors='black',
               linewidth=2, label='Sweet Spot', zorder=20)

    ax1.set_xlabel('Final Velocity (% of c)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Science Capability (Mbps × margin)', fontsize=12, fontweight='bold')
    ax1.set_title('Pareto Frontier: Velocity vs Science Capability', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    cbar = plt.colorbar(scatter, ax=ax1)
    cbar.set_label('Total Mass (g)', fontsize=10)

    # 2. Mass Breakdown
    ax2 = fig.add_subplot(gs[1, 0])
    top_5 = df.head(5)

    # Calculate mass components for top 5 designs
    mass_categories = []
    for i, design in enumerate(top_5.itertuples(), 1):
        # Reconstruct mass breakdown (simplified)
        solar_mass = design.solar_area_cm2 * 0.15
        battery_mass = design.battery_capacity_wh / 0.05
        comm_mass = design.total_mass_g * 0.2  # approx
        structure = design.structural_mass_g
        thermal = design.thermal_mass_g
        payload = 2.0

        mass_categories.append({
            'Design': f'#{i}',
            'Solar': solar_mass,
            'Battery': battery_mass,
            'Comm': comm_mass,
            'Structure': structure,
            'Thermal': thermal,
            'Payload': payload
        })

    mass_df = pd.DataFrame(mass_categories)
    mass_df.set_index('Design')[['Solar', 'Battery', 'Comm', 'Structure', 'Thermal', 'Payload']].plot(
        kind='bar', stacked=True, ax=ax2, colormap='tab10'
    )
    ax2.set_ylabel('Mass (g)', fontsize=10, fontweight='bold')
    ax2.set_title('Top 5 Designs: Mass Breakdown', fontsize=12, fontweight='bold')
    ax2.legend(loc='upper right', fontsize=8)
    ax2.grid(True, alpha=0.3, axis='y')
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=0)

    # 3. Power Budget Analysis
    ax3 = fig.add_subplot(gs[1, 1])
    power_margin = df.head(10)['power_margin'].values * 100
    design_labels = [f'#{i+1}' for i in range(len(power_margin))]

    colors = ['green' if pm >= 20 else 'orange' if pm >= 0 else 'red' for pm in power_margin]
    bars = ax3.barh(design_labels, power_margin, color=colors, alpha=0.7, edgecolor='black')

    ax3.axvline(x=20, color='green', linestyle='--', linewidth=2, label='Target Margin')
    ax3.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Zero Margin')
    ax3.set_xlabel('Power Margin (%)', fontsize=10, fontweight='bold')
    ax3.set_ylabel('Design', fontsize=10, fontweight='bold')
    ax3.set_title('Top 10 Designs: Power Margin', fontsize=12, fontweight='bold')
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3, axis='x')

    # 4. Communication Performance
    ax4 = fig.add_subplot(gs[1, 2])
    comm_snr = df.head(10)['comm_snr_db'].values

    colors_comm = ['green' if snr >= 8 else 'orange' if snr >= 0 else 'red' for snr in comm_snr]
    bars = ax4.barh(design_labels, comm_snr, color=colors_comm, alpha=0.7, edgecolor='black')

    ax4.axvline(x=8, color='green', linestyle='--', linewidth=2, label='Strong Signal')
    ax4.axvline(x=0, color='orange', linestyle='--', linewidth=2, label='Weak Signal')
    ax4.set_xlabel('Communication SNR (dB)', fontsize=10, fontweight='bold')
    ax4.set_ylabel('Design', fontsize=10, fontweight='bold')
    ax4.set_title('Top 10 Designs: Communication SNR', fontsize=12, fontweight='bold')
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3, axis='x')

    # 5. Architecture Comparison
    ax5 = fig.add_subplot(gs[2, 0])

    arch_data = []
    for arch_name, arch_designs in results['architectures'].items():
        if arch_designs:
            best_design = arch_designs[0]
            arch_data.append({
                'Architecture': arch_name.replace('_', ' ').title(),
                'Mass': best_design['total_mass_g'],
                'Velocity': best_design['final_velocity_c'] * 100,
                'Mission Value': best_design['mission_value']
            })

    if arch_data:
        arch_df = pd.DataFrame(arch_data)
        x = np.arange(len(arch_df))
        width = 0.25

        ax5.bar(x - width, arch_df['Mass'], width, label='Mass (g)', alpha=0.8)
        ax5.bar(x, arch_df['Velocity'], width, label='Velocity (% c)', alpha=0.8)
        ax5.bar(x + width, arch_df['Mission Value'] * 10, width, label='Mission Value (×10)', alpha=0.8)

        ax5.set_xlabel('Architecture', fontsize=10, fontweight='bold')
        ax5.set_ylabel('Value', fontsize=10, fontweight='bold')
        ax5.set_title('Architecture Comparison', fontsize=12, fontweight='bold')
        ax5.set_xticks(x)
        ax5.set_xticklabels(arch_df['Architecture'], rotation=15, ha='right')
        ax5.legend(fontsize=8)
        ax5.grid(True, alpha=0.3, axis='y')

    # 6. Travel Time vs Data Rate
    ax6 = fig.add_subplot(gs[2, 1])
    travel_time = df['travel_time_years'].values
    data_rate = df['data_rate_bps'].values / 1e6

    scatter = ax6.scatter(travel_time, data_rate, c=df['mission_value'],
                         s=100, alpha=0.7, cmap='plasma', edgecolors='black', linewidth=0.5)
    ax6.scatter([sweet_spot['travel_time_years']], [sweet_spot['data_rate_bps'] / 1e6],
               marker='*', s=500, c='red', edgecolors='black', linewidth=2, zorder=10)

    ax6.set_xlabel('Travel Time (years)', fontsize=10, fontweight='bold')
    ax6.set_ylabel('Data Rate (Mbps)', fontsize=10, fontweight='bold')
    ax6.set_title('Trade-off: Speed vs Communication', fontsize=12, fontweight='bold')
    ax6.grid(True, alpha=0.3)

    cbar = plt.colorbar(scatter, ax=ax6)
    cbar.set_label('Mission Value', fontsize=8)

    # 7. Cost vs Performance
    ax7 = fig.add_subplot(gs[2, 2])
    cost = df['cost_usd'].values / 1000
    performance = df['mission_value'].values

    colors_cost = ['green' if c <= 500 else 'red' for c in cost]
    scatter = ax7.scatter(cost, performance, c=colors_cost, s=100, alpha=0.7, edgecolors='black', linewidth=0.5)
    ax7.axvline(x=500, color='red', linestyle='--', linewidth=2, label='Budget Limit')
    ax7.scatter([sweet_spot['cost_usd'] / 1000], [sweet_spot['mission_value']],
               marker='*', s=500, c='red', edgecolors='black', linewidth=2, zorder=10)

    ax7.set_xlabel('Cost ($K)', fontsize=10, fontweight='bold')
    ax7.set_ylabel('Mission Value', fontsize=10, fontweight='bold')
    ax7.set_title('Cost vs Performance', fontsize=12, fontweight='bold')
    ax7.legend(fontsize=8)
    ax7.grid(True, alpha=0.3)

    # 8. Communication Type Distribution
    ax8 = fig.add_subplot(gs[3, 0])
    comm_types = df['comm_type'].value_counts()
    colors_pie = ['#ff9999', '#66b3ff', '#99ff99']
    ax8.pie(comm_types.values, labels=comm_types.index, autopct='%1.1f%%',
           colors=colors_pie, startangle=90, textprops={'fontsize': 10})
    ax8.set_title('Communication Type Distribution\n(Top 50 Designs)', fontsize=12, fontweight='bold')

    # 9. Velocity Distribution by Architecture
    ax9 = fig.add_subplot(gs[3, 1])

    velocities_by_arch = []
    labels_by_arch = []
    for arch_name, arch_designs in results['architectures'].items():
        if arch_designs:
            velocities_by_arch.append([d['final_velocity_c'] * 100 for d in arch_designs[:20]])
            labels_by_arch.append(arch_name.replace('_', ' ').title())

    if velocities_by_arch:
        bp = ax9.boxplot(velocities_by_arch, labels=labels_by_arch, patch_artist=True)
        for patch, color in zip(bp['boxes'], ['lightblue', 'lightgreen', 'lightcoral']):
            patch.set_facecolor(color)

        ax9.set_ylabel('Final Velocity (% of c)', fontsize=10, fontweight='bold')
        ax9.set_title('Velocity Distribution by Architecture', fontsize=12, fontweight='bold')
        ax9.grid(True, alpha=0.3, axis='y')
        plt.setp(ax9.xaxis.get_majorticklabels(), rotation=15, ha='right')

    # 10. Constraint Violations Heatmap
    ax10 = fig.add_subplot(gs[3, 2])

    # Count constraint violations
    violation_counts = {}
    for design in top_designs[:20]:
        for violation_type in design['violation_details'].keys():
            violation_counts[violation_type] = violation_counts.get(violation_type, 0) + 1

    if violation_counts:
        violations_sorted = sorted(violation_counts.items(), key=lambda x: x[1], reverse=True)
        v_types = [v[0].replace('_', ' ').title() for v in violations_sorted]
        v_counts = [v[1] for v in violations_sorted]

        bars = ax10.barh(v_types, v_counts, color='salmon', alpha=0.7, edgecolor='black')
        ax10.set_xlabel('Number of Violations (out of 20)', fontsize=10, fontweight='bold')
        ax10.set_title('Most Common Constraint Violations', fontsize=12, fontweight='bold')
        ax10.grid(True, alpha=0.3, axis='x')

    plt.suptitle('Quantum Integrated Spacecraft Optimization: Comprehensive Analysis',
                fontsize=16, fontweight='bold', y=0.995)

    # Save figure
    plt.savefig(f'{output_dir}/integrated_analysis.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved comprehensive analysis plot")

    plt.close()


def create_sensitivity_analysis(results: Dict, output_dir: str):
    """Create sensitivity analysis plots"""

    top_designs = results['top_50_designs']
    df = pd.DataFrame(top_designs)

    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Sensitivity Analysis: Parameter Impact on Mission Value',
                fontsize=16, fontweight='bold')

    # Parameters to analyze
    params = [
        ('solar_area_cm2', 'Solar Area (cm²)'),
        ('tx_power_w', 'TX Power (W)'),
        ('tx_aperture_m', 'TX Aperture (m)'),
        ('total_mass_g', 'Total Mass (g)'),
        ('final_velocity_c', 'Final Velocity (×c)'),
        ('data_rate_bps', 'Data Rate (Mbps)')
    ]

    for ax, (param, label) in zip(axes.flat, params):
        if param in df.columns:
            x_vals = df[param].values
            if param == 'data_rate_bps':
                x_vals = x_vals / 1e6
            y_vals = df['mission_value'].values

            scatter = ax.scatter(x_vals, y_vals, c=df['constraints_met'].astype(int),
                               s=80, alpha=0.7, cmap='RdYlGn', edgecolors='black', linewidth=0.5)

            # Fit polynomial trend
            if len(x_vals) > 3:
                z = np.polyfit(x_vals, y_vals, 2)
                p = np.poly1d(z)
                x_trend = np.linspace(x_vals.min(), x_vals.max(), 100)
                ax.plot(x_trend, p(x_trend), 'r--', linewidth=2, alpha=0.8)

            ax.set_xlabel(label, fontsize=10, fontweight='bold')
            ax.set_ylabel('Mission Value', fontsize=10, fontweight='bold')
            ax.set_title(f'Impact of {label}', fontsize=11, fontweight='bold')
            ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/sensitivity_analysis.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved sensitivity analysis plot")

    plt.close()


def create_risk_assessment(results: Dict, output_dir: str):
    """Create risk assessment visualization"""

    top_designs = results['top_50_designs'][:20]
    df = pd.DataFrame(top_designs)

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Risk Assessment: Top 20 Designs', fontsize=16, fontweight='bold')

    # 1. Power Risk (margin < 20%)
    ax1 = axes[0, 0]
    design_nums = np.arange(1, 21)
    power_margins = df['power_margin'].values * 100

    colors = ['green' if pm >= 20 else 'orange' if pm >= 10 else 'red' for pm in power_margins]
    bars = ax1.bar(design_nums, power_margins, color=colors, alpha=0.7, edgecolor='black')

    ax1.axhline(y=20, color='green', linestyle='--', linewidth=2, label='Safe Zone')
    ax1.axhline(y=10, color='orange', linestyle='--', linewidth=2, label='Caution Zone')
    ax1.axhline(y=0, color='red', linestyle='--', linewidth=2, label='Critical')

    ax1.set_xlabel('Design Rank', fontsize=10, fontweight='bold')
    ax1.set_ylabel('Power Margin (%)', fontsize=10, fontweight='bold')
    ax1.set_title('Power System Risk', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3, axis='y')

    # 2. Communication Risk (SNR)
    ax2 = axes[0, 1]
    comm_snr = df['comm_snr_db'].values

    colors = ['green' if snr >= 8 else 'orange' if snr >= 0 else 'red' for snr in comm_snr]
    bars = ax2.bar(design_nums, comm_snr, color=colors, alpha=0.7, edgecolor='black')

    ax2.axhline(y=8, color='green', linestyle='--', linewidth=2, label='Strong Link')
    ax2.axhline(y=0, color='orange', linestyle='--', linewidth=2, label='Weak Link')
    ax2.axhline(y=-10, color='red', linestyle='--', linewidth=2, label='Critical')

    ax2.set_xlabel('Design Rank', fontsize=10, fontweight='bold')
    ax2.set_ylabel('Communication SNR (dB)', fontsize=10, fontweight='bold')
    ax2.set_title('Communication Risk', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3, axis='y')

    # 3. Mission Duration Risk
    ax3 = axes[1, 0]
    travel_times = df['travel_time_years'].values

    colors = ['green' if tt <= 30 else 'orange' if tt <= 40 else 'red' for tt in travel_times]
    bars = ax3.bar(design_nums, travel_times, color=colors, alpha=0.7, edgecolor='black')

    ax3.axhline(y=30, color='green', linestyle='--', linewidth=2, label='Short Mission')
    ax3.axhline(y=40, color='orange', linestyle='--', linewidth=2, label='Long Mission')
    ax3.axhline(y=50, color='red', linestyle='--', linewidth=2, label='Max Duration')

    ax3.set_xlabel('Design Rank', fontsize=10, fontweight='bold')
    ax3.set_ylabel('Travel Time (years)', fontsize=10, fontweight='bold')
    ax3.set_title('Mission Duration Risk', fontsize=12, fontweight='bold')
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3, axis='y')

    # 4. Overall Risk Score
    ax4 = axes[1, 1]

    # Calculate composite risk score
    risk_scores = []
    for design in top_designs:
        risk = 0
        # Power risk
        if design['power_margin'] < 0.20:
            risk += abs(design['power_margin'] - 0.20) * 100

        # Communication risk
        if design['comm_snr_db'] < 8:
            risk += abs(design['comm_snr_db'] - 8) * 2

        # Duration risk
        if design['travel_time_years'] > 40:
            risk += (design['travel_time_years'] - 40) * 2

        # Mass risk (too heavy = slower)
        if design['total_mass_g'] > 10:
            risk += (design['total_mass_g'] - 10) * 1

        # Constraint violations
        risk += len(design['violation_details']) * 5

        risk_scores.append(risk)

    colors = ['green' if rs < 30 else 'orange' if rs < 60 else 'red' for rs in risk_scores]
    bars = ax4.bar(design_nums, risk_scores, color=colors, alpha=0.7, edgecolor='black')

    ax4.axhline(y=30, color='green', linestyle='--', linewidth=2, label='Low Risk')
    ax4.axhline(y=60, color='orange', linestyle='--', linewidth=2, label='Medium Risk')

    ax4.set_xlabel('Design Rank', fontsize=10, fontweight='bold')
    ax4.set_ylabel('Composite Risk Score', fontsize=10, fontweight='bold')
    ax4.set_title('Overall Mission Risk', fontsize=12, fontweight='bold')
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(f'{output_dir}/risk_assessment.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved risk assessment plot")

    plt.close()


def generate_detailed_report(results: Dict, output_path: str):
    """Generate detailed text report"""

    with open(output_path, 'w') as f:
        f.write("="*80 + "\n")
        f.write("QUANTUM INTEGRATED SPACECRAFT OPTIMIZATION: DETAILED REPORT\n")
        f.write("="*80 + "\n\n")

        f.write(f"Optimization Date: {results['timestamp']}\n")
        f.write(f"Backend: {results['backend']}\n\n")

        # Mission parameters
        f.write("MISSION PARAMETERS:\n")
        f.write("-" * 80 + "\n")
        mp = results['mission_parameters']
        f.write(f"  Destination: {mp['destination']}\n")
        f.write(f"  Distance: {mp['distance_ly']:.2f} light-years\n")
        f.write(f"  Laser Power: {mp['laser_power_gw']:.0f} GW\n")
        f.write(f"  Sail Area: {mp['sail_area_m2']:.1f} m²\n\n")

        # Sweet spot design
        f.write("="*80 + "\n")
        f.write("RECOMMENDED 'SWEET SPOT' DESIGN\n")
        f.write("="*80 + "\n\n")

        ss = results['sweet_spot']
        f.write(f"Mission Value: {ss['mission_value']:.3f}\n\n")

        f.write("POWER SYSTEM:\n")
        f.write(f"  Solar Array: {ss['solar_area_cm2']:.1f} cm² @ {ss['solar_efficiency']*100:.1f}% efficiency\n")
        f.write(f"  Battery: {ss['battery_capacity_wh']:.2f} Wh\n")
        f.write(f"  Power Margin: {ss['power_margin']*100:+.1f}%\n\n")

        f.write("COMMUNICATION SYSTEM:\n")
        f.write(f"  Type: {ss['comm_type']}\n")
        f.write(f"  Transmit Power: {ss['tx_power_w']:.2f} W\n")
        f.write(f"  TX Aperture: {ss['tx_aperture_m']:.2f} m\n")
        f.write(f"  Modulation Efficiency: {ss['modulation_efficiency']*100:.1f}%\n")
        f.write(f"  SNR: {ss['comm_snr_db']:+.1f} dB\n")
        f.write(f"  Data Rate: {ss['data_rate_bps']/1e6:.2f} Mbps\n\n")

        f.write("SPACECRAFT:\n")
        f.write(f"  Total Mass: {ss['total_mass_g']:.2f} g\n")
        f.write(f"  Structural Mass: {ss['structural_mass_g']:.2f} g\n")
        f.write(f"  Thermal Mass: {ss['thermal_mass_g']:.2f} g\n")
        f.write(f"  Cross-section: {ss['cross_section_m2']*1e6:.1f} mm²\n\n")

        f.write("PERFORMANCE:\n")
        f.write(f"  Final Velocity: {ss['final_velocity_c']:.4f}c ({ss['final_velocity_c']*100:.2f}% speed of light)\n")
        f.write(f"  Travel Time: {ss['travel_time_years']:.1f} years\n")
        f.write(f"  Cost: ${ss['cost_usd']:,.0f}\n\n")

        f.write("CONSTRAINTS:\n")
        if ss['constraints_met']:
            f.write("  ✓ All constraints met\n\n")
        else:
            f.write("  ✗ Constraint violations:\n")
            for constraint, value in ss['violation_details'].items():
                f.write(f"    - {constraint}: {value:.3f} over limit\n")
            f.write("\n")

        # Architecture comparison
        f.write("="*80 + "\n")
        f.write("ARCHITECTURE COMPARISON\n")
        f.write("="*80 + "\n\n")

        for arch_name, arch_designs in results['architectures'].items():
            if arch_designs:
                best = arch_designs[0]
                f.write(f"{arch_name.replace('_', ' ').title()}:\n")
                f.write(f"  Mass: {best['total_mass_g']:.2f} g\n")
                f.write(f"  Velocity: {best['final_velocity_c']:.4f}c\n")
                f.write(f"  Travel Time: {best['travel_time_years']:.1f} years\n")
                f.write(f"  Data Rate: {best['data_rate_bps']/1e6:.2f} Mbps\n")
                f.write(f"  Mission Value: {best['mission_value']:.3f}\n")
                f.write(f"  Constraints Met: {'Yes' if best['constraints_met'] else 'No'}\n\n")

        # Pareto frontier
        f.write("="*80 + "\n")
        f.write("PARETO-OPTIMAL DESIGNS\n")
        f.write("="*80 + "\n\n")

        f.write(f"Found {len(results['pareto_frontier'])} Pareto-optimal designs:\n\n")

        for i, design in enumerate(results['pareto_frontier'][:10], 1):
            f.write(f"#{i}: Velocity={design['final_velocity_c']:.4f}c, "
                   f"Data Rate={design['data_rate_bps']/1e6:.2f} Mbps, "
                   f"Mass={design['total_mass_g']:.1f}g, "
                   f"Value={design['mission_value']:.3f}\n")

        # Statistics
        f.write("\n" + "="*80 + "\n")
        f.write("OPTIMIZATION STATISTICS\n")
        f.write("="*80 + "\n\n")

        all_designs = results['top_50_designs']
        valid_designs = [d for d in all_designs if d['constraints_met']]

        f.write(f"Total designs evaluated: {len(all_designs)}\n")
        f.write(f"Constraint-satisfying designs: {len(valid_designs)}\n")
        f.write(f"Pareto-optimal designs: {len(results['pareto_frontier'])}\n\n")

        # Ranges
        df = pd.DataFrame(all_designs)
        f.write("Design Space Coverage:\n")
        f.write(f"  Mass: {df['total_mass_g'].min():.1f} - {df['total_mass_g'].max():.1f} g\n")
        f.write(f"  Velocity: {df['final_velocity_c'].min():.4f} - {df['final_velocity_c'].max():.4f}c\n")
        f.write(f"  Travel Time: {df['travel_time_years'].min():.1f} - {df['travel_time_years'].max():.1f} years\n")
        f.write(f"  Data Rate: {df['data_rate_bps'].min()/1e6:.2f} - {df['data_rate_bps'].max()/1e6:.2f} Mbps\n")
        f.write(f"  Cost: ${df['cost_usd'].min():,.0f} - ${df['cost_usd'].max():,.0f}\n\n")

        f.write("="*80 + "\n")
        f.write("END OF REPORT\n")
        f.write("="*80 + "\n")

    print(f"✓ Saved detailed report")


def main():
    """Main analysis execution"""

    results_path = "/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/results/quantum_integrated_solutions.json"
    output_dir = "/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/results"

    print("\n" + "="*80)
    print("ANALYZING QUANTUM INTEGRATED OPTIMIZATION RESULTS")
    print("="*80)

    # Load results
    print("\nLoading results...")
    results = load_results(results_path)
    print(f"✓ Loaded {len(results['top_50_designs'])} designs")

    # Create analyses
    print("\nGenerating visualizations...")
    create_comprehensive_analysis(results, output_dir)
    create_sensitivity_analysis(results, output_dir)
    create_risk_assessment(results, output_dir)

    # Generate report
    print("\nGenerating detailed report...")
    report_path = f"{output_dir}/integrated_optimization_report.txt"
    generate_detailed_report(results, report_path)

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nGenerated files:")
    print(f"  1. {output_dir}/integrated_analysis.png")
    print(f"  2. {output_dir}/sensitivity_analysis.png")
    print(f"  3. {output_dir}/risk_assessment.png")
    print(f"  4. {report_path}")


if __name__ == "__main__":
    main()
