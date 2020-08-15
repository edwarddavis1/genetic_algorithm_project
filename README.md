## Fun summer project: simulating natural selection.

# Current Progress:
- Have individuals who compete for food, which regenerates in the environment at a set rate, and are given a value for velocity, size and sense region radius.
- Food within a sense region will allow the individual to move straight towards the food.
- Individuals who eat a multiple of 2 food can asexually reproduce, creating an almost identical individual but with random mutations.
- Successful mutations will allow for the individual to reproduce and pass on the genes.
- Over many iterations, can observe evolution of the populations by natural seletion through a live plot of the chromosomes (combination of parameters).
- Can run simulation with graphics to illustrate individuals or without to see the evolution more quickly.
- After the simulation the population over time will be shown with the number of foods in the environment over time.
- Additionally a dataframe with all individuals who lived in the simulation are allocated performance metrics, allowing the user to see which genes were most successful.

# Next Steps:
- Add functionality to record the genetic evolution figures to review why change happened.
- Move from pygame to Unity and re-write code in C# so individuals can live in a 3D environment. 
