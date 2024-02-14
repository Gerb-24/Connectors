# The goal here is to handle brushes that overlap with eachother
# and cut them into smaller brushes that second_attempt can work with

from src.PyVMF import *
from main import *
from sidewalls import BrushVertexManipulationBox
from random_connector import get_dimensions_of_solid
from bezier_connector import DIRECTION_HANDLER, DIRECTION_IS_POSITIVE

class ClippingPlane:
    def __init__(self, direction, value) -> None:
        self.direction = direction
        self.value = value
    def cut_solid( self, solid: Solid ):
        def get_move( direction, value ):
            moveDict = {
            'x': (value, 0, 0),
            'y': (0, value, 0),
            'z': (0, 0, value),
            '-x': (value, 0, 0),
            '-y': (0, value, 0),
            '-z': (0, 0, value),
            }
            return moveDict[ direction ]
        # first we need to check that we actually do make a cut into this solid
        # otherwise we return our solid again
        x_min, x_max, y_min, y_max, z_min, z_max = get_dimensions_of_solid( solid )
        direction_to_min_max_dict = {
            'x':    (x_min, x_max),
            'y':    (y_min, y_max),
            'z':    (z_min, z_max),
        }
        if not (direction_to_min_max_dict[self.direction][0] < self.value and direction_to_min_max_dict[self.direction][1] > self.value):
            return None
        # we now want to get the dimensions of the corresponding faces
        direction_to_dim_dic = {
            'x':    x_max,
            'y':    y_max,
            'z':    z_max,
            '-x':   x_min,
            '-y':   y_min,
            '-z':   z_min,
        }
        min_solid = solid.copy()
        min_value = direction_to_min_max_dict[self.direction][0]
        min_dic = direction_to_dim_dic.copy()
        min_dic[self.direction] = min_value
        min_dic[DIRECTION_HANDLER(self.direction, 'o')] = min_value
        min_vmb = VertexManipulationBox( min_dic['-x'], min_dic['x'], min_dic['-y'], min_dic['y'], min_dic['-z'], min_dic['z'] )
        min_verts = min_vmb.getVerticesOfSolid(min_solid)
        for vertex in min_verts:
            vertex.move( *get_move( DIRECTION_HANDLER(self.direction, 'o'), self.value - min_value))
        
        max_solid = solid.copy()
        max_value = direction_to_min_max_dict[self.direction][1]
        max_dic = direction_to_dim_dic.copy()
        max_dic[self.direction] = max_value
        max_dic[DIRECTION_HANDLER(self.direction, 'o')] = max_value
        max_vmb = VertexManipulationBox( max_dic['-x'], max_dic['x'], max_dic['-y'], max_dic['y'], max_dic['-z'], max_dic['z'] )
        max_verts = max_vmb.getVerticesOfSolid(max_solid)
        for vertex in max_verts:
            vertex.move( *get_move( DIRECTION_HANDLER(self.direction, 'o'), self.value - max_value))

        return (max_solid, min_solid)

def get_clipping_planes_of_intersection( solid: Solid, other_solid: Solid ):
    x_min, x_max, y_min, y_max, z_min, z_max = get_dimensions_of_intersection( solid, other_solid )
    return (ClippingPlane('x', x_min), 
            ClippingPlane('x', x_max), 
            ClippingPlane('y', y_min), 
            ClippingPlane('y', y_max), 
            ClippingPlane('z', z_min), 
            ClippingPlane('z', z_max))

def get_dimensions_of_intersection( solid: Solid, other_solid: Solid ):
    def get_dimensions_of_intersect_along_axis( x_min, x_max, o_x_min, o_x_max ):
        intersect_x_min = o_x_min if x_min <= o_x_min else x_min
        intersect_x_max = o_x_max if x_max >= o_x_max else x_max
        return intersect_x_min, intersect_x_max
    
    # we first get the dimensions of both solids
    x_min, x_max, y_min, y_max, z_min, z_max = get_dimensions_of_solid( solid )
    o_x_min, o_x_max, o_y_min, o_y_max, o_z_min, o_z_max = get_dimensions_of_solid( other_solid )
    return (*get_dimensions_of_intersect_along_axis(x_min, x_max, o_x_min, o_x_max), 
            *get_dimensions_of_intersect_along_axis(y_min, y_max, o_y_min, o_y_max),
            *get_dimensions_of_intersect_along_axis(z_min, z_max, o_z_min, o_z_max),
            )
    
def intersects_with_solid( solid: Solid, other_solid: Solid ):
    # we first get the dimensions of both solids
    x_min, x_max, y_min, y_max, z_min, z_max = get_dimensions_of_solid( solid )
    o_x_min, o_x_max, o_y_min, o_y_max, o_z_min, o_z_max = get_dimensions_of_solid( other_solid )

    if x_max <= o_x_min or o_x_max <= x_min:
        return False
    if y_max <= o_y_min or o_y_max <= y_min:
        return False
    if z_max <= o_z_min or o_z_max <= z_min:
        return False
    return True

def cutter_handler(plane: ClippingPlane, solid: Solid, new_solids: List[Solid], to_add: int, add=True):
    to_cut = 0 if to_add == 1 else 1
    ans = plane.cut_solid(solid)
    if ans:
        if add:
            new_solids.append( ans[to_add] )
        return ans[to_cut]
    return solid

def get_new_solids( cur_solid: Solid, prev_solid: Solid ):
    prev_new_solids, cur_new_solids = [], []
    solid_to_add = (0, 1, 0, 1, 0, 1)
    solid_add = (True, True, True, True, False, False)
    prev_ans, cur_ans = prev_solid, cur_solid
    for index, plane in enumerate(get_clipping_planes_of_intersection(cur_solid, prev_solid)):
        cur_ans = cutter_handler( plane, cur_ans, prev_new_solids, solid_to_add[index], solid_add[index])
        prev_ans = cutter_handler( plane, prev_ans, cur_new_solids, solid_to_add[index], solid_add[index])
    cur_new_solids.append(cur_ans)
    return cur_new_solids, prev_new_solids


# we start with a VMF that consists of overlapping brushes
vmf = load_vmf('vmfs/preworker_test.vmf')
solids = vmf.get_solids()
prev_solids = [solids[0]]
for cur_i in range(1,len(solids)):
    new_prev_solids = []
    for prev_solid in prev_solids:
        # when a cur_solid overlaps with a prev_solid, then we will cut our cur_solid up into sub solids
        # we will then have to iterate over these instead
        cur_sub_solids = [ solids[cur_i] ]
        new_cur_sub_solids = []
        for cur_sub_solid in cur_sub_solids:
            # when  a cur_solid overlaps with a prev_solid, then we will cut our prev_solid up into sub solids
            # we will then have to iterate over these
            prev_sub_solids = [ prev_solid ]
            new_prev_sub_solids = []
            for prev_sub_solid in prev_sub_solids:
                if intersects_with_solid(cur_sub_solid, prev_sub_solid):
                    cur_sub_sub_solids, prev_sub_sub_solids = get_new_solids(cur_sub_solid, prev_sub_solid)

                else:
                    continue

_vmf = new_vmf()
_vmf.add_solids( *new_solids )
_vmf.export('vmfs/preworker_test_result.vmf')
            
                

            
