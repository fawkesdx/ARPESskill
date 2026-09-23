# Example: curvature + minimum gradient

Follow `reference/band-enhance.md`. Needs a 2D cut.

```python
from arpes.analysis.derivative import curvature, minimum_gradient
import matplotlib.pyplot as plt

# cut2d = data.sel(...)  # 2D: eV × angle or eV × k
# c = curvature(cut2d)
# g = minimum_gradient(cut2d)

# fig, axes = plt.subplots(1, 3, figsize=(10, 3))
# cut2d.plot(ax=axes[0]); axes[0].set_title("I")
# c.plot(ax=axes[1]); axes[1].set_title("curvature")
# g.plot(ax=axes[2]); axes[2].set_title("min gradient")
# # save under analysis/
```

**Report:** derived maps (not intensity); package defaults unless `alpha`/`delta`
stated; no peak/EF claims from these alone.
