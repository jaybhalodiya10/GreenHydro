# -*- coding: utf-8 -*-
"""
Create clear and understandable visualizations of hydrogen cost analysis
"""

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os

def create_clear_visualizations():
    """Create clear and understandable visualizations"""
    
    print("Creating clear and understandable visualizations...")
    
    # Set parameters
    country = "NA"
    weather_year = "2023"
    
    # File paths
    hexagons_path = f'Results/hex_cost_components_{country}_{weather_year}.geojson'
    demand_excel_path = f'Parameters/{country}/demand_parameters.xlsx'
    
    # Load data
    print("Loading data...")
    hexagons = gpd.read_file(hexagons_path)
    demand_parameters = pd.read_excel(demand_excel_path, index_col='Demand center').squeeze("columns")
    demand_centers = demand_parameters.index
    
    # Create Plots directory
    plots_dir = f'Plots/{country}_{weather_year}_clear'
    os.makedirs(plots_dir, exist_ok=True)
    
    # Set style for better readability
    plt.style.use('default')
    sns.set_palette("husl")
    
    # 1. BAR CHART: LCOH Comparison (Trucking vs Pipeline)
    print("Creating LCOH comparison chart...")
    fig, ax = plt.subplots(figsize=(10, 6))
    
    lcoh_data = []
    labels = []
    
    for demand_center in demand_centers:
        for transport_type in ["trucking", "pipeline"]:
            col = f'{demand_center} {transport_type} LCOH'
            if col in hexagons.columns:
                mean_lcoh = hexagons[col].mean()
                lcoh_data.append(mean_lcoh)
                labels.append(f'{demand_center}\n{transport_type.title()}')
    
    bars = ax.bar(labels, lcoh_data, color=['#ff7f0e', '#1f77b4', '#ff7f0e', '#1f77b4'])
    
    # Color coding: Orange for trucking, Blue for pipeline
    for i, bar in enumerate(bars):
        if i % 2 == 0:  # Trucking
            bar.set_color('#ff7f0e')
        else:  # Pipeline
            bar.set_color('#1f77b4')
    
    ax.set_title('Average Hydrogen Cost Comparison\nTrucking vs Pipeline Transport', fontsize=16, fontweight='bold')
    ax.set_ylabel('Levelized Cost of Hydrogen (€/kg H2)', fontsize=12)
    ax.set_ylim(0, max(lcoh_data) * 1.2)
    
    # Add value labels on bars
    for bar, value in zip(bars, lcoh_data):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{value:.2f} €/kg', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{plots_dir}/lcoh_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. PIE CHART: Cost Breakdown by Component
    print("Creating cost breakdown chart...")
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Calculate average costs for one transport type (trucking)
    transport_type = "trucking"
    demand_center = demand_centers[0]
    
    component_costs = {}
    components = ['wind', 'solar', 'electrolyzer', 'battery', 'h2 storage']
    
    for component in components:
        col = f'{demand_center} {transport_type} {component} cost'
        if col in hexagons.columns:
            component_costs[component.title()] = hexagons[col].mean()
    
    if component_costs:
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc']
        wedges, texts, autotexts = ax.pie(component_costs.values(), 
                                         labels=component_costs.keys(),
                                         autopct='%1.1f%%',
                                         colors=colors,
                                         startangle=90)
        
        ax.set_title(f'Cost Breakdown by Component\n{demand_center} - {transport_type.title()} Transport', 
                    fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{plots_dir}/cost_breakdown.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. SIMPLE MAP: Best vs Worst Cost Areas
    print("Creating simple cost map...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Trucking LCOH map
    col_trucking = f'{demand_center} trucking LCOH'
    if col_trucking in hexagons.columns:
        hexagons.plot(column=col_trucking, ax=ax1, 
                     cmap='RdYlBu_r', legend=True,
                     legend_kwds={'label': 'LCOH (€/kg H2)'})
        ax1.set_title(f'{demand_center} - Trucking Transport\n(Red = Expensive, Blue = Cheap)', 
                     fontsize=14, fontweight='bold')
        ax1.axis('off')
    
    # Pipeline LCOH map
    col_pipeline = f'{demand_center} pipeline LCOH'
    if col_pipeline in hexagons.columns:
        hexagons.plot(column=col_pipeline, ax=ax2, 
                     cmap='RdYlBu_r', legend=True,
                     legend_kwds={'label': 'LCOH (€/kg H2)'})
        ax2.set_title(f'{demand_center} - Pipeline Transport\n(Red = Expensive, Blue = Cheap)', 
                     fontsize=14, fontweight='bold')
        ax2.axis('off')
    
    plt.tight_layout()
    plt.savefig(f'{plots_dir}/simple_cost_map.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. SUMMARY TABLE
    print("Creating summary table...")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('tight')
    ax.axis('off')
    
    # Create summary data
    summary_data = []
    for demand_center in demand_centers:
        for transport_type in ["trucking", "pipeline"]:
            col = f'{demand_center} {transport_type} LCOH'
            if col in hexagons.columns:
                lcoh_values = hexagons[col].dropna()
                summary_data.append([
                    demand_center,
                    transport_type.title(),
                    f"{lcoh_values.min():.2f}",
                    f"{lcoh_values.max():.2f}",
                    f"{lcoh_values.mean():.2f}",
                    f"{lcoh_values.median():.2f}"
                ])
    
    # Create table
    table = ax.table(cellText=summary_data,
                    colLabels=['Demand Center', 'Transport', 'Min (€/kg)', 'Max (€/kg)', 
                              'Mean (€/kg)', 'Median (€/kg)'],
                    cellLoc='center',
                    loc='center',
                    colColours=['#f0f0f0']*6)
    
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.5)
    
    ax.set_title('Hydrogen Cost Summary - Namibia 2023', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(f'{plots_dir}/cost_summary_table.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 5. COST SAVINGS CHART
    print("Creating cost savings chart...")
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if col_trucking in hexagons.columns and col_pipeline in hexagons.columns:
        cost_savings = hexagons[col_trucking] - hexagons[col_pipeline]
        
        # Create histogram of cost savings
        ax.hist(cost_savings.dropna(), bins=30, color='lightblue', edgecolor='black', alpha=0.7)
        ax.axvline(cost_savings.mean(), color='red', linestyle='--', linewidth=2, 
                  label=f'Mean Savings: {cost_savings.mean():.2f} €/kg')
        
        ax.set_title('Cost Savings: Pipeline vs Trucking Transport', fontsize=16, fontweight='bold')
        ax.set_xlabel('Cost Savings (€/kg H2)\nPositive = Pipeline cheaper, Negative = Trucking cheaper', fontsize=12)
        ax.set_ylabel('Number of Locations', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{plots_dir}/cost_savings_histogram.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n🎉 All clear visualizations completed!")
    print(f"📁 Results saved in: {plots_dir}")
    print("\nGenerated charts:")
    print("1. LCOH Comparison Bar Chart")
    print("2. Cost Breakdown Pie Chart") 
    print("3. Simple Cost Map (Red=Expensive, Blue=Cheap)")
    print("4. Cost Summary Table")
    print("5. Cost Savings Histogram")
    
    return plots_dir

if __name__ == "__main__":
    create_clear_visualizations() 