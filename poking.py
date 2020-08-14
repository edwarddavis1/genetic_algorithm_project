import matplotlib
import matplotlib.pyplot as plt

# Create colourmap limits
norm = matplotlib.colors.LogNorm(
    vmin=0.0001, vmax=100000)
# Create colourmap
mapper = plt.cm.ScalarMappable(cmap='rainbow', norm=norm)
mapper.to_rgba()
