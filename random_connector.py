from random import randint, choice
import os
from src.PyVMF import *
from main import  createDuplicateVMF, addVMF
from sidewalls import BrushVertexManipulationBox, Textures

def get_dimensions_of_side( side: Side ):
    allVertices = side.get_vertices()
    xMin = min([ vertex.x for vertex in allVertices ])
    yMin = min([ vertex.y for vertex in allVertices ])
    zMin = min([ vertex.z for vertex in allVertices ])
    xMax = max([ vertex.x for vertex in allVertices ])
    yMax = max([ vertex.y for vertex in allVertices ])
    zMax = max([ vertex.z for vertex in allVertices ])
    return xMin, xMax, yMin, yMax, zMin, zMax

def get_dimensions_of_solid( solid: Solid ):
    allVertices = solid.get_all_vertices()
    xMin = min([ vertex.x for vertex in allVertices ])
    yMin = min([ vertex.y for vertex in allVertices ])
    zMin = min([ vertex.z for vertex in allVertices ])
    xMax = max([ vertex.x for vertex in allVertices ])
    yMax = max([ vertex.y for vertex in allVertices ])
    zMax = max([ vertex.z for vertex in allVertices ])
    return xMin, xMax, yMin, yMax, zMin, zMax

def is_in_solid( x, y, z, solid: Solid ):
    x_min, x_max, y_min, y_max, z_min, z_max = get_dimensions_of_solid( solid )
    if not x in range( x_min//128, x_max//128 + 1 ):
        return False
    if not y in range( y_min//128, y_max//128 + 1 ):
        return False
    if not z in range( z_min//128, z_max//128 + 1 ):
        return False
    return True

def intersects_with_solid( solid: Solid, other_solid: Solid ):
    x_min, x_max, y_min, y_max, z_min, z_max = get_dimensions_of_solid( solid )
    o_x_min, o_x_max, o_y_min, o_y_max, o_z_min, o_z_max = get_dimensions_of_solid( other_solid )
    o_x_range = range( o_x_min//128, o_x_max//128 + 1 )
    o_y_range = range( o_y_min//128, o_y_max//128 + 1 )
    o_z_range = range( o_z_min//128, o_z_max//128 + 1 )

    # the following is not intirely what we want, but its at least something
    if x_min//128 not in o_x_range and x_max//128 not in o_x_range:
        return False
    if y_min//128 not in o_y_range and y_max//128 not in o_y_range:
        return False
    if z_min//128 not in o_z_range and z_max//128 not in o_z_range:
        return False
    return True

def create_random_connector( dirname, min_width, max_width, min_height, max_height, brush_amount ):
    open_val = 2    
    # min_width, max_width = 4, 10
    # min_height, max_height = 4, 10
    # brush_amount = 10

    prototype_vmf = load_vmf('vmfs/prototype.vmf')
    dummy_vmf = new_vmf()
    skip_tex = 'tools/toolsskip'
    textures = Textures()

    # create initial brush
    proto = createDuplicateVMF(prototype_vmf)
    verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()
    verts.full_move(
        randint( min_width, max_width )*128,
        randint( min_width, max_width )*128,
        randint( min_height, max_height )*128,
        0,
        0,
        0,
    )

    dummy_vmf = addVMF( dummy_vmf, proto )

    brush_count = 2
    while brush_count <= brush_amount:
    # now choose a solid, then a side, then a vertex inside of the solid
        solid = choice( dummy_vmf.get_solids() )
        
        direction = choice( ['x', 'y', '-x', '-y'] )
        counter_direction = choice(['x','-x']) if direction in { 'y', '-y' } else choice(['y', '-y'])
        z_direction = choice(['z','-z'])
        side = solid.get_texture_sides( textures.to_side( direction ) )[0]
        xMin, xMax, yMin, yMax, zMin, zMax = get_dimensions_of_side( side )

        # create a new brush that starts on the edge
        proto = createDuplicateVMF(prototype_vmf)
        verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()

        x_val = randint( xMin//128 + open_val, xMax//128 - open_val )*128 if xMax != xMin else xMax
        y_val = randint( yMin//128 + open_val, yMax//128 - open_val )*128 if yMax != yMin else yMax
        z_val = randint( zMin//128 + open_val, zMax//128 - open_val)*128

        # check that the starting coordinate is not already on the boundary of another brush
        other_solids = [ s for s in dummy_vmf.get_solids() if s!= solid ]
        if any([ is_in_solid( x_val, y_val, z_val, s ) for s in other_solids ]):
            print('start coord is in solid')
            continue

        verts.translate(
            x_val,
            y_val,
            z_val,
        )

        move_dic = {
            direction: randint( min_width, max_width )*128,
            counter_direction: randint( min_width, max_width )*128,
            z_direction: randint( min_height, max_height )*128,
        }
        verts.move_to_dic( move_dic )
        # check that the solid does not intersect with any other solid
        new_solid = proto.get_solids()[0]
        if any([ intersects_with_solid( new_solid, s ) for s in other_solids ]):
            print('intersects with solid')
            continue

        dummy_vmf = addVMF( dummy_vmf, proto )
        brush_count += 1

    for solid in dummy_vmf.get_solids():
        solid.set_texture(skip_tex.upper())

    # finnaly we export it
    filepath = os.path.join( dirname, f'rg_connector.vmf')
    dummy_vmf.export( filepath )
    return filepath