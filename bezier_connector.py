from src.PyVMF import *
from main import *
from sidewalls import BrushVertexManipulationBox

def bezier(t, points):
    P1, P2, P3, P4 = points
    x = (1-t)**3*P1[0] + 3*(1-t)**2*t*P2[0] +3*(1-t)*t**2*P3[0] + t**3*P4[0]
    y = (1-t)**3*P1[1] + 3*(1-t)**2*t*P2[1] +3*(1-t)*t**2*P3[1] + t**3*P4[1]
    z = (1-t)**3*P1[2] + 3*(1-t)**2*t*P2[2] +3*(1-t)*t**2*P3[2] + t**3*P4[2]
    return x, y, z

def bezier_tangent(t, points):
    P1, P2, P3, P4 = points
    dx = -3*(1-t)**2*P1[0] - 6*(1-t)*t*P2[0] +3*(1-t)**2*P2[0] - 3*t**2*P3[0] + 6 * (1-t)*t*P3[0] + 3*t**2*P4[0]
    dy = -3*(1-t)**2*P1[1] - 6*(1-t)*t*P2[1] +3*(1-t)**2*P2[1] - 3*t**2*P3[1] + 6 * (1-t)*t*P3[1] + 3*t**2*P4[1]
    dz = -3*(1-t)**2*P1[2] - 6*(1-t)*t*P2[2] +3*(1-t)**2*P2[2] - 3*t**2*P3[2] + 6 * (1-t)*t*P3[2] + 3*t**2*P4[2]

    return dx, dy, dz

def line(t, P0, P1):
    """ we construct the line, starting at P0 and ending at P1 """
    x = P0[0]*(1-t) + P1[0]*t
    y = P0[1]*(1-t) + P1[1]*t
    z = P0[2]*(1-t) + P1[2]*t
    return x, y, z

def get_random_coordinate( max: int):
    return (randint(-max, max)*128, randint(-max, max)*128, randint(-max, max)*128)

def DIRECTION_HANDLER( direction, s ):
    '''
    Here we use: 'l' for turn left, 'r' for turn right, 'o' for opposite, and '-' for do nothing
    '''
    direction_dict = {
                'x':
                    {
                    'r':    '-y',
                    'l':    'y',
                    '-':    'x',
                    'o':    '-x',
                    },
                'y':
                    {
                    'r':    'x',
                    'l':    '-x',
                    '-':    'y',
                    'o':    '-y',
                    },
                '-x':
                    {
                    'r':    'y',
                    'l':    '-y',
                    '-':    '-x',
                    'o':    'x',
                    },
                '-y':
                    {
                    'r':    '-x',
                    'l':    'x',
                    '-':    '-y',
                    'o':    'y',
                    },
                'z':
                    {
                    'o':    '-z',
                    },
                '-z':
                    {
                    'o':    'z',
                    }
                }
    return direction_dict[direction][s]

def DIRECTION_IS_POSITIVE( direction ):
    if direction in { 'x', 'y', 'z' }:
        return 1
    return -1

handle_points = [ get_random_coordinate(20), get_random_coordinate(20), get_random_coordinate(20), get_random_coordinate(20) ]
# handle_points = [ (0,0,0), (0,0,20*128), (20*128,0,20*128), (20*128, 0, 0) ]

prototype_vmf = load_vmf('vmfs/prototype.vmf')
dummy_vmf = new_vmf()

amount = 6

new_tangents = [bezier_tangent(i/(amount+1), handle_points) for i in range(amount+1)]
new_coords = [bezier(i/(amount+1), handle_points) for i in range(amount+1)]

# we want the centerpoints to be on the 128 grid
new_coords = [((coord[0]//128)*128, (coord[1]//128)*128, (coord[2]//128)*128) for coord in new_coords]



for i in range(len(new_coords)-1):
    x_diff = new_coords[i+1][0] - new_coords[i][0]
    x_dir = 'x' if x_diff > 0 else '-x'
    y_diff = new_coords[i+1][1] - new_coords[i][1]
    y_dir = 'y' if y_diff > 0 else '-y'
    z_diff = new_coords[i+1][2] - new_coords[i][2]
    z_dir = 'z' if z_diff > 0 else '-z'

    # we want to determine the direction of our cube
    index_to_direction_dic = { 0: x_dir, 1: y_dir, 2: z_dir}
    index_to_other_directions_dic = { 0: (y_dir, z_dir), 1: (x_dir, z_dir), 2: (x_dir, y_dir) }
    direction_to_diff_dic = {x_dir: x_diff, y_dir: y_diff, z_dir: z_diff}

    index = new_tangents[i].index(max(new_tangents[i]))
    direction = index_to_direction_dic[index]
    others = index_to_other_directions_dic[index]

    proto = createDuplicateVMF(prototype_vmf)
    verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()
    verts.translate( *new_coords[i] )
    move_dic = {
        others[0]: DIRECTION_IS_POSITIVE(others[0]) * direction_to_diff_dic[others[0]] + randint(1, 4)*128,
        others[1]: DIRECTION_IS_POSITIVE(others[1]) * direction_to_diff_dic[others[1]] + randint(1, 4)*128,
        direction: DIRECTION_IS_POSITIVE(direction) * direction_to_diff_dic[direction],
        DIRECTION_HANDLER(others[0],'o'): randint(1, 4)*128,
        DIRECTION_HANDLER(others[1],'o'): randint(1, 4)*128,
    }
    verts.move_to_dic( move_dic )
    
    # give it the trigger texture
    solid = proto.get_solids()[0]
    for side in solid.get_sides():
        side.material = 'tools/toolsskip'.upper()

    dummy_vmf = addVMF(dummy_vmf, proto)

dummy_vmf.export('vmfs/bezier_test.vmf')
