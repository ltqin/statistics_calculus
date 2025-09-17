# 双曲函数完整表达式

## 基本定义（指数形式）

| 函数名称 | 数学表达式 |
|:---:|:---|
| **双曲正弦** | $\sinh(x) = \frac{e^x - e^{-x}}{2}$ |
| **双曲余弦** | $\cosh(x) = \frac{e^x + e^{-x}}{2}$ |
| **双曲正切** | $\tanh(x) = \frac{\sinh(x)}{\cosh(x)} = \frac{e^x - e^{-x}}{e^x + e^{-x}}$ |
| **双曲余切** | $\coth(x) = \frac{\cosh(x)}{\sinh(x)} = \frac{e^x + e^{-x}}{e^x - e^{-x}}$ |
| **双曲正割** | $\operatorname{sech}(x) = \frac{1}{\cosh(x)} = \frac{2}{e^x + e^{-x}}$ |
| **双曲余割** | $\operatorname{csch}(x) = \frac{1}{\sinh(x)} = \frac{2}{e^x - e^{-x}}$ |

## 导数公式

| 函数 | 导数 |
|:---:|:---|
| $\sinh(x)$ | $\frac{d}{dx} \sinh(x) = \cosh(x)$ |
| $\cosh(x)$ | $\frac{d}{dx} \cosh(x) = \sinh(x)$ |
| $\tanh(x)$ | $\frac{d}{dx} \tanh(x) = \operatorname{sech}^2(x)$ |
| $\coth(x)$ | $\frac{d}{dx} \coth(x) = -\operatorname{csch}^2(x)$ |
| $\operatorname{sech}(x)$ | $\frac{d}{dx} \operatorname{sech}(x) = -\operatorname{sech}(x)\tanh(x)$ |
| $\operatorname{csch}(x)$ | $\frac{d}{dx} \operatorname{csch}(x) = -\operatorname{csch}(x)\coth(x)$ |

## 积分公式

| 函数 | 积分 |
|:---:|:---|
| $\sinh(x)$ | $\int \sinh(x)  dx = \cosh(x) + C$ |
| $\cosh(x)$ | $\int \cosh(x)  dx = \sinh(x) + C$ |
| $\tanh(x)$ | $\int \tanh(x)  dx = \ln\|\cosh(x)\| + C$ |
| $\coth(x)$ | $\int \coth(x)  dx = \ln\|sinh(x)\| + C$ |
| $\operatorname{sech}(x)$ | $\int \operatorname{sech}(x)  dx = 2\arctan(e^x) + C$ |
| $\operatorname{csch}(x)$ | $\int \operatorname{csch}(x)  dx = \ln\left|\tanh\left(\frac{x}{2}\right)\right| + C$ |

## 重要恒等式

1. $\cosh^2(x) - \sinh^2(x) = 1$
2. $1 - \tanh^2(x) = \operatorname{sech}^2(x)$
3. $\coth^2(x) - 1 = \operatorname{csch}^2(x)$
4. $\sinh(2x) = 2\sinh(x)\cosh(x)$
5. $\cosh(2x) = \cosh^2(x) + \sinh^2(x)$