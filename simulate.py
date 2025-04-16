import pygame
import random
import math
import pygame_gui

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
manager = pygame_gui.UIManager((WIDTH, HEIGHT))
pygame.display.set_caption("Epidemic Spread Simulation (SIR)")

BLUE = (0, 0, 255)      # Susceptible
RED = (255, 0, 0)       # Infected
GREEN = (0, 200, 0)     # Recovered
WHITE = (255, 255, 255)

# NUM_AGENTS = 100
# RADIUS = 5
# SPEED = 2
# INFECTION_RADIUS = 50
# INFECTION_TIME = 2000  # milliseconds


SUSCEPTIBLE = 0
INFECTED = 1
RECOVERED = 2

x_offset = 20  
y_offset = 20
PANEL_WIDTH = 250


# sliders = {
#     "Infection Time": pygame_gui.elements.UIHorizontalSlider(
#         relative_rect = pygame.Rect((20, 20), (200, 30)),
#         start_value = INFECTION_TIME,
#         text = "Infection Time",
#         value_range = (100, 30000),
#         manager = manager
#     ),
#     "Infection Radius": pygame_gui.elements.UIHorizontalSlider(
#         relative_rect = pygame.Rect((20, 60), (200, 30)),
#         start_value = INFECTION_RADIUS,
#         value_range = (20, 500),
#         text = "Infection Radius",
#         manager = manager
#     ),
#     "Speed": pygame_gui.elements.UIHorizontalSlider(
#         relative_rect = pygame.Rect((20, 100), (200, 30)),
#         start_value = SPEED,
#         value_range = (1, 10),
#         text = "Infection Time",
#         manager = manager
#     ),
#     "Agent Count": pygame_gui.elements.UIHorizontalSlider(
#         relative_rect = pygame.Rect((20, 140), (200, 30)),
#         start_value = NUM_AGENTS,
#         value_range = (10, 500),
#         text = "Agent Count",
#         manager = manager
#     ),
#     "Agent Radius": pygame_gui.elements.UIHorizontalSlider(
#         relative_rect = pygame.Rect((20, 180), (200, 30)),
#         start_value = RADIUS,
#         value_range = (2, 15),
#         text = "Agent Radius",
#         manager = manager
#     ),
#     "Start": pygame_gui.elements.UIButton(
#         relative_rect = pygame.Rect((250, 20), (100, 30)),
#         text = 'Start',
#         manager = manager
#     )
# }

def add_slider_with_label(name, start_value, min_val, max_val):
    global y_offset
    pygame_gui.elements.UILabel(
        pygame.Rect((x_offset, y_offset), (200, 20)),
        name,
        manager=manager
    )
    y_offset += 25
    slider = pygame_gui.elements.UIHorizontalSlider(
        pygame.Rect((x_offset, y_offset), (200, 30)),
        start_value=start_value,
        value_range=(min_val, max_val),
        manager=manager
    )
    y_offset += 50
    return slider

infection_time_slider = add_slider_with_label("Infection Time", 2000, 100, 30000)
infection_radius_slider = add_slider_with_label("Infection Radius", 50, 20, 500)
speed_slider = add_slider_with_label("Speed", 2, 1, 10)
agent_count_slider = add_slider_with_label("Agent Count", 100, 10, 300)
radius_slider = add_slider_with_label("Agent Radius", 5, 2, 15)

start_button = pygame_gui.elements.UIButton(
    pygame.Rect((x_offset, y_offset), (100, 30)),
    text = 'Start',
    manager = manager
)

started = False
clock = pygame.time.Clock()
while not started:
    time_delta = clock.tick(60) / 1000.0
    screen.fill(WHITE)
    pygame.draw.rect(screen, (230, 230, 230), pygame.Rect(0, 0, PANEL_WIDTH, HEIGHT))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        manager.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == start_button:
            # Click "Start"
            started = True
            

    manager.update(time_delta)
    manager.draw_ui(screen)
    pygame.display.update()

INFECTION_TIME = int(infection_time_slider.get_current_value())
INFECTION_RADIUS = int(infection_radius_slider.get_current_value())
SPEED = int(speed_slider.get_current_value())
NUM_AGENTS = int(agent_count_slider.get_current_value())
RADIUS = int(radius_slider.get_current_value())


class Agent:
    def __init__(self):
        self.x = random.randint(PANEL_WIDTH + RADIUS, WIDTH - RADIUS)
        self.y = random.randint(RADIUS, HEIGHT - RADIUS)
        self.dx = random.choice([-SPEED, SPEED])
        self.dy = random.choice([-SPEED, SPEED])
        self.state = SUSCEPTIBLE
        self.infection_timer = 0

    def move(self):
        self.x += self.dx
        self.y += self.dy

        # Bounce off walls and panel
        if self.x <= PANEL_WIDTH + RADIUS or self.x >= WIDTH - RADIUS:
            self.dx *= -1
        if self.y <= RADIUS or self.y >= HEIGHT - RADIUS:
            self.dy *= -1

    def draw(self):
        if self.state == SUSCEPTIBLE:
            color = BLUE
        elif self.state == INFECTED:
            color = RED
        else:
            color = GREEN
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), RADIUS)

    def update(self, current_time):
        if self.state == INFECTED:
            if current_time - self.infection_timer > INFECTION_TIME:
                self.state = RECOVERED

agents = [Agent() for _ in range(NUM_AGENTS)]
# Infect one randomly
patient_zero = random.choice(agents)
patient_zero.state = INFECTED
patient_zero.infection_timer = pygame.time.get_ticks()

# Main loop
running = True

while running:
    # clock.tick(60) #60fps
    time_delta = clock.tick(60) / 1000.0
    screen.fill(WHITE)
    pygame.draw.rect(screen, (230, 230, 230), pygame.Rect(0, 0, PANEL_WIDTH, HEIGHT))
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():       
        if event.type == pygame.QUIT:       #pressing cross to quit
            running = False
        manager.process_events(event)

    for agent in agents:
        agent.move()                       #moves the circles based on the class
        agent.update(current_time)

    for i, a in enumerate(agents):
        if a.state == INFECTED:
            for b in agents[i+1:]:
                if b.state == SUSCEPTIBLE:
                    distance = math.hypot(a.x - b.x, a.y - b.y)
                    if distance < INFECTION_RADIUS:
                        b.state = INFECTED
                        b.infection_timer = current_time

    infected_count = sum(1 for agent in agents if agent.state == INFECTED)
    
    if infected_count == 0:
        susceptible_agents = [agent for agent in agents if agent.state == SUSCEPTIBLE]
        if susceptible_agents:
            new_patient_zero = random.choice(susceptible_agents)
            new_patient_zero.state = INFECTED
            new_patient_zero.infection_timer = pygame.time.get_ticks()

    for agent in agents:
        agent.draw()

    manager.update(time_delta)
    manager.draw_ui(screen)
    pygame.display.flip()

pygame.quit()