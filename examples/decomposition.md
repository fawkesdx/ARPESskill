# Example: decomposition (PCA / NMF / ICA)

Follow `reference/decomposition.md`.

```python
from arpes.analysis.decomposition import (
    pca_along, nmf_along, ica_along, factor_analysis_along,
)

# Observation axes = what varies between "samples" (often spatial)
# transformed, model = pca_along(spectrum, ["x", "y"], n_components=5)

# NMF — non-negative data only
# transformed, model = nmf_along(spectrum, ["x", "y"], n_components=4)

# ICA / factor analysis
# transformed, model = ica_along(spectrum, ["x", "y"], n_components=4)
# transformed, model = factor_analysis_along(spectrum, ["x", "y"], n_components=4)

# Save component maps; pca_explorer only if asked
# Mask with component threshold → masks.md
```

**Report:** method; axes; n_components; correlation if used.
