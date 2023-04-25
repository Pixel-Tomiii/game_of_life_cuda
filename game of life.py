import cupy

CHUNK_SIZE = 8

# Update cells kernel.
# middles - 8 bit integer of on/off bits denoting the state of the middles cells.
# neighbors - 64 bit integer denoting the surrounding neighbors of each bit.
# result - the resultant 8 middles after their state has been updated.
update_cells = cupy.ElementwiseKernel(
"uint8 middles, uint64 neighbors",
"uint8 result",
"""
int on = 0;
int reverse = 0;
                
for (int middle_bit = 0; middle_bit < 8; middle_bit++) {
    on = 0;
    for (int neigh = 0; neigh < 8; neigh++) {
        if (neighbors & 1) {
            on++;
        }
        neighbors = neighbors >> 1;
    }

    if ((middles >> middle_bit) & 1) {
        if (on >= 2 && on <= 3) result++;
    }
    else {
        if (on == 3) result++;
    }
    result = result << 1;
}

for (int rev = 8; rev > 0; rev--) {
    reverse = reverse << 1
    if (result & 1) {
        reverse = reverse ^ 1
    }
    result = result >> 1
}
result = reverse;
""",
"update_cells")


def index_to_xy(index):
    """Converts a 1D index to a 2D x, y coordinate"""
    x = index % width
    y = index // width
    return (x, y)


def xy_to_index(x, y):
    """Converts an x, y coordinate back to its 1D index"""
    return (y * width) + x


def get_neighbors(index, cells):
    """Gets the neighbors of the cell at the given index."""
    neighbors = 0
    x, y = index_to_xy(index)

    # Loop through 3x3 square.
    for dy in [-1, 0, 1]:
        new_y = (y + dy) % height
        for dx in [-1, 0, 1]:
            # Skip centre cell.
            if dy == 0 and dx == 0:
                continue
            
            new_x = (x + dx) % width
            target = xy_to_index(new_x, new_y)
            
