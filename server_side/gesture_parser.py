# video-game joystick!
# FROM GPT

import matplotlib.pyplot as plt
import numpy as np

# Set up the data for the line
r = [1, 2, 3, 4, 5, 4, 3, 2]
theta = [0, 45, 90, 135, 180, 225, 270, 315]
deg_theta = [np.deg2rad(i) for i in theta]

# Convert the polar coordinates to Cartesian coordinates
x = r * np.cos(np.deg2rad(theta))
y = r * np.sin(np.deg2rad(theta))

# Fit a curve to the Cartesian coordinates using a polynomial fit
coeffs = np.polyfit(x, y, 3)

# Calculate the first and second derivatives of the fitted curve
deriv1 = np.polyder(coeffs, 1)
deriv2 = np.polyder(coeffs, 2)

# Calculate the curvature at each point
curvature = (deriv1[0] * deriv2[1] - deriv1[1] * deriv2[0]) / (deriv1[0] ** 2 + deriv1[1] ** 2) ** 1.5

# Set up a polar subplot
ax = plt.subplot(111, projection='polar')

# Set the labels and plot the line and the curvature
ax.set_theta_zero_location('N')
ax.set_thetagrids(range(0, 360, 45), labels=["flex", "flex-abd", "abd", "ext-abd", "ext", "ext-add", "add", "flex-add"])
ax.plot(deg_theta, r, label='Line')
#ax.plot(theta, curvature, label='Curvature')
ax.legend()

# Show the plot
plt.show()
