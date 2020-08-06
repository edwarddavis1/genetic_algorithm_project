import numpy as np
import pygame
import math
import pandas as pd
import matplotlib.pyplot as plt

# %matplotlib qt


def is_item_in_sense_region(x_pos, y_pos, item_x_pos, item_y_pos, radius):
    """Checks is something is within an individual's sense region
    """
    if (x_pos - item_x_pos)**2 + (y_pos - item_y_pos)**2 < radius**2:
        return True
    else:
        return False


def text_label(win, text):
    """Text to display on the window
    """
    pygame.font.init()
    font = pygame.font.Font(None, 30)
    scoretext = font.render(text, 1, (255, 255, 255))
    win.blit(scoretext, (500, 457))


class individual:
    def __init__(self, velocity, size, lifetime, pop):
        self.velocity = velocity
        self.size = size
        self.init_lifetime = lifetime
        self.lifetime = lifetime
        self.pop = pop
        self.sense_region_radius = 100
        self.current_theta = np.random.uniform(0, 2 * np.pi)
        self.x_pos = np.random.uniform(0, pop.win_x)
        self.y_pos = np.random.uniform(0, pop.win_y)
        self.x_size = 30
        self.y_size = 30
        self.colour = (0, 0, 255)
        self.x_max = pop.win_x
        self.y_max = pop.win_y
        self.x_min = 0
        self.y_min = 0
        self.time_lived = 0
        self.dying_time = 1000
        self.alive = True
        self.food_x_pos = [f.x_pos for f in pop.foods]
        self.food_y_pos = [f.y_pos for f in pop.foods]
        self.foods_eaten = 0
        self.replications = 0

        self.data = []
        self.frame_data = []
        self.foods_eaten_data = []
        self.replications_data = []

    def collect_data_step(self):
        self.frame_data.append(pop.frame_no)
        self.foods_eaten_data.append(self.foods_eaten)
        self.replications_data.append(self.replications)

    def consolidate_data(self):
        self.data.append(self.frame_data)
        self.data.append(self.foods_eaten_data)
        self.data.append(self.replications_data)

    def update_position(self):
        """Steps the individual in a somewhat random direction
        """
        # Move towards food if within sense region
        move_randomly = True
        for food_piece in pop.foods:
            food_in_sense_region = is_item_in_sense_region(self.x_pos, self.y_pos,
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
                    self.lifetime += food_piece.extra_life_time

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
        """Replicates the current individual
        """
        new_ind = individual(2, 30, self.init_lifetime, self.pop)
        new_ind.x_pos = self.x_pos
        new_ind.y_pos = self.y_pos
        pop.individuals.append(new_ind)
        pop.pop_size += 1

    def step(self):
        """Updates the properties of the individual for a step
        """
        self.time_lived += 1
        if self.time_lived < self.lifetime:
            # Keep moving while alive
            self.update_position()

            # Replicate individual for every two foods it eats
            if self.foods_eaten % 2 == 0 and self.foods_eaten / 2 != self.replications:
                self.replicate()
                self.replications += 1

            # Colour change
            red_colour = np.linspace(255, 0, 5000)
            life_remaining = self.lifetime - self.time_lived
            if life_remaining < 5000:
                self.colour = (red_colour[life_remaining], 0, 255)
            else:
                self.colour = (0, 0, 255)

        elif self.time_lived <= self.lifetime + self.dying_time:
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
        self.data = pd.DataFrame()
        self.frame_data = []
        self.pop_size_data = []
        self.food_number_data = []
        self.individual_data = pd.DataFrame()
        self.dead_individuals = 0

    def simulate(self):
        """Starts a simulation of the population, opening a pygame window to
        animate the population evolution
        """
        pygame.init()
        pygame.font.init()
        font = pygame.font.Font('freesansbold.ttf', 32)

        # Create window
        win = pygame.display.set_mode((self.win_x, self.win_y))
        pygame.display.set_caption("Genetic Algorithm Animation")

        # Create initial individuals
        for i in range(self.pop_size):
            ind_temp = individual(2, 30, 4000, self)
            self.individuals.append(ind_temp)

        # Create initial food
        for i in range(self.food_number):
            food_temp = food(self)
            self.foods.append(food_temp)

        # Food regeneration
        food_regen_wait_time = 1000 / self.food_regen

        # Main loop
        running = True
        self.frame_no = 0
        while running:
            pygame.time.delay(int(1 / (60 * 1000)))
            self.frame_no += 1

            # Stop the program when window is quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            win.fill((0, 0, 0))

            # Population text
            pop_text = font.render("Population: %s" %
                                   self.pop_size, True, (255, 255, 255))
            win.blit(pop_text, (20, 20))

            # Food regeneration
            if self.frame_no % food_regen_wait_time == 0:
                self.food_number += 1
                new_food = food(self)
                self.foods.append(new_food)

            # Step and animate each individual
            ind_index = 0
            for ind in self.individuals:
                # If alive, move
                if ind.alive:
                    ind.step()
                    pygame.draw.rect(win, ind.colour, (ind.x_pos, ind.y_pos,
                                                       ind.x_size, ind.y_size))
                    ind_index += 1
                # If dead remove from population
                else:
                    # collect data
                    self.dead_individuals += 1
                    ind.consolidate_data()
                    self.individual_data['ind_%s' %
                                         self.dead_individuals] = ind.data

                    # self.individuals = np.delete(self.individuals, ind_index)
                    self.individuals.pop(ind_index)
                    self.pop_size -= 1

            # Animate foods
            food_index = 0
            for food_piece in self.foods:
                # If not eaten, draw
                if not food_piece.eaten:
                    pygame.draw.rect(win, food_piece.colour, (food_piece.x_pos, food_piece.y_pos,
                                                              food_piece.x_size, food_piece.y_size))
                    food_index += 1
                # If eaten remove from foods
                else:
                    # self.foods = np.delete(self.foods, food_index)
                    self.foods.pop(food_index)
                    self.food_number -= 1

            pygame.display.update()

            # Summarise each step and save data
            self.frame_data.append(self.frame_no)
            self.pop_size_data.append(self.pop_size)
            self.food_number_data.append(self.food_number)
            for j, ind in enumerate(self.individuals):
                ind.collect_data_step()

            # Finish evolution after an amount of iterations
            if self.pop_size == 0:
                running = False

        pygame.quit()

        # Collect data
        self.data['frame'] = self.frame_data
        self.data['population'] = self.pop_size_data
        self.data['food_number'] = self.food_number_data

        # for ind in self.individuals:
        #     ind.consolidate_data()

    def plot_summary(self):
        plt.figure()
        plt.xlabel("Frame")
        plt.ylabel("#")
        plt.plot(self.data.frame, self.data.population, label="Population")
        plt.plot(self.data.frame, self.data.food_number, label="Food Number")
        plt.legend()
        plt.show()

    def plot_ind(self, ind):
        """Plot frame, food and replications of individuals
        """
        ind_string = "ind_" + str(ind)
        data = self.individual_data[ind_string]
        frame_data = data[0]
        food_eaten_data = data[1]
        replication_data = data[2]

        plt.figure()
        plt.title("Individual: " + str(ind))
        plt.xlabel("Frame")
        plt.ylabel("#")
        plt.plot(frame_data, food_eaten_data, label="Food Eaten")
        plt.plot(frame_data, replication_data, label="Replications")
        plt.legend()
        plt.show()


pop = population(pop_size=1, food_number=10, food_regen=2)
pop.simulate()
pop.plot_summary()
plt.show()

# pop.plot_ind(1)
