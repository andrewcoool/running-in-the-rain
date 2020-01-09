import CONSTANTS, math
import plotly.express as px
import pygame
import sys
import random

pygame.init()

s_w = 1280
s_h = 720
pi = 3.14159265358

screen = pygame.display.set_mode((s_w, s_h))
pygame.display.set_caption('CAPTION')


class Drop:
    def __init__(self, pos):
        self.pos = pos


class Edge:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2


class Runner:
    def __init__(self, pos, width, height, tilt):
        self.pos = pos
        self.width = width
        self.height = height
        self.tilt = tilt

        self.rawVertices = None
        self.vertices = None
        self.edges = None
        self.body_center = []

        self.peak_y = None

        self.update_runner_vertices()

    def update_runner_vertices(self):
        self.rawVertices = [
            [self.pos[0], self.pos[1]],
            [self.pos[0] + self.width, self.pos[1]],
            [self.pos[0] + self.width, self.pos[1] + self.height],
            [self.pos[0], self.pos[1] + self.height]
        ]

        self.vertices = []

        # Rotation is Centered on The Bottom Right Point (i.e. third vertex [2])
        center = self.rawVertices[2]

        # Rotate Points Among Center
        for vertice in self.rawVertices:
            new_x = center[0] + math.cos(self.tilt) * (vertice[0] - center[0]) + math.sin(self.tilt) * (vertice[1] - center[1])
            new_y = center[1] - math.sin(self.tilt) * (vertice[0] - center[0]) + math.cos(self.tilt) * (vertice[1] - center[1])

            self.vertices.append([new_x, new_y])

        self.edges = [Edge(self.vertices[0], self.vertices[1]),
                      Edge(self.vertices[1], self.vertices[2]),
                      Edge(self.vertices[2], self.vertices[3]),
                      Edge(self.vertices[3], self.vertices[0])
                      ]

        x_ave = average_in_list([v[0] for v in self.vertices])
        y_ave = average_in_list([v[1] for v in self.vertices])

        self.body_center = [x_ave, y_ave]
        self.peak_y = max([v[1] for v in self.vertices])

    def move_runner(self, d_x, d_y):

        self.pos[0] += d_x
        self.pos[1] += d_y

        self.body_center[0] += d_x
        self.body_center[1] += d_y

        self.peak_y += d_y

        for vertice in self.rawVertices:
            vertice[0] += d_x
            vertice[1] += d_y

        for vertice in self.vertices:
            vertice[0] += d_x
            vertice[1] += d_y

        self.edges = [Edge(self.vertices[0], self.vertices[1]),
                      Edge(self.vertices[1], self.vertices[2]),
                      Edge(self.vertices[2], self.vertices[3]),
                      Edge(self.vertices[3], self.vertices[0])
                      ]


def average_in_list(my_list):

    sum = 0

    for entry in my_list:
        sum += entry

    return sum / len(my_list)


def edge_intersect_edge(edge1, edge2):
    interval_x1 = [min(edge1.p1[0], edge1.p2[0]) * (2 - CONSTANTS.COLLISION_ERROR),
                   max(edge1.p1[0], edge1.p2[0]) * CONSTANTS.COLLISION_ERROR]
    interval_x2 = [min(edge2.p1[0], edge2.p2[0]) * (2 - CONSTANTS.COLLISION_ERROR),
                   max(edge2.p1[0], edge2.p2[0]) * CONSTANTS.COLLISION_ERROR]
    interval_y1 = [min(edge1.p1[1], edge1.p2[1]) * (2 - CONSTANTS.COLLISION_ERROR),
                   max(edge1.p1[1], edge1.p2[1]) * CONSTANTS.COLLISION_ERROR]
    interval_y2 = [min(edge2.p1[1], edge2.p2[1]) * (2 - CONSTANTS.COLLISION_ERROR),
                   max(edge2.p1[1], edge2.p2[1]) * CONSTANTS.COLLISION_ERROR]

    m1 = (edge1.p1[1] - edge1.p2[1]) / (edge1.p1[0] - edge1.p2[0])
    m2 = (edge2.p1[1] - edge2.p2[1]) / (edge2.p1[0] - edge2.p2[0])

    x = (-m2 * edge2.p1[0] + edge2.p1[1] + m1 * edge1.p1[0] - edge1.p1[1])/(m1 - m2)
    y = m1 * x - m1 * edge1.p1[0] + edge1.p1[1]

    x_valid = interval_x1[0] <= x <= interval_x1[1] and interval_x2[0] <= x <= interval_x2[1]
    y_valid = interval_y1[0] <= y <= interval_y1[1] and interval_y2[0] <= y <= interval_y2[1]

    # print(y, interval_y1, interval_y2)

    return x_valid and y_valid


