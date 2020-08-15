import matplotlib
import matplotlib.pyplot as plt
import numpy as np

norm = matplotlib.colors.Normalize(
    vmin=0.0001, vmax=20)
# Create colourmap
mapper = plt.cm.ScalarMappable(cmap='seismic', norm=norm)

x = np.linspace(0.0001, 0.1)
y = [1] * len(x)
c = [mapper.to_rgba(v) for v in x]

plt.scatter(x, y, color=c)
