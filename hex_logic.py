

POINTY_DIRECTIONS = [
    (1, 0),  # 0: E
    (1, -1),  # 1: NE
    (0, -1),  # 2: NW
    (-1, 0),  # 3: W
    (-1, 1),  # 4: SW
    (0, 1),  # 5: SE
]


FLAT_DIRECTIONS = [
    (1, -1),  # 0: NE
    (1, 0),  # 1: E
    (0, 1),  # 2: SE
    (-1, 1),  # 3: SW
    (-1, 0),  # 4: W
    (0, -1),  # 5: NW
]


HEX_INDEX_DIRECTIONS = [
    [0, 0], []
]


VERTEX_NEIGHBOR_DELTAS = [
    [(0, 0), (1, 0), (0, -1)],      # vertex 0
    [(0, 0), (0, -1), (-1, 0)],     # vertex 1
    [(0, 0), (-1, 0), (-1, 1)],     # vertex 2
    [(0, 0), (-1, 1), (0, 1)],      # vertex 3
    [(0, 0), (0, 1), (1, 0)],       # vertex 4
    [(0, 0), (1, 0), (1, -1)],      # vertex 5
]


EDGE_NEIGHBOR_DELTAS = [
    [(0, 0), (1, 0)],       # edge 0
    [(0, 0), (0, -1)],      # edge 1
    [(0, 0), (-1, 1)],      # edge 2
    [(0, 0), (-1, 0)],      # edge 3
    [(0, 0), (0, +1)],      # edge 4
    [(0, 0), (1, -1)],      # edge 5
]


import math


def peg_to_pixel(q, r, peg_index, hex_size, point_top=True):
    """
    Convert a peg's (q, r, peg_index) into screen (x, y) coordinates.
    - Assumes pointy-topped hexagons.
    - peg_index: 0–11 (alternating corners and edges around the hex)
    - hex_size: radius of a hexagon (distance from center to corner)
    """
    # 1. Convert hex axial coords to pixel center
    sqrt3 = math.sqrt(3)

    if point_top:
        cx = hex_size * sqrt3 * (q + r / 2)
        cy = hex_size * 1.5 * r
    else:
        cx = hex_size * 1.5 * q
        cy = hex_size * math.sqrt(3) * (r + q / 2)

    # 2. Determine angle and radius to peg point
    angle_deg = 30 * peg_index  # peg_index 0 = top (0°), then clockwise
    angle_rad = math.radians(angle_deg)

    # Use full radius for corners, slightly shorter for edges
    radius = hex_size

    edge_indicator = 1 if point_top else 0
    if peg_index % 2 == edge_indicator:  # edge
        radius *= (sqrt3 / 2)  # pull edge pegs slightly closer to center

    # 3. Compute offset
    dx = radius * math.sin(angle_rad)
    dy = -radius * math.cos(angle_rad)  # minus because y axis points down in most GUI systems

    x = cx + dx
    y = cy + dy
    return x, y


# def get_hexes_for_peg(q: int, r: int, peg_index: int) -> list[tuple[int, int]]:
#     """
#     Returns the list of (q, r) hexes that a peg at a given (q, r) and peg_index (0–11) touches.
#     Peg index starts at top corner and proceeds clockwise around a pointy-topped hex.
#     Even indices (0, 2, 4, ...) = corners (touch 3 hexes)
#     Odd indices (1, 3, 5, ...) = edges   (touch 2 hexes)
#     """
#     # 6 axial directions: E, NE, NW, W, SW, SE
#     directions = [
#         (1, 0),   # 0
#         (1, -1),  # 1
#         (0, -1),  # 2
#         (-1, 0),  # 3
#         (-1, 1),  # 4
#         (0, 1),   # 5
#     ]
#
#     center = (q, r)
#     dir_index = (peg_index // 2) % 6
#     prev_dir = directions[(dir_index - 1) % 6]
#     next_dir = directions[dir_index % 6]
#
#     if peg_index % 2 == 0:
#         # Corner: touches current hex and 2 neighbors
#         hex1 = (q + prev_dir[0], r + prev_dir[1])
#         hex2 = (q + next_dir[0], r + next_dir[1])
#         return [center, hex1, hex2]
#     else:
#         # Edge: touches current hex and 1 neighbor
#         neighbor = (q + next_dir[0], r + next_dir[1])
#         return [center, neighbor]


def get_hexes_for_peg(q, r, hex_index, pointy_top):
    """
    Return a sorted tuple of (q, r) tuples = hexes that a peg at this index touches
    Vertices touch 3 hexes, edges touch 2 hexes.

    Notes on return value:
        - Sorted = Guaranteed unique peg location
        - Tuple = immutable, usable as a dict key
    """
    center = (q, r)

    if pointy_top:
        directions = [
            (1, 0), (1, -1), (0, -1),  # 0,1,2
            (-1, 0), (-1, 1), (0, 1)   # 3,4,5
        ]
    else:
        directions = [
            (1, -1), (1, 0), (0, 1),   # 0,1,2
            (-1, 1), (-1, 0), (0, -1)  # 3,4,5
        ]

    # Normalize hex_index to 0–11
    i = hex_index % 12
    dir_index = i // 2
    d = directions[dir_index]
    d_next = directions[(dir_index + 1) % 6]

    # EDGE: touches 2 hexes (center + one neighbor)
    if i % 2 == 1:
        hex_list = [center, (q + d[0], r + d[1])]

    # VERTEX: touches 3 hexes (center + two adjacent neighbors)
    else:
        hex_list = [
            center,
            (q + d[0], r + d[1]),
            (q + d_next[0], r + d_next[1])
        ]

    return sorted(tuple(hex_list))

# def get_hexes_for_peg(q, r, hex_index, pointy_top):
#     """
#     Given a central hex (q, r), a hex_index (0–11), and grid orientation,
#     return the list of hexes the peg at that index would touch.
#
#     Pegs at even indices are placed at vertices and touch 3 hexes.
#     Pegs at odd indices are placed at edges and touch 2 hexes.
#     """
#     i = hex_index % 12
#
#     # get proper axial directions
#     directions = POINTY_DIRECTIONS if pointy_top else FLAT_DIRECTIONS
#
#     if i % 2 == 0:
#         # Vertex (even index) — touches 3 hexes
#         d1 = directions[(i // 2) % 6]
#         d2 = directions[(i // 2 + 1) % 6]
#         return [
#             (q, r),
#             (q + d1[0], r + d1[1]),
#             (q + d2[0], r + d2[1]),
#         ]
#     else:
#         # Edge (odd index) — touches 2 hexes
#         d = directions[(i // 2) % 6]
#         return [
#             (q, r),
#             (q + d[0], r + d[1]),
#         ]