import numpy as np
import matplotlib.pyplot as plt

# 模拟参数
mu = 0
se = 1
n_intervals = 20

# 生成20个样本均值（来自正态分布）
sample_means = np.random.normal(mu, se, n_intervals)
# 计算每个样本均值对应的95%置信区间
lower_bounds = sample_means - 1.96*se
upper_bounds = sample_means + 1.96*se

# 绘图
plt.figure(figsize=(10, n_intervals/2))
for i in range(n_intervals):
    # 判断是否覆盖真实均值
    if lower_bounds[i] <= mu <= upper_bounds[i]:
        color = 'blue'
        plt.plot([lower_bounds[i], upper_bounds[i]], [i, i], color=color, lw=2)
        plt.plot(sample_means[i], i, 'o', color=color)
    else:
        color = 'red'
        plt.plot([lower_bounds[i], upper_bounds[i]], [i, i], color=color, lw=2)
        plt.plot(sample_means[i], i, 'o', color=color)

plt.axvline(mu, color='black', linestyle='--', label='True Mean (μ)')
plt.yticks([])
plt.xlabel('Value')
plt.title('Confidence Intervals from Multiple Samples')
plt.legend()
plt.show()