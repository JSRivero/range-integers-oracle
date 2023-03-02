import pandas as pd

import matplotlib.pyplot as plt


df = pd.read_csv('depth_data/depths_intervals_two_methods_3-12_qubits.csv')


fig, ax = plt.subplots(1, 1, figsize=(14,9))

x = df.index.tolist()
y_oracle = df['mean_oracles'].values
std_oracle = df['std_oracles'].values
y_addition = df['mean_addition'].values
std_addition = df['std_addition'].values

# Area parameters
alpha = 0.25

#  mean +- std parameters
alpha_std = 1
linewidth_std = 1.5
linestyle_A = (0, (5, 10))
linestyle_B = (0, (3, 5, 1, 5, 1, 5))

ax.scatter(x, y_oracle, marker='^', s=50, facecolor='tomato', label='Mean Depth Implementation A', zorder=4)
ax.plot(x, y_oracle, c='tomato', zorder=5)
ax.plot(x, y_oracle-std_oracle, c='tomato', zorder=4, alpha=alpha_std, linestyle = linestyle_A, linewidth=linewidth_std)
ax.plot(x, y_oracle+std_oracle, c='tomato', zorder=4, alpha=alpha_std, linestyle = linestyle_A, linewidth=linewidth_std, label='Std Depth Implementation A')
ax.fill_between(x, y1=y_oracle-std_oracle, y2=y_oracle+std_oracle, facecolor='tomato', alpha=alpha,
            zorder = 3)

ax.scatter(x, y_addition, marker='o', s=50, facecolor='royalblue', label='Mean Depth Implementation B', zorder=4)
ax.plot(x, y_addition, c='royalblue', zorder=5)
ax.plot(x, y_addition-std_addition, c='royalblue', zorder=4, alpha=alpha_std, linestyle = linestyle_B, linewidth=linewidth_std)
ax.plot(x, y_addition+std_addition, c='royalblue', zorder=4, alpha=alpha_std, linestyle = linestyle_B, linewidth=linewidth_std, label='Std Depth Implementation B')
ax.fill_between(x, y1=y_addition-std_addition, y2=y_addition+std_addition, facecolor='royalblue', alpha=alpha,
            zorder = 3)

ax.grid(True, zorder=0)

fontsize = 15

# ax.set_title('Comparison between methods', fontsize=fontsize+2)

ax.set_xticks(list(range(10)))
ax.set_xticklabels(list(range(3,13)))

ax.set_xlabel('Number of qubits',fontsize=fontsize)
ax.set_ylabel('Depth',fontsize=fontsize)

ax.legend(fontsize=fontsize)

ax.tick_params(labelsize=fontsize-1)

plt.show()