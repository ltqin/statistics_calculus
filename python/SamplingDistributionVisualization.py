import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# 参数
mu = 0
se = 1
x = np.linspace(mu - 4*se, mu + 4*se, 100)
y = norm.pdf(x, mu, se)

# 绘图
plt.figure(figsize=(10,6))
plt.plot(x, y, 'b-')
plt.vlines([mu - 1.96*se, mu + 1.96*se], ymin=0, ymax=0.4, colors='r', linestyles='dashed')
plt.fill_between(x, y, where=(x >= mu-1.96*se) & (x <= mu+1.96*se), color='grey', alpha=0.3)
plt.text(mu, 0.1, '95%', ha='center', fontsize=15)
plt.title('Sampling Distribution of Sample Mean')
plt.xlabel('Sample Mean (x̄)')
plt.ylabel('Density')
plt.show()