import pygame
import numpy as np
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


pygame.init()

# Create window
win_x = 800
win_y = 800
win = pygame.display.set_mode((win_x, win_y))
pygame.display.set_caption("Genetic Algorithm Animation")

# Population characteristics
population_size = 10

# Individual initial characteristics
x_position = [400] * population_size
y_position = [400] * population_size
x_size = 30
y_size = 30
velocity = [5] * population_size
lifetime = [5000] * population_size

# Colour of individuals
rgb_x = [0] * population_size
rgb_y = [0] * population_size
rgb_z = [255] * population_size

# Sense region characteristics
sense_region_radius = 100
# rgb_x_sense_region = [218] * population_size
# rgb_y_sense_region = [112] * population_size
# rgb_z_sense_region = [214] * population_size

# Food characteristics
food_number = 9
food_life_extension = 3000
x_position_food = np.random.uniform(0, 800, food_number)
y_position_food = np.random.uniform(0, 800, food_number)
x_size_food = 10
y_size_food = 10
rgb_x_food = [0] * food_number
rgb_y_food = [255] * food_number
rgb_z_food = [0] * food_number

# Initial conditions
frame_rate = 20
number_of_frames = 0
number_of_dead_frames = [0] * population_size
total_dead_time = 500
running = True

# Main loop
while running:
    pygame.time.delay(frame_rate)
    number_of_frames += 1
    # Fill background black where individuals used to be
    win.fill((0, 0, 0))

    # Stop the program when window is quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Loop over population
    individual = 0
    while individual < population_size:

        # Check if individual has exceeded its lifetime
        # When individual dies, stop and turn red breifly before disappearing
        current_run_time = number_of_frames * frame_rate
        if current_run_time >= lifetime[individual]:
            # Stop moving
            velocity[individual] = 0
            # Turn red
            rgb_x[individual] = 255
            rgb_y[individual] = 0
            rgb_z[individual] = 0

            number_of_dead_frames[individual] += 1
            current_dead_time = number_of_dead_frames[individual] * frame_rate
            # Individual dies
            if current_dead_time >= total_dead_time:
                x_position = np.delete(x_position, individual)
                y_position = np.delete(y_position, individual)
                lifetime = np.delete(lifetime, individual)
                rgb_x = np.delete(rgb_x, individual)
                rgb_y = np.delete(rgb_y, individual)
                rgb_z = np.delete(rgb_z, individual)
                velocity = np.delete(velocity, individual)
                number_of_dead_frames = np.delete(
                    number_of_dead_frames, individual)
                population_size -= 1
                continue

        # Define sense region
        # NOTE this should be randomised probably
        food_in_sense_region = False
        for i in range(food_number):
            # if food is within sense region head towards it
            food_in_sense_region = is_item_in_sense_region(x_position[individual],
                                                           y_position[individual],
                                                           x_position_food[i],
                                                           y_position_food[i],
                                                           sense_region_radius)
            if food_in_sense_region:
                target_food = i
                break

        if food_in_sense_region:
            # Calculate distance and direction to food
            radians_to_food = math.atan2(y_position[individual] - y_position_food[target_food],
                                         x_position[individual] - x_position_food[target_food])
            distance_to_food = math.hypot(x_position[individual] - x_position_food[target_food],
                                          y_position[individual] - y_position_food[target_food])
            distance_to_food = int(distance_to_food)

            # If individual is at food location, eat the food
            if distance_to_food == 0:
                # Delete food
                x_position_food = np.delete(x_position_food, target_food)
                y_position_food = np.delete(y_position_food, target_food)
                food_number -= 1

                # Increase life of individual
                lifetime[individual] += food_life_extension

            # Otherwise move directly towards food
            else:
                if distance_to_food > velocity[individual]:
                    x_update = -math.cos(radians_to_food) * \
                        velocity[individual]
                    y_update = -math.sin(radians_to_food) * \
                        velocity[individual]
                else:
                    x_update = -math.cos(radians_to_food) * \
                        distance_to_food
                    y_update = -math.sin(radians_to_food) * \
                        distance_to_food

        else:
            # Move randomly if not chasing food
            x_update, y_update = np.multiply(
                random_direction(), velocity[individual])

        # Update position, making sure to stay in the window
        x_adjusted = False
        y_adjusted = False
        if (x_position[individual] + x_update > win_x or
                x_position[individual] + x_update < 0):
            x_position[individual] -= x_update
            x_adjusted = True
        if (y_position[individual] + y_update > win_y or
                y_position[individual] + y_update < 0):
            y_position[individual] -= y_update
            y_adjusted = True

        if not x_adjusted:
            x_position[individual] += x_update
        if not y_adjusted:
            y_position[individual] += y_update

        # Create individual (window, color, (pos, size))
        pygame.draw.rect(win, (rgb_x[individual], rgb_y[individual],
                               rgb_z[individual]), (x_position[individual],
                                                    y_position[individual],
                                                    x_size, y_size))

        # Draw food
        for food in range(food_number):
            pygame.draw.rect(win, (rgb_x_food[food],
                                   rgb_y_food[food],
                                   rgb_z_food[food]),
                             (x_position_food[food],
                              y_position_food[food],
                              x_size_food, y_size_food))
        individual += 1

    pygame.display.update()

pygame.quit()
