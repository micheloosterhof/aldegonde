#!/usr/bin/env python3
"""Singapore COE Analysis - Category B prices, supply/demand, and market outlook."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from datetime import datetime

# ============================================================
# DATA: Category B COE prices (S$) from 2023 to Mar 2026
# ============================================================
coe_data = [
    # 2023
    ("Jan 23 1st", 114689),
    ("Jan 23 2nd", 112001),
    ("Feb 23 1st", 112000),
    ("Feb 23 2nd", 110001),
    ("Mar 23 1st", 111000),
    ("Mar 23 2nd", 110001),
    ("Apr 23 1st", 112001),
    ("Apr 23 2nd", 113001),
    ("May 23 1st", 116001),
    ("May 23 2nd", 120889),
    ("Jun 23 1st", 121001),
    ("Jun 23 2nd", 122001),
    ("Jul 23 1st", 125001),
    ("Jul 23 2nd", 128001),
    ("Aug 23 1st", 130001),
    ("Aug 23 2nd", 131889),
    ("Sep 23 1st", 135889),
    ("Sep 23 2nd", 140889),
    ("Oct 23 1st", 146002),
    ("Oct 23 2nd", 150001),
    ("Nov 23 1st", 155001),
    ("Nov 23 2nd", 148889),
    ("Dec 23 1st", 145001),
    ("Dec 23 2nd", 150001),
    # 2024
    ("Jan 24 1st", 140001),
    ("Jan 24 2nd", 135001),
    ("Feb 24 1st", 130001),
    ("Feb 24 2nd", 126001),
    ("Mar 24 1st", 120001),
    ("Mar 24 2nd", 115889),
    ("Apr 24 1st", 112001),
    ("Apr 24 2nd", 110001),
    ("May 24 1st", 108001),
    ("May 24 2nd", 105001),
    ("Jun 24 1st", 102001),
    ("Jun 24 2nd", 100889),
    ("Jul 24 1st", 99001),
    ("Jul 24 2nd", 97001),
    ("Aug 24 1st", 98001),
    ("Aug 24 2nd", 100001),
    ("Sep 24 1st", 106890),
    ("Sep 24 2nd", 110001),
    ("Oct 24 1st", 116002),
    ("Oct 24 2nd", 113890),
    ("Nov 24 1st", 118001),
    ("Nov 24 2nd", 125001),
    ("Dec 24 1st", 130001),
    ("Dec 24 2nd", 135001),
    # 2025
    ("Jan 25 1st", 121501),
    ("Jan 25 2nd", 125001),
    ("Feb 25 1st", 128001),
    ("Feb 25 2nd", 132001),
    ("Mar 25 1st", 135001),
    ("Mar 25 2nd", 138001),
    ("Apr 25 1st", 117899),
    ("Apr 25 2nd", 117003),
    ("May 25 1st", 120001),
    ("May 25 2nd", 122001),
    ("Jun 25 1st", 125001),
    ("Jun 25 2nd", 128001),
    ("Jul 25 1st", 130001),
    ("Jul 25 2nd", 133001),
    ("Aug 25 1st", 135001),
    ("Aug 25 2nd", 136890),
    ("Sep 25 1st", 138001),
    ("Sep 25 2nd", 136890),
    ("Oct 25 1st", 141000),
    ("Oct 25 2nd", 138001),
    ("Nov 25 1st", 115001),
    ("Nov 25 2nd", 129890),
    ("Dec 25 1st", 125001),
    ("Dec 25 2nd", 122001),
    # 2026
    ("Jan 26 1st", 119100),
    ("Jan 26 2nd", 121634),
    ("Feb 26 1st", 110890),
    ("Feb 26 2nd", 105001),
    ("Mar 26 1st", 114002),
]

labels = [d[0] for d in coe_data]
prices = [d[1] for d in coe_data]

# ============================================================
# FIGURE 1: COE Category B Price Trend (2023-2026)
# ============================================================
fig1, ax1 = plt.subplots(figsize=(18, 8))

x = np.arange(len(prices))
ax1.plot(x, [p/1000 for p in prices], 'b-o', markersize=3, linewidth=1.5, label='Cat B Premium')

# Moving average (6-period)
window = 6
ma = np.convolve([p/1000 for p in prices], np.ones(window)/window, mode='valid')
ax1.plot(x[window-1:], ma, 'r-', linewidth=2.5, label=f'{window}-period Moving Avg')

# Highlight key zones
ax1.axhspan(95, 110, alpha=0.1, color='green', label='Buyer-friendly zone')
ax1.axhspan(135, 160, alpha=0.1, color='red', label='Overheated zone')

# Mark current price
ax1.annotate(f'Current:\nS${prices[-1]:,}',
             xy=(len(prices)-1, prices[-1]/1000),
             xytext=(len(prices)-6, prices[-1]/1000 + 12),
             arrowprops=dict(arrowstyle='->', color='darkgreen'),
             fontsize=11, fontweight='bold', color='darkgreen',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow'))

# Mark all-time high in this period
max_idx = prices.index(max(prices))
ax1.annotate(f'Peak:\nS${prices[max_idx]:,}',
             xy=(max_idx, prices[max_idx]/1000),
             xytext=(max_idx-8, prices[max_idx]/1000 + 5),
             arrowprops=dict(arrowstyle='->', color='red'),
             fontsize=10, color='red')

# Mark trough
min_idx = prices.index(min(prices))
ax1.annotate(f'Trough:\nS${prices[min_idx]:,}',
             xy=(min_idx, prices[min_idx]/1000),
             xytext=(min_idx+3, prices[min_idx]/1000 - 8),
             arrowprops=dict(arrowstyle='->', color='blue'),
             fontsize=10, color='blue')

# Year dividers
for year_start_label, year_name in [("Jan 24 1st", "2024"), ("Jan 25 1st", "2025"), ("Jan 26 1st", "2026")]:
    idx = labels.index(year_start_label)
    ax1.axvline(x=idx, color='gray', linestyle='--', alpha=0.5)
    ax1.text(idx+1, max(prices)/1000 + 3, year_name, fontsize=12, fontweight='bold', color='gray')

ax1.set_xlabel('Bidding Exercise', fontsize=12)
ax1.set_ylabel('COE Premium (S$ thousands)', fontsize=12)
ax1.set_title('Singapore COE Category B Price Trend (2023-2026)\nCars >1600cc / >97kW', fontsize=14, fontweight='bold')
ax1.set_xticks(x[::4])
ax1.set_xticklabels([labels[i] for i in range(0, len(labels), 4)], rotation=45, ha='right', fontsize=8)
ax1.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%dk'))
ax1.legend(loc='upper left', fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_ylim(85, 165)

plt.tight_layout()
fig1.savefig('/home/user/aldegonde/coe_price_trend.png', dpi=150)
print("Saved: coe_price_trend.png")

# ============================================================
# FIGURE 2: Supply vs Demand + Price
# ============================================================
# Quarterly COE quota data (Cat B approximate)
supply_demand_data = [
    # (Quarter, Cat B Quota/month, Bids/month approx, Avg Price)
    ("Q1 2023", 700, 1050, 112000),
    ("Q2 2023", 720, 1100, 118000),
    ("Q3 2023", 710, 1200, 132000),
    ("Q4 2023", 690, 1250, 150000),
    ("Q1 2024", 730, 1150, 132000),
    ("Q2 2024", 750, 1050, 108000),
    ("Q3 2024", 780, 1000, 99000),
    ("Q4 2024", 790, 1100, 120000),
    ("Q1 2025", 800, 1150, 128000),
    ("Q2 2025", 810, 1100, 118000),
    ("Q3 2025", 830, 1200, 135000),
    ("Q4 2025", 850, 1100, 122000),
    ("Q1 2026", 815, 1261, 114000),
    ("Q2 2026*", 860, 1100, None),  # Forecast
    ("Q3 2026*", 900, 1050, None),  # Forecast
    ("Q4 2026*", 920, 1000, None),  # Forecast
]

fig2, (ax2a, ax2b) = plt.subplots(2, 1, figsize=(14, 12))

quarters = [d[0] for d in supply_demand_data]
supply = [d[1] for d in supply_demand_data]
demand = [d[2] for d in supply_demand_data]
avg_prices = [d[3] for d in supply_demand_data]

x2 = np.arange(len(quarters))
width = 0.35

bars1 = ax2a.bar(x2 - width/2, supply, width, label='COE Quota (Supply/month)', color='steelblue', alpha=0.8)
bars2 = ax2a.bar(x2 + width/2, demand, width, label='Bids (Demand/month)', color='coral', alpha=0.8)

# Forecast shading
forecast_start = 12
ax2a.axvspan(forecast_start - 0.5, len(quarters) - 0.5, alpha=0.1, color='yellow')
ax2a.text(forecast_start + 1, max(demand) + 30, 'FORECAST', fontsize=12, fontweight='bold',
          color='orange', ha='center', style='italic')

# Demand/Supply ratio line
ratio = [d/s for s, d in zip(supply, demand)]
ax2a_twin = ax2a.twinx()
ax2a_twin.plot(x2, ratio, 'g-s', markersize=6, linewidth=2, label='Demand/Supply Ratio')
ax2a_twin.axhline(y=1.0, color='green', linestyle=':', alpha=0.5)
ax2a_twin.set_ylabel('Demand/Supply Ratio', color='green', fontsize=11)
ax2a_twin.tick_params(axis='y', labelcolor='green')
ax2a_twin.set_ylim(0.8, 2.0)

ax2a.set_xlabel('Quarter', fontsize=11)
ax2a.set_ylabel('Number of COEs / Bids per month', fontsize=11)
ax2a.set_title('COE Category B: Supply vs Demand', fontsize=14, fontweight='bold')
ax2a.set_xticks(x2)
ax2a.set_xticklabels(quarters, rotation=45, ha='right', fontsize=9)
ax2a.legend(loc='upper left', fontsize=10)
ax2a_twin.legend(loc='upper right', fontsize=10)
ax2a.grid(True, alpha=0.3, axis='y')

# Price chart with forecast
actual_prices = [p for p in avg_prices if p is not None]
forecast_prices = [114000, 108000, 100000, 95000]  # Predicted decline
all_prices_plot = actual_prices + forecast_prices[1:]

ax2b.plot(range(len(actual_prices)), [p/1000 for p in actual_prices], 'b-o',
          markersize=6, linewidth=2, label='Actual Avg Price')
ax2b.plot(range(len(actual_prices)-1, len(all_prices_plot)),
          [p/1000 for p in [actual_prices[-1]] + forecast_prices[1:]],
          'r--s', markersize=6, linewidth=2, label='Forecast Price')

ax2b.axvspan(len(actual_prices) - 0.5, len(all_prices_plot) - 0.5, alpha=0.1, color='yellow')

# Best buy window
ax2b.axvspan(13.5, 15.5, alpha=0.2, color='green')
ax2b.text(14.5, 92, 'BEST BUY\nWINDOW', fontsize=11, fontweight='bold',
          color='darkgreen', ha='center')

ax2b.set_xlabel('Quarter', fontsize=11)
ax2b.set_ylabel('Avg COE Premium (S$ thousands)', fontsize=11)
ax2b.set_title('COE Category B: Price Trend & Forecast', fontsize=14, fontweight='bold')
ax2b.set_xticks(range(len(quarters)))
ax2b.set_xticklabels(quarters, rotation=45, ha='right', fontsize=9)
ax2b.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%dk'))
ax2b.legend(fontsize=10)
ax2b.grid(True, alpha=0.3)
ax2b.set_ylim(85, 160)

plt.tight_layout()
fig2.savefig('/home/user/aldegonde/coe_supply_demand.png', dpi=150)
print("Saved: coe_supply_demand.png")

# ============================================================
# FIGURE 3: Petrol vs Hybrid vs EV - Total Cost of Ownership
# ============================================================
fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(16, 8))

# --- 10-Year TCO Comparison (SUV segment) ---
categories = ['Purchase\n(after rebates)', 'COE\n(Cat B)', 'Fuel/Energy\n(10yr)', 'Road Tax\n(10yr)',
               'Insurance\n(10yr)', 'Maintenance\n(10yr)']

# Approximate costs for SUV segment in Singapore (S$)
petrol_costs = [85000, 114000, 28000, 8000, 18000, 15000]
hybrid_costs = [90000, 114000, 18000, 9000, 20000, 12000]
ev_costs =     [75000, 114000, 10000, 14000, 24000, 8000]  # After ~S$30k rebates

x3 = np.arange(len(categories))
w = 0.25

ax3a.bar(x3 - w, [c/1000 for c in petrol_costs], w, label='Petrol SUV', color='gray', alpha=0.8)
ax3a.bar(x3, [c/1000 for c in hybrid_costs], w, label='Hybrid SUV', color='skyblue', alpha=0.8)
ax3a.bar(x3 + w, [c/1000 for c in ev_costs], w, label='Electric SUV', color='limegreen', alpha=0.8)

ax3a.set_ylabel('Cost (S$ thousands)', fontsize=11)
ax3a.set_title('Cost Breakdown by Category\n(SUV Segment, 10-Year Ownership)', fontsize=13, fontweight='bold')
ax3a.set_xticks(x3)
ax3a.set_xticklabels(categories, fontsize=9)
ax3a.legend(fontsize=10)
ax3a.grid(True, alpha=0.3, axis='y')
ax3a.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%dk'))

# --- Total TCO bar chart ---
total_petrol = sum(petrol_costs)
total_hybrid = sum(hybrid_costs)
total_ev = sum(ev_costs)

bars = ax3b.barh(['Electric SUV\n(with rebates)', 'Hybrid SUV', 'Petrol SUV'],
                  [total_ev/1000, total_hybrid/1000, total_petrol/1000],
                  color=['limegreen', 'skyblue', 'gray'], alpha=0.8, height=0.5)

for bar, total in zip(bars, [total_ev, total_hybrid, total_petrol]):
    ax3b.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
              f'S${total:,.0f}', va='center', fontsize=12, fontweight='bold')

savings_vs_petrol_ev = total_petrol - total_ev
savings_vs_petrol_hy = total_petrol - total_hybrid
ax3b.text(total_ev/1000/2, 0, f'Save S${savings_vs_petrol_ev:,}\nvs petrol',
          ha='center', va='center', fontsize=10, color='darkgreen', fontweight='bold')
ax3b.text(total_hybrid/1000/2, 1, f'Save S${savings_vs_petrol_hy:,}\nvs petrol',
          ha='center', va='center', fontsize=10, color='darkblue', fontweight='bold')

ax3b.set_xlabel('Total 10-Year Cost of Ownership (S$ thousands)', fontsize=11)
ax3b.set_title('Total Cost of Ownership Comparison\n(10 Years, SUV Segment)', fontsize=13, fontweight='bold')
ax3b.xaxis.set_major_formatter(mticker.FormatStrFormatter('$%dk'))
ax3b.set_xlim(0, 320)
ax3b.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
fig3.savefig('/home/user/aldegonde/tco_comparison.png', dpi=150)
print("Saved: tco_comparison.png")

# ============================================================
# FIGURE 4: COE Renewal vs New Car Decision Matrix
# ============================================================
fig4, ax4 = plt.subplots(figsize=(14, 8))

# Scenario comparison for Subaru Forester owner with 1 year COE left
scenarios = {
    'Renew COE\n5 years\n(50% PQP)': {
        'upfront': 57000,  # ~50% of PQP (~S$114k)
        'maintenance_5yr': 8000,
        'road_tax_surcharge': 3000,
        'insurance_premium': 2000,
        'fuel_5yr': 14000,
        'total': 84000,
    },
    'Renew COE\n10 years\n(100% PQP)': {
        'upfront': 114000,  # Full PQP
        'maintenance_10yr': 20000,
        'road_tax_surcharge': 8000,
        'insurance_premium': 5000,
        'fuel_10yr': 28000,
        'total': 175000,
    },
    'New Petrol\nSUV': {
        'upfront': 199000,  # OMV + COE + dealer
        'maintenance_10yr': 15000,
        'road_tax': 8000,
        'insurance': 18000,
        'fuel_10yr': 28000,
        'total': 268000,
    },
    'New Hybrid\nSUV': {
        'upfront': 204000,
        'maintenance_10yr': 12000,
        'road_tax': 9000,
        'insurance': 20000,
        'fuel_10yr': 18000,
        'total': 263000,
    },
    'New Electric\nSUV': {
        'upfront': 189000,  # After rebates
        'maintenance_10yr': 8000,
        'road_tax': 14000,
        'insurance': 24000,
        'fuel_10yr': 10000,
        'total': 245000,
    },
}

scenario_names = list(scenarios.keys())
totals = [scenarios[s]['total']/1000 for s in scenario_names]
colors = ['#FFD700', '#FFA500', 'gray', 'skyblue', 'limegreen']

bars = ax4.bar(scenario_names, totals, color=colors, alpha=0.85, width=0.6,
               edgecolor='black', linewidth=0.5)

for bar, total, name in zip(bars, totals, scenario_names):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
             f'S${total:.0f}k', ha='center', fontsize=12, fontweight='bold')

# Add value indicator
ax4.annotate('CHEAPEST\nOPTION', xy=(0, totals[0]),
             xytext=(0.5, totals[0] + 30),
             arrowprops=dict(arrowstyle='->', color='darkgreen', lw=2),
             fontsize=12, fontweight='bold', color='darkgreen', ha='center')

ax4.annotate('BEST LONG-TERM\nVALUE (new car)', xy=(4, totals[4]),
             xytext=(3.5, totals[4] + 30),
             arrowprops=dict(arrowstyle='->', color='green', lw=2),
             fontsize=11, fontweight='bold', color='green', ha='center')

ax4.set_ylabel('Total Cost (S$ thousands)', fontsize=12)
ax4.set_title('Decision Matrix: Renew COE vs Buy New Car\n(Subaru Forester Owner, Cat B, 2026)', fontsize=14, fontweight='bold')
ax4.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%dk'))
ax4.grid(True, alpha=0.3, axis='y')
ax4.set_ylim(0, 320)

# Add footnotes
ax4.text(0.02, 0.02,
         'Note: 5-yr renewal = non-renewable, car must be scrapped after.\n'
         '10-yr renewal costs include higher maintenance & road tax surcharges for older vehicles.\n'
         'New car prices are approximate all-in (COE + ARF + dealer) for mid-range SUV segment.\n'
         'EV prices reflect S$30k EEAI+VES rebates available in 2026.',
         transform=ax4.transAxes, fontsize=8, verticalalignment='bottom',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

plt.tight_layout()
fig4.savefig('/home/user/aldegonde/decision_matrix.png', dpi=150)
print("Saved: decision_matrix.png")

print("\n=== ALL CHARTS GENERATED ===")