def collide(runner, drop):
    # draw a horizontal line from the point to the right
    # if it intersects the edges of the runner an odd number of times
    # then it is inside

    times_intersected = 0
    test_line = Edge([drop.pos[0], drop.pos[1]], [9999999999999999999, drop.pos[1]])

    for edge in runner.edges:
        # print(edge.p1, edge.p2)
        if edge_intersect_edge(edge, test_line):
            # print(edge.p1, edge.p2)
            times_intersected += 1

    if times_intersected % 2 == 0:
        return False
    else:
        return True


def flip_y_coords(coords):
    return [coords[0], s_h - coords[1]]


def create_rain_drop_row():
    time_to_reach_ground = (CONSTANTS.RAIN_DROP_GENERATION_HEIGHT - my_runner.body_center[1]) / abs(CONSTANTS.V_RAIN)
    x_center = time_to_reach_ground * CONSTANTS.V_RUNNER + my_runner.body_center[0]

    x_min = x_center - CONSTANTS.RAIN_DROP_GENERATION_WIDTH / 2
    x_max = x_center + CONSTANTS.RAIN_DROP_GENERATION_WIDTH / 2

    drop_row = []

    """
    current_pos = x_min

    while current_pos < x_max:
        drop_row.append(Drop([current_pos, 5]))
        current_pos += drop_spacing
    """

    h_i = math.ceil(CONSTANTS.RAIN_DROP_GENERATION_WIDTH / drop_spacing)

    for i in range(h_i):
        x = random.randint(round(x_min * 100), round(x_max * 100)) / 100
        y = CONSTANTS.RAIN_DROP_GENERATION_HEIGHT

        drops.append(Drop([x, y]))

    drops.extend(drop_row)


def create_rain_drop_fill():
    x_min = -2
    x_max = CONSTANTS.INITIAL_RAIN_DROP_WIDTH + x_min

    y_min = 0
    y_max = CONSTANTS.RAIN_DROP_GENERATION_HEIGHT

    """
    current_x = x_min

    while current_x < x_max:

        current_y = 0
        while current_y < y_max:
            drops.append(Drop([current_x, current_y]))
            current_y += drop_spacing

        current_x += drop_spacing
    """

    h_i = math.ceil((x_max - x_min) / drop_spacing)
    v_i = math.ceil((y_max - y_min) / drop_spacing)

    for i0 in range(h_i):
        for i1 in range(v_i):
            x = random.randint(round(x_min * 100), round(x_max * 100)) / 100
            y = random.randint(round(y_min * 100), round(y_max * 100)) / 100
            drops.append(Drop([x, y]))


def pygame_render():
    # RENDER

    screen.fill((255, 255, 255))
    for drop in drops:
        xy = flip_y_coords([round(CONSTANTS.SCREEN_SCALE * drop.pos[0]), round(CONSTANTS.SCREEN_SCALE * drop.pos[1])])
        pygame.draw.circle(screen, (52, 76, 235), xy, 2, 0)

    vertices_converted = [[v[0] * CONSTANTS.SCREEN_SCALE, v[1] * CONSTANTS.SCREEN_SCALE] for v in my_runner.vertices]
    vertices_flipped = [flip_y_coords(v) for v in vertices_converted]

    pygame.draw.polygon(screen, (42, 227, 32), vertices_flipped, 0)

    pygame.display.flip()

# ============================================================================= #
# CALCULATION OF STEPS
# ============================================================================= #


# Take Cube Root of Cubic Density
one_dimension_drop_density = CONSTANTS.RAINDROP_DENSITY ** (1 / 3)  # drops/m
drop_spacing = 1 / one_dimension_drop_density  # m / drop

# Recreation of T=D/V
time_to_generate_row_of_drops = drop_spacing / abs(CONSTANTS.V_RAIN)
time_step = 0

# Recommended Time Step is TIME_FOR_ROW / 20
if CONSTANTS.TIME_STEP == 'AUTO':
    time_step = time_to_generate_row_of_drops / CONSTANTS.TIME_PRECISION
    print('AUTO Generating Time Step of ' + str(time_step) + 's')
else:
    if time_to_generate_row_of_drops < CONSTANTS.TIME_STEP * CONSTANTS.TIME_PRECISION:
        time_step = time_to_generate_row_of_drops / CONSTANTS.TIME_PRECISION

        print('Given TIME_STEP is too large...')
        print('AUTO Generating Time Step of ' + str(time_step) + 's')

    else:
        time_step = CONSTANTS.TIME_STEP

# ============================================================================= #
# LOOP STARTS HERE
# ============================================================================= #

tilt_point = []
final_drops_point = []

CONSTANTS.RUNNER_TILT = 0.000001
tick = 0

while CONSTANTS.RUNNER_TILT < (pi / 2):
    CONSTANTS.RUNNER_TILT += (pi / 2) / CONSTANTS.TILT_PRECISION
    print('Current Trial ', tick)
    print('Current Tilt', CONSTANTS.RUNNER_TILT)

    tick += 1

    current_time = 0

    drops = []
    my_runner = Runner([0, 0], CONSTANTS.RUNNER_WIDTH, CONSTANTS.RUNNER_HEIGHT, CONSTANTS.RUNNER_TILT)
    total_drops_collided = 0
    drops_point = []
    time_point = []

    pretend_pos = 0

    rows_generated = 1
    create_rain_drop_fill()

    # drops.append(Drop([1, 5]))

    # FIX THIS BTW
    while pretend_pos < CONSTANTS.DESTINATION_X_POS:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        if CONSTANTS.DO_RENDER:
            pygame_render()
        #
        # Move All Points
        for drop in drops:
            drop.pos[0] += CONSTANTS.V_RAIN_H * time_step
            drop.pos[1] += CONSTANTS.V_RAIN * time_step

        # Move Runner Only Once Ready
        my_runner.move_runner(CONSTANTS.V_RUNNER * time_step, 0)  # 0 VERTICAL VELOCITY
        pretend_pos += CONSTANTS.V_RUNNER * time_step

        # Check for Collisions (make a duplicate list for safe deletion)

        for drop in drops[:]:
            if drop.pos[1] < 0:
                # KIll DROP
                drops.remove(drop)
            else:
                if collide(my_runner, drop):
                    drops.remove(drop)
                    total_drops_collided += 1

                    time_point.append(current_time)
                    drops_point.append(total_drops_collided)

        # Create New RainDrops?
        if rows_generated * time_to_generate_row_of_drops <= current_time:
            # Create New Row
            create_rain_drop_row()
            rows_generated += 1

        current_time += time_step
        print(current_time, total_drops_collided)

    tilt_point.append(CONSTANTS.RUNNER_TILT)
    final_drops_point.append(total_drops_collided)

if CONSTANTS.SCALE_WITH_DEPTH:
    final_drops_point = [d * (CONSTANTS.RUNNER_DEPTH / drop_spacing) for d in final_drops_point]

fig = px.scatter(x=tilt_point, y=final_drops_point)

fig.update_layout(
    title='The Effect of Tilt on Number of Raindrops Collided With',
    xaxis_title='Tilt',
    yaxis_title='Total Raindrops Collided With (N)',
    font=dict(
        family='Courier New, monospace',
        size=18,
        color='#7f7f7f'
    )
)

fig.show()

"""
current_time = 0

drops = []
my_runner = Runner([0, 0], CONSTANTS.RUNNER_WIDTH, CONSTANTS.RUNNER_HEIGHT, CONSTANTS.RUNNER_TILT)
total_drops_collided = 0
drops_point =[]
time_point = []

pretend_pos = 0

rows_generated = 1
create_rain_drop_fill()

# drops.append(Drop([1, 5]))

# FIX THIS BTW
while pretend_pos < CONSTANTS.DESTINATION_X_POS:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
            
    pygame_render()

    # Move All Points
    for drop in drops:
        drop.pos[0] += CONSTANTS.V_RAIN_H * time_step
        drop.pos[1] += CONSTANTS.V_RAIN * time_step

    # Move Runner Only Once Ready
    my_runner.move_runner(CONSTANTS.V_RUNNER * time_step, 0)  # 0 VERTICAL VELOCITY
    pretend_pos += CONSTANTS.V_RUNNER * time_step

    # Check for Collisions (make a duplicate list for safe deletion)
    for drop in drops[:]:
        if drop.pos[1] < 0:
            # KIll DROP
            drops.remove(drop)
        else:
            if collide(my_runner, drop):

                drops.remove(drop)
                total_drops_collided += 1

                time_point.append(current_time)
                drops_point.append(total_drops_collided)

    # Create New RainDrops?
    if rows_generated * time_to_generate_row_of_drops <= current_time:
        # Create New Row
        create_rain_drop_row()
        rows_generated += 1

    current_time += time_step
    print(current_time, total_drops_collided)

if CONSTANTS.SCALE_WITH_DEPTH:
    drops_point = [d * (CONSTANTS.RUNNER_DEPTH/drop_spacing) for d in drops_point]

fig = px.scatter(x=time_point, y=drops_point)
fig.show()

"""
