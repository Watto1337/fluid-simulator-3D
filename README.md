# Fluid-Simulator-3D

This is a three dimensional fluid simulator I programmed in Python. It uses hundreds of particles and calculates collisions between them. Variable coefficients are used to make the particles interact in a more fluid manner.

The program tracks the exact position of the particles as well as their position in a grid. The grid's cells are the same size as the particles, which makes it much faster to check for collisions, since it only needs to check adjacent cells.
