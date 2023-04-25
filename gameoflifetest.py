import numpy
import pygame
from time import time as time_seconds

RENDER_SCALE = 20
width = 2500 // RENDER_SCALE
height = 1400 // RENDER_SCALE
CHUNK = 8
width -= width % CHUNK
ON = (255, 0, 0)
OFF = (0, 255, 0)

print(width, height)


def cells_to_surf(cells):
    colors = numpy.ndarray(shape=(width, height, 3), dtype=int)
    for i in range(width * height):
        x, y = index_to_xy(i)
        array_index = i // CHUNK
        offset = i % CHUNK

        if (cells[array_index] >> (CHUNK - offset - 1)) & 1:
            colors[x, y] = ON
        else:
            colors[x, y] = OFF
    
    return pygame.surfarray.make_surface(colors)


def update(middles, neighbors):
    new = 0

    for i in range(CHUNK):
        new = new << 1
        n_neigh = 0

        # Get total neighbors.
        for neigh in range(CHUNK):
            if numpy.bitwise_and(neighbors, numpy.uint64(1)) == 1:
                n_neigh += 1

            neighbors = neighbors >> numpy.uint64(1)

        # Update middle.
        if (middles >> i) & 1:
            if 2 <= n_neigh <= 3:
                new += 1
        else:
            if n_neigh == 3:
                new += 1
                
    # Reverse new middles.
    reverse = 0
    i = 8
    while i > 0:
        reverse = reverse << 1
        if new & 1:
            reverse ^= 1
        new = new >> 1
        i -= 1
    return reverse


def index_to_xy(index):
    x = index % width
    y = index // width
    return (x, y)


def xy_to_index(x, y):
    index = (y * width) + x
    return index


def get_neighbors(index, cells):
    neighbors = 0
    x, y = index_to_xy(index)

    for dx in [-1, 0, 1]:
        new_x = (x + dx) % width
        for dy in [-1, 0, 1]:
            if dy == 0 and dx == 0:
                continue
            neighbors = neighbors << 1

            new_y = (y + dy) % height
            target = xy_to_index(new_x, new_y)

            offset = target % CHUNK
            array_index = target // CHUNK

            if (cells[array_index] >> (CHUNK-1-offset)) & 1:
                neighbors += 1
    return neighbors


def get_neighbors_array(cells):
    neighbors_array = numpy.zeros(numpy.shape(cells), dtype="uint64")

    for array_index, cell in enumerate(cells):
        neighbors = 0
        for i in range(CHUNK):
            index = (array_index * CHUNK) + i
            neighbors = neighbors << CHUNK
            neighbors += get_neighbors(index, cells)
        neighbors_array[array_index] = neighbors

    return neighbors_array


cells = numpy.zeros((width // CHUNK) * height, dtype="uint8")
cells[10] = 255

pygame.init()
window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF)
window.fill((0, 0, 0))
pygame.display.update()

while True:

    # Render cells
    render = pygame.transform.scale_by(cells_to_surf(cells), RENDER_SCALE)
    window.blit(render, (30, 20))
    pygame.display.update()

    # Fetch neighbors.
    start = time_seconds()
    new_neighbors = get_neighbors_array(cells)
    end = time_seconds()
    print(f"Time taken to find neighbors: {round((end - start) * 1000)}ms")

    start = time_seconds()
    for i, middles in enumerate(cells):
        cells[i] = update(cells[i], new_neighbors[i])
    end = time_seconds()
    print(f"Time taken to update: {round((end - start) * 1000)}ms")
    
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()


