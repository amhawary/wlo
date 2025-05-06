import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv('fitness_metrics.csv')

# Create a figure with subplots for each metric
metrics = ['travel_distance', 'congestion_risk', 'turns', 'clustering', 'utility_access', 'total_fitness']
fig, axes = plt.subplots(len(metrics), 1, figsize=(10, 15))

# Plot each metric
for i, metric in enumerate(metrics):
    ax = axes[i]
    ax.plot(df['Generation'], df[f'{metric}_avg'], 'b-', label='Average')
    ax.plot(df['Generation'], df[f'{metric}_min'], 'g--', label='Min')
    ax.plot(df['Generation'], df[f'{metric}_max'], 'r--', label='Max')
    ax.set_title(f'{metric.replace("_", " ").title()} over Generations')
    ax.set_xlabel('Generation')
    ax.set_ylabel(metric.replace("_", " ").title())
    ax.grid(True)
    ax.legend()

plt.tight_layout()
plt.savefig('fitness_metrics_plot.png')
plt.close() 