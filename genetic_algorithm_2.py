import numpy as np
import pygame
import math
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
import seaborn as sns

sns.set(style="whitegrid")
sns.set_context("paper")

%matplotlib qt


def is_item_in_sense_region(x_pos, y_pos, item_x_pos, item_y_pos, radius):
    """Checks is something is within an individual's sense region
    """
    if (x_pos - item_x_pos)**2 + (y_pos - item_y_pos)**2 < radius**2:
        return True
    else:
        return False


def get_lifetime(energy_use):
    """Calculates the lifetime of an individual based on its energy use
    """
    constant = 67.5E6
    lifetime = int(round(constant / energy_use))
    return lifetime


def get_energy_use(ind):
    """Calculates the energy use of an individual based on chromosome
    """
    energy_use = 0.5 * ind.size**3 * ind.velocity**2
    return energy_use


class individual:
    def __init__(self, velocity, size, sense_region_radius, pop, name):

        # World
        self.pop = pop
        self.current_theta = np.random.uniform(0, 2 * np.pi)
        self.x_max = pop.win_x
        self.y_max = pop.win_y
        self.x_min = 0
        self.y_min = 0
        self.food_x_pos = [f.x_pos for f in pop.foods]
        self.food_y_pos = [f.y_pos for f in pop.foods]

        # Genetic Parameters
        self.velocity = velocity
        self.size = size
        self.sense_region_radius = sense_region_radius
        self.energy_use = get_energy_use(self)
        self.chromosome = [self.velocity, self.size, self.sense_region_radius]

        # Non-genetic Descriptors
        self.name = name
        self.init_lifetime = get_lifetime(self.energy_use)
        self.x_pos = np.random.uniform(0, pop.win_x)
        self.y_pos = np.random.uniform(0, pop.win_y)
        self.x_size = size
        self.y_size = size
        self.dying_time = 200
        self.colour = (0, 0, 255)

        # Ongoing performance
        self.time_lived = 0
        self.alive = True
        self.foods_eaten = 0
        self.replications = 0
        self.life_remaining = self.init_lifetime

        # print("%s created" % self.name)

        # Plot traits for population tracking
        # Set up colour map
        norm = matplotlib.colors.Normalize(
            vmin=0.0001, vmax=2 * pop.init_velocity * pop.speed_up)
        # Create colourmap
        mapper = plt.cm.ScalarMappable(cmap='gnuplot', norm=norm)
        pop.live_ax.scatter(self.velocity, self.size, self.sense_region_radius,
                            color=mapper.to_rgba(self.velocity))
        pop.live_fig.canvas.draw()

    def __del__(self):
        pop.add_individual_to_data(self)
        # print("%s died" % self.name)

    def update_position(self):
        """Steps the individual in a somewhat random direction
        """
        # Move towards food if within sense region
        move_randomly = True
        for food_piece in pop.foods:
            food_in_sense_region = is_item_in_sense_region(
                self.x_pos, self.y_pos,
                food_piece.x_pos, food_piece.y_pos,
                self.sense_region_radius)
            if food_in_sense_region:
                move_randomly = False
                # Calculate distance to food
                radians_to_food = math.atan2(self.y_pos - food_piece.y_pos,
                                             self.x_pos - food_piece.x_pos)
                distance_to_food = math.hypot(self.x_pos - food_piece.x_pos,
                                              self.y_pos - food_piece.y_pos)
                distance_to_food = int(distance_to_food)

                # Eata the food once upon it
                if distance_to_food == 0 and not food_piece.eaten:
                    food_piece.eat()
                    self.foods_eaten += 1
                    self.life_remaining += food_piece.extra_life_time

                # Otherwise move directly towards food
                else:
                    if distance_to_food > self.velocity:
                        x_update = -math.cos(radians_to_food) * \
                            self.velocity
                        y_update = -math.sin(radians_to_food) * \
                            self.velocity
                    else:
                        x_update = -math.cos(radians_to_food) * \
                            distance_to_food
                        y_update = -math.sin(radians_to_food) * \
                            distance_to_food

                    self.x_pos += x_update
                    self.y_pos += y_update

                break

        if move_randomly:
            self.current_theta = np.random.uniform(
                self.current_theta - np.pi / 4, self.current_theta + np.pi / 4)
            x = np.sin(self.current_theta)
            y = np.cos(self.current_theta)
            x_update, y_update = np.multiply((x, y), self.velocity)

            # Stop individual going off screen by reversing direction
            if self.x_pos + x_update >= self.x_max or self.x_pos + x_update < self.x_min:
                x_update *= -1
            if self.y_pos + y_update >= self.y_max or self.y_pos + y_update < self.y_min:
                y_update *= -1

            self.x_pos += x_update
            self.y_pos += y_update

    def replicate(self):
        """Replicates the current individual with mutations from parent
        """
        mutated_velocity = np.random.normal(self.velocity, 1 / 3)
        mutated_size = np.random.normal(self.size, 10 / 3)
        mutated_sense_region_radius = np.random.normal(
            self.sense_region_radius, 100 / 3)
        new_ind = individual(mutated_velocity, mutated_size,
                             mutated_sense_region_radius,
                             self.pop, "%s copy" % self.name)
        new_ind.x_pos = self.x_pos
        new_ind.y_pos = self.y_pos
        pop.individuals.append(new_ind)
        pop.pop_size += 1

    def step(self):
        """Updates the properties of the individual for a step
        """
        self.time_lived += 1
        if self.time_lived < self.life_remaining:
            # Keep moving while alive
            self.update_position()

            # Replicate individual for every two foods it eats
            if self.foods_eaten % 2 == 0 and self.foods_eaten / 2 != self.replications:
                self.replicate()
                self.replications += 1

            # Colour change
            red_colour = np.linspace(255, 0, 5000)
            life_remaining = self.life_remaining - self.time_lived
            if life_remaining < 5000:
                self.colour = (red_colour[life_remaining], 0, 255)
            else:
                self.colour = (0, 0, 255)

        elif self.time_lived <= self.life_remaining + self.dying_time:
            # If dying change colour to red
            self.colour = (255, 0, 0)
        else:
            self.alive = False


class food:
    def __init__(self, pop):
        self.extra_life_time = 2000
        self.colour = (0, 255, 0)
        self.x_size = 10
        self.y_size = 10
        self.x_pos = np.random.uniform(0, pop.win_x)
        self.y_pos = np.random.uniform(0, pop.win_y)
        self.eaten = False

    def eat(self):
        self.eaten = True


class population:
    def __init__(self, pop_size, food_number, food_regen):
        self.pop_size = pop_size
        self.win_x = 800
        self.win_y = 800
        self.food_number = food_number
        self.food_regen = food_regen
        self.individuals = []
        self.foods = []
        self.speed_up = 1
        self.init_velocity = 1
        self.macro_pop_data = pd.DataFrame()
        self.frame_data = []
        self.pop_size_data = []
        self.food_number_data = []
        self.individual_data = pd.DataFrame()
        self.dead_individuals = 0
        self.past_individual_data = pd.DataFrame()
        column_titles = ['Individual', 'Alive at End', 'Time Lived',
                         'Food Eaten', 'Replications', 'Size', 'Velocity', 'Sense']
        self.past_individual_data = self.past_individual_data.reindex(
            columns=column_titles)
        self.colour_for_plots = (0, 0, 0, 0)

    def add_individual_to_data(self, ind):
        """Once an individual dies, add its genes and performance to dataframe
        """
        new_row = {'Individual': ind.name,
                   'Alive at End': ind.alive,
                   'Time Lived': ind.time_lived,
                   'Food Eaten': ind.foods_eaten,
                   'Replications': ind.replications,
                   'Size': ind.size, 'Velocity': ind.velocity,
                   'Sense': ind.sense_region_radius}
        self.past_individual_data = self.past_individual_data.append(
            new_row, ignore_index=True)

    def replot(self):
        """Replots the live 3D plot of genes after an individual dies
        """
        pop.live_ax.clear()

        # Set up colour map
        norm = matplotlib.colors.Normalize(
            vmin=0.0001, vmax=2 * self.init_velocity * self.speed_up)
        # Create colourmap
        mapper = plt.cm.ScalarMappable(cmap='gnuplot', norm=norm)

        for ind in self.individuals:
            pop.live_ax.scatter(ind.velocity, ind.size, ind.sense_region_radius,
                                color=mapper.to_rgba(ind.velocity))
        self.live_ax.set_xlabel("Velocity")
        self.live_ax.set_ylabel("Size")
        self.live_ax.set_zlabel("Sense Region Radius")
        pop.live_fig.canvas.draw()

    def simulate(self, graphics=True):
        """Starts a simulation of the population, opening a pygame window to
        animate the population evolution
        """

        # Create window
        pygame.init()
        pygame.font.init()
        pop_font = pygame.font.Font('freesansbold.ttf', 32)
        ind_font = pygame.font.Font('freesansbold.ttf', 25)
        win = pygame.display.set_mode((self.win_x, self.win_y))
        pygame.display.set_caption("Genetic Algorithm Animation")

        # Create live plot figure
        self.live_fig = plt.figure()
        self.live_ax = Axes3D(self.live_fig)
        self.live_ax.set_xlabel("Velocity")
        self.live_ax.set_ylabel("Size")
        self.live_ax.set_zlabel("Sense Region Radius")

        # If non-graphics option, speed up the interaction
        if not graphics:
            self.speed_up = 10

        # Create initial individuals
        for i in range(self.pop_size):
            ind_temp = individual(self.init_velocity * self.speed_up, 30, 100,
                                  self, "I %s" % (i + 1))
            self.individuals.append(ind_temp)

        # Create initial food
        for i in range(self.food_number):
            food_temp = food(self)
            self.foods.append(food_temp)

        # Main loop
        running = True
        self.frame_no = 0
        while running:
            if not graphics:
                plt.pause(0.000001)
            self.frame_no += 1

            # Stop the program when window is quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if graphics:
                win.fill((0, 0, 0))

                # Population text
                pop_text = pop_font.render("Population: %s" %
                                           self.pop_size, True, (255, 255, 255))
                win.blit(pop_text, (20, 20))

            # Food regeneration
            if self.food_regen:
                food_regen_wait_time = 1000 / (self.food_regen * self.speed_up)
                if self.frame_no % food_regen_wait_time == 0:
                    self.food_number += 1
                    new_food = food(self)
                    self.foods.append(new_food)

            # Step and animate each individual
            temp_individuals = []
            for ind in self.individuals:
                # If alive, move
                if ind.alive:
                    temp_individuals.append(ind)
                    ind.step()

                    if graphics:
                        # Draw individual
                        pygame.draw.rect(win, ind.colour,
                                         (int(round(ind.x_pos)), int(round(ind.y_pos)),
                                          int(round(ind.x_size)), int(round(ind.y_size))))
                        # Label individual
                        ind_text = ind_font.render(
                            ind.name, True, (255, 255, 255))
                        win.blit(ind_text, (int(round(ind.x_pos)),
                                            int(round(ind.y_pos))))

                # If dead remove from population
                else:
                    self.dead_individuals += 1
                    del ind
                    self.replot()
                    self.pop_size -= 1

            self.individuals = temp_individuals

            # Animate foods
            food_index = 0
            for food_piece in self.foods:
                # If not eaten, draw
                if not food_piece.eaten:
                    food_index += 1

                    if graphics:
                        pygame.draw.rect(win, food_piece.colour,
                                         (int(round(food_piece.x_pos)),
                                          int(round(food_piece.y_pos)),
                                          int(round(food_piece.x_size)),
                                          int(round(food_piece.y_size))))

                # If eaten remove from foods
                else:
                    # self.foods = np.delete(self.foods, food_index)
                    self.foods.pop(food_index)
                    self.food_number -= 1

            if graphics:
                pygame.display.update()

            # Summarise each step and save macro population data
            self.frame_data.append(self.frame_no)
            self.pop_size_data.append(self.pop_size)
            self.food_number_data.append(self.food_number)

            # Finish evolution after an amount of iterations
            if self.pop_size == 0:
                running = False

        # Collect data
        self.macro_pop_data['frame'] = self.frame_data
        self.macro_pop_data['population'] = self.pop_size_data
        self.macro_pop_data['food_number'] = self.food_number_data

        # Document final individuals
        for ind in self.individuals:
            pop.add_individual_to_data(ind)

        pygame.quit()

    def plot_summary(self):
        plt.figure()
        plt.xlabel("Frame")
        plt.ylabel("#")
        plt.plot(self.macro_pop_data.frame,
                 self.macro_pop_data.population, label="Population")
        plt.plot(self.macro_pop_data.frame,
                 self.macro_pop_data.food_number, label="Food Number")
        plt.legend()
        plt.show()


pop = population(pop_size=10, food_number=100, food_regen=5)
pop.simulate(graphics=False)
pop.plot_summary()
plt.show()


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pop.past_individual_data.sort_values(by='Time Lived', ascending=False)
