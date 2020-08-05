import numpy as np
import pygame
import math


def random_direction():
    """Selects a random 2D direction using an Inverse CDF function in polar
    coordinates
    """
    theta = np.random.uniform(0, 2 * np.pi)

    # Cartesian Conversion
    x = np.sin(theta)
    y = np.cos(theta)
    return x, y


def is_item_in_sense_region(x_pos, y_pos, item_x_pos, item_y_pos, radius):
    """Checks is something is within an individual's sense region
    """
    if (x_pos - item_x_pos)**2 + (y_pos - item_y_pos)**2 < radius**2:
        return True
    else:
        return False


class individual:
    def __init__(self, velocity, size, lifetime, pop):
        self.velocity = velocity
        self.size = size
        self.lifetime = lifetime
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
                if distance_to_food == 0:
                    food_piece.eat()
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

    def step(self):
        """Updates the properties of the individual for a step
        """
        self.time_lived += 1
        if self.time_lived < self.lifetime:
            # Keep moving while alive
            self.update_position()

        elif self.time_lived <= self.lifetime + self.dying_time:
            # If dying change colour to red
            self.colour = (255, 0, 0)
        else:
            self.alive = False


class food:
    def __init__(self, extra_life_time, pop):
        self.extra_life_time = extra_life_time
        self.colour = (0, 255, 0)
        self.x_size = 10
        self.y_size = 10
        self.x_pos = np.random.uniform(0, pop.win_x)
        self.y_pos = np.random.uniform(0, pop.win_y)
        self.eaten = False

    def eat(self):
        self.eaten = True


class population:
    def __init__(self, pop_size, food_number):
        self.pop_size = pop_size
        self.win_x = 800
        self.win_y = 800
        self.food_number = food_number
        self.individuals = []
        self.foods = []

    def simulate(self, iterations):
        """Starts a simulation of the population, opening a pygame window to
        animate the population evolution
        """
        pygame.init()

        # Create window
        win = pygame.display.set_mode((self.win_x, self.win_y))
        pygame.display.set_caption("Genetic Algorithm Animation")

        # Create initial individuals
        for i in range(self.pop_size):
            ind_temp = individual(5, 30, 3000, self)
            self.individuals.append(ind_temp)

        # Create initial food
        for i in range(self.food_number):
            food_temp = food(1000, self)
            self.foods.append(food_temp)

        # Main loop
        running = True
        frame_no = 0
        while running:
            pygame.time.delay(int(1 / (60 * 1000)))
            frame_no += 1

            # Stop the program when window is quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Step and animate each individual
            win.fill((0, 0, 0))
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
                    self.individuals = np.delete(self.individuals, ind_index)
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
                    self.foods = np.delete(self.foods, food_index)
                    self.food_number -= 1

            pygame.display.update()

            # Finish evolution after an amount of iterations
            if frame_no >= iterations:
                running = False

        pygame.quit()


pop = population(3, 4)
pop.simulate(10000)
