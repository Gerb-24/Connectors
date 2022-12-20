from src.PyVMF import *
from main import *
import os

prototypeVMF = load_vmf('vmfs/prototype.vmf')

leftDict = {
    'y':    'x',
    'x':    '-y',
    '-y':   '-x',
    '-x':   'y',
}

rightDict = {
    'x':    'y',
    '-y':    'x',
   '-x':    '-y',
    'y':    '-x',
}

class Textures:
    def __init__( self ):
        '''side textures'''
        self.x = 'dev/reflectivity_10'.upper()
        self.y = 'dev/reflectivity_20'.upper()
        self.z = 'dev/reflectivity_30'.upper()
        self.neg_x = 'dev/reflectivity_40'.upper()
        self.neg_y = 'dev/reflectivity_50'.upper()
        self.neg_z = 'dev/reflectivity_60'.upper()

        '''default textures'''
        self.nodraw = 'tools/toolsnodraw'.upper()
        self.trigger = 'tools/toolstrigger'.upper()
        self.black = 'tools/toolsblack'.upper()

        self.end = 'u24_tools/toolsend'.upper()
        self.end_back = 'u24_tools/toolsendback'.upper()

        self.dest = 'u24_tools/toolsdest'.upper()
        self.dest_front = 'u24_tools/toolsdestfront'.upper()
        self.dest_side = 'u24_tools/toolsdestside'.upper()

        ''' jump textures '''
        self.tele = ''  # used for surfaces with a tele

        ''' connectors textures '''
        self.side = ''  # used for nonaded surfaces
        self.wall = ''   # the texture for the walls
        self.corner = ''    # the texture for a corner
        self.floor = ''     # the texture for a teled floor
        self.search = ''    # the texture to search for when building connectors

    def load_textures( self, texture_list ):
        search_tex, wall_tex, floor_tex, ceiling_tex, corner_tex, tele_tex = texture_list
        self.wall = wall_tex
        self.ceiling = ceiling_tex
        self.corner = corner_tex
        self.floor = floor_tex
        self.search = search_tex
        self.tele = tele_tex

        return self

    def to_side( self, s ):
        side_dict = {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "-x": self.neg_x,
            "-y": self.neg_y,
            "-z": self.neg_z,
        }

        return side_dict[ s ]

    def to_sides( self, *args ):
        return { self.to_side(s) for s in args }

    def to_key( self, side ):
        key_dict = {
            self.x:         'x',
            self.y:         'y',
            self.z:         'z',
            self.neg_x:     '-x',
            self.neg_y:     '-y',
            self.neg_z:     '-z',
        }
        return key_dict[ side ]

    def mat_to_dic( self, proto, mat_dic ):
        solid = proto.get_solids()[0]
        pre_mat_dic = {
            "x":    self.nodraw,
            "y":    self.nodraw,
            "z":    self.nodraw,
            "-x":   self.nodraw,
            "-y":   self.nodraw,
            "-z":   self.nodraw,
        }
        for key in mat_dic:
            pre_mat_dic[key] = mat_dic[key]
        for side in solid.get_sides():
            side.material = pre_mat_dic[ self.to_key( side.material ) ]

class Triggers:
    def create( self, solids, textures ):
        dim_tuple = getMaxDimensionsOfList(solids)
        xMin, xMax, yMin, yMax, zMin, zMax = dim_tuple
        o_xMin, o_xMax, o_yMin, o_yMax, o_zMin, o_zMax = getDimensionsOfSolid( solids[0] )
        proto = createDuplicateVMF(prototypeVMF)
        verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()
        verts.full_move( xMax, yMax, zMax, xMin, yMin, zMin )
        for direction in verts.verticesDict:
            for vertex in verts.verticesDict[ direction ]:
                vertex.move( *verts.getMove( direction, 4*128 ) )

        solid = proto.get_solids()[0]
        solid.set_texture( textures.trigger )

        regen_dic = {
            'classname':    'func_regenerate',
        }
        regen_ent = Entity(dic=regen_dic)
        regen_ent.solids.append( solid )

        hurt_dic = {
            'origin':       f'{ (o_xMax + o_xMin)//2 } { (o_yMax + o_yMin)//2 } {(o_zMax + o_zMin)//2}',
            'classname':    'trigger_hurt',
            'damage':       '-9999999'
        }

        hurt_ent = Entity(dic=hurt_dic)
        hurt_ent.solids.append( solid )

        proto = new_vmf()
        proto.add_entities(*[regen_ent, hurt_ent])

        val = 5*128
        dim_tuple = xMin - val, xMax + val, yMin - val, yMax + val, zMin - val, zMax + val
        return proto, dim_tuple

class BrushVertexManipulationBox:

    def __init__( self, proto ):
        self.proto = proto
        self.boxes = self.createBoxesDict()

    def createBoxesDict( self ):
        verts = {
        'x':    VertexManipulationBox( 0, 512, -512, 512, -512, 512),
        'y':    VertexManipulationBox( -512, 512, 0, 512, -512, 512),
        'z':    VertexManipulationBox( -512, 512, -512, 512, 0, 512),
        '-x':   VertexManipulationBox( -512, 0, -512, 512, -512, 512),
        '-y':   VertexManipulationBox( -512, 512, -512, 0, -512, 512 ),
        '-z':   VertexManipulationBox( -512, 512, -512, 512, -512, 0),
        }
        return verts

    def createVerticesInBoxDict( self ):
        '''Creates a dictionary of lists of vertices that are contained in the given VMB'''
        verticesDict = { key: self.boxes[key].getVerticesInBox( self.proto ) for key in self.boxes }
        return VerticesToManipulate( verticesDict )

class VerticesToManipulate:
    def __init__( self, verticesDict ):
        self.verticesDict = verticesDict

    def getMove( self, direction, value ):
        moveDict = {
        'x': (value, 0, 0),
        'y': (0, value, 0),
        'z': (0, 0, value),
        '-x': (-value, 0, 0),
        '-y': (0, -value, 0),
        '-z': (0, 0, -value),
        }
        return moveDict[ direction ]

    def translate( self, x, y, z ):
        moveDict = {
        'x': (x, 0, 0),
        'y': (0, y, 0),
        'z': (0, 0, z),
        '-x': (x, 0, 0),
        '-y': (0, y, 0),
        '-z': (0, 0, z),
        }

        for direction in self.verticesDict:
            for vertex in self.verticesDict[ direction ]:
                vertex.move( *moveDict[ direction ] )

    def full_move( self, a, b, c, d, e, f ):
        moveDict = {
        'x': (a, 0, 0),
        'y': (0, b, 0),
        'z': (0, 0, c),
        '-x': (d, 0, 0),
        '-y': (0, e, 0),
        '-z': (0, 0, f),
        }

        for direction in self.verticesDict:
            for vertex in self.verticesDict[ direction ]:
                vertex.move( *moveDict[ direction ] )

    def moveToZero( self ):
        for direction in self.verticesDict:
            for vertex in self.verticesDict[ direction ]:
                vertex.move( *self.getMove( direction, -384 ) )

        return self

    def move_to_dic( self, move_dic ):
        for key in move_dic:
            for vertex in self.verticesDict[ key ]:
                vertex.move( *self.getMove( key, move_dic[ key ] ))

class edgeData:
    def __init__(self, normal, pos,  _min, _max, z_min, z_max ):
        self.normal = normal
        self.pos = int(pos)
        self.interval = ( _min, _max )
        self.height_interval = ( z_min, z_max )

    def get_start( self ):
        if self.normal in {'x', '-x'}:
            return ( self.pos, self.interval[0] )
        return ( self.interval[0], self.pos )

    def get_end( self ):
        if self.normal in {'x', '-x'}:
            return ( self.pos, self.interval[1] )
        return ( self.interval[1], self.pos )

    def corner_points_checks( self, corner_points, visited ):
        start, end = self.get_start(), self.get_end()
        if start in corner_points:
            self.interval = (self.interval[0] + 128, self.interval[1])
            visited.add( start )
        if end in corner_points:
            self.interval = (self.interval[0], self.interval[1] - 128)
            visited.add( end )

    def change_interval( self, new_min, new_max ):

        ed = edgeData(
            self.normal,
            self.pos,
            new_min,
            new_max,
            self.height_interval[0],
            self.height_interval[1]
        )
        return ed

    def toWall( self, textures ):
        proto = createDuplicateVMF(prototypeVMF)
        verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()

        verts.full_move( 0, 0, self.height_interval[1], 0, 0, self.height_interval[0] )

        if self.normal == 'x':
            verts.full_move( self.pos, self.interval[1], 0, self.pos - 128, self.interval[0], 0  )

        elif self.normal == 'y':
            verts.full_move( self.interval[1], self.pos, 0, self.interval[0], self.pos - 128, 0  )

        elif self.normal == '-x':
            verts.full_move( self.pos + 128, self.interval[1], 0, self.pos, self.interval[0], 0  )

        elif self.normal == '-y':
            verts.full_move( self.interval[1], self.pos + 128, 0, self.interval[0], self.pos, 0  )

        solid = proto.get_solids()[0]
        for side in solid.get_sides():
            if side.material in textures.to_sides( self.normal ):
                side.material = textures.wall
            else:
                side.material = textures.nodraw.upper()
        return proto

class cornerPoint:
    def __init__(self, pos, z_min, z_max, n_1, n_2 ):
        self.pos = pos
        self.z_min, self.z_max = z_min, z_max
        if n_1 in {'x', '-x'}:
            self.n_x, self.n_y = n_1, n_2
        else:
            self.n_x, self.n_y = n_2, n_1

    def toCorner( self, textures ):
        proto = createDuplicateVMF(prototypeVMF)
        verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()

        verts.translate( *self.pos, 0 )
        normalsDict = {
        'x':    ( -128, 0, 0, 0, 0, 0 ),
        'y':    ( 0, -128, 0, 0, 0, 0 ),
        '-x':   ( 0, 0, 0, 128, 0, 0 ),
        '-y':   ( 0, 0, 0, 0, 128, 0 ),
        }
        verts.full_move( *normalsDict[self.n_x] )
        verts.full_move( *normalsDict[self.n_y] )
        verts.full_move( 0, 0, self.z_max, 0, 0, self.z_min )

        solid = proto.get_solids()[0]
        for side in solid.get_sides():
            if side.material in textures.to_sides( self.n_x , self.n_y, 'z', '-z'):
                side.material = textures.nodraw
            else:
                side.material = textures.corner
        return proto

def solidToCeiling( solid: Solid, tot_z_max, textures, nodraw ):
    proto = createDuplicateVMF(prototypeVMF)
    verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()

    xMin, xMax, yMin, yMax, zMin, zMax = getDimensionsOfSolid( solid )

    verts.full_move( xMax, yMax, tot_z_max + 128, xMin, yMin, zMax )

    solid = proto.get_solids()[0]
    if nodraw:
        for side in solid.get_sides():
            if side.material == textures.neg_z:
                side.material = textures.ceiling
            else:
                side.material = textures.nodraw
    else:
        for side in solid.get_sides():
            if side.material == textures.neg_z:
                side.material = textures.ceiling
            elif side.material == textures.z:
                side.material = textures.nodraw
            else:
                side.material = textures.wall
    return proto

def solidToFloor( solid: Solid, tot_z_min, filename, textures, type, nodraw ):
    # create the floor brush
    proto = createDuplicateVMF(prototypeVMF)
    verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()
    xMin, xMax, yMin, yMax, zMin, zMax = getDimensionsOfSolid( solid )
    verts.full_move( xMax, yMax, zMin, xMin, yMin, tot_z_min - 128 )

    # texture the floor brush
    solid = proto.get_solids()[0]
    if nodraw:
        for side in solid.get_sides():
            if side.material == textures.z:
                side.material = textures.floor
            else:
                side.material = textures.nodraw
    else:
        for side in solid.get_sides():
            if side.material == textures.z:
                side.material = textures.floor
            elif side.material == textures.neg_z:
                side.material = textures.nodraw
            else:
                side.material = textures.wall
    # if it is a standard connector, then we are done
    if type == 'standard':
        return proto

    # create the teleport brush and the catapult brush
    proto2 = createDuplicateVMF(prototypeVMF)
    verts = BrushVertexManipulationBox( proto2 ).createVerticesInBoxDict().moveToZero()
    verts.full_move( xMax, yMax, zMin+64, xMin, yMin, zMin )

    # give it the trigger texture
    solid = proto2.get_solids()[0]
    for side in solid.get_sides():
        side.material = textures.trigger.upper()
    target = os.path.splitext(os.path.basename(filename))[0]

    # create the trigger_teleport
    tele_dic = {
        'classname':    'trigger_teleport',
        'target':       target

    }
    tele_ent = Entity(dic=tele_dic)
    tele_ent.solids.append( solid )

    # create the trigger_catapult
    _solid = solid.copy()
    cata_dic = {
        'classname':    'trigger_catapult',
        'playerSpeed':  '0'
    }
    cata_ent = Entity(dic=cata_dic)
    cata_ent.solids.append( _solid )
    proto.add_entities(*[tele_ent, cata_ent])
    
    return proto

def getEdgeDataOfSolid( solid: Solid ):
    xMin, xMax, yMin, yMax, zMin, zMax = getDimensionsOfSolid( solid )
    solid_ed_dict = {
        'x':    edgeData( 'x', xMin, yMin, yMax, zMin, zMax ),
        '-x':   edgeData( '-x', xMax, yMin, yMax, zMin, zMax ),
        'y':    edgeData( 'y', yMin, xMin, xMax, zMin, zMax ),
        '-y':   edgeData( '-y', yMax, xMin, xMax, zMin, zMax ),
    }

    solid_data = [ solid_ed_dict[key] for key in solid_ed_dict ]
    return solid_data

def createSkipTeleport( solid: Solid, filename, textures: Textures ):
    # get dimensions
    side = solid.get_texture_sides( textures.tele )[0]
    xMin, xMax, yMin, yMax, z, _ = getDimensionsOfSide( side )
    
    # create the teleport brush and the catapult brush
    proto = createDuplicateVMF(prototypeVMF)
    verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()
    verts.full_move( xMax, yMax, z+1, xMin, yMin, z )

    # give it the trigger texture
    solid = proto.get_solids()[0]
    for side in solid.get_sides():
        side.material = textures.trigger.upper()
    target = os.path.splitext(os.path.basename(filename))[0]

    # create the trigger_teleport
    tele_dic = {
        'classname':    'trigger_teleport',
        'target':       target

    }
    tele_ent = Entity(dic=tele_dic)
    tele_ent.solids.append( solid )

    # create the trigger_catapult
    _solid = solid.copy()
    cata_dic = {
        'classname':    'trigger_catapult',
        'playerSpeed':  '0'
    }
    cata_ent = Entity(dic=cata_dic)
    cata_ent.solids.append( _solid )
    proto.add_entities(*[tele_ent, cata_ent])
    
    return proto

def createDestination( solid: Solid, filename, textures: Textures, spawn ):
    proto = new_vmf()
    dest_front = solid.get_texture_sides( textures.dest_front )[0]
    dest_side = solid.get_texture_sides( textures.dest_side )[0]
    xMin_f, xMax_f, yMin_f, yMax_f, zMin, _ = getDimensionsOfSide( dest_front )
    xMin_s, xMax_s, yMin_s, yMax_s, _, _ = getDimensionsOfSide( dest_side )
    if xMin_f == xMax_f:
        x = xMin_f
        if yMin_s == yMin_f:
            y = yMin_s
            coord = ( x - 2*128, y + 64 )
            deg = 0
        elif yMax_s == yMax_f:
            y = yMax_s
            coord = ( x + 2*128, y - 64 )
            deg = 180
    elif yMin_f == yMax_f:
        y = yMin_f
        if xMin_s == xMin_f:
            x = xMin_s
            coord = ( x + 64 , y + 2*128 )
            deg = 270
        if xMax_s == xMax_f:
            x = xMax_s
            coord = ( x - 64 , y - 2*128 )
            deg = 90
    target = os.path.splitext(os.path.basename(filename))[0]
    dic = {
            'classname':    'info_teleport_destination',
            'origin':       f'{coord[0]} {coord[1]} {zMin + 1}',
            'angles':       f'0 {deg} 0',
        	'targetname':   target,
        }
    dest = Entity(dic=dic)
    entity_list = [ dest ]
    if spawn:
        spawn_dic = {
            'classname':    'info_player_teamspawn',
            'origin':       f'{coord[0]} {coord[1]} {zMin + 1}',
            'angles':       f'0 {deg} 0',
        }
        spawn_ent = Entity(dic=spawn_dic)
        entity_list.append( spawn_ent )
    proto.add_entities( *entity_list )
    return proto

def createEnd( solid: Solid, filename, textures: Textures ):
    def create_tele( coord, dir, filename, textures ):
        proto = createDuplicateVMF(prototypeVMF)
        verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()
        verts.translate( *coord )
        dir_r, dir_l, dir_opp = direction_dict[ dir ][ 'l' ], direction_dict[ dir ][ 'r' ], direction_dict[ dir ][ 'o' ]
        move_dic = {
            dir_r:     0.5*128+8,
            dir_l:      0.5*128+8,
            dir_opp:    32+8,
            'z':        1.5*128+8,
        }
        verts.move_to_dic( move_dic )

        solid = proto.get_solids()[0]
        solid.set_texture( textures.trigger )

        target = os.path.splitext(os.path.basename(filename))[0]
        tele_dic = {
            'classname':    'trigger_teleport',
            'target':       target

        }
        tele_ent = Entity(dic=tele_dic)
        tele_ent.solids.append( solid )
        proto = new_vmf()
        proto.add_entities(*[tele_ent])

        return proto
    
    def create_tele_door( coord, dir, textures ):
        proto = createDuplicateVMF(prototypeVMF)
        verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()
        verts.translate( *coord )

        dir_r = direction_dict[ dir ][ 'r' ]
        dir_l = direction_dict[ dir ][ 'l' ]
        dir_opp = direction_dict[ dir ][ 'o' ]
        move_dic = {
            dir_r:     0.5*128,
            dir_l:      0.5*128,
            dir_opp:    32,
            'z':        1.5*128,
        }
        verts.move_to_dic( move_dic )

        mat_dic = {
            'z':        textures.black,
            dir_opp:    textures.black,
            dir_l:      textures.black,
            dir_r:      textures.black
        }
        textures.mat_to_dic( proto, mat_dic )

        return proto

    # determine coord
    end_back = solid.get_texture_sides( textures.end_back )[0] 
    xMin, xMax, yMin, yMax, zMin, _ = getDimensionsOfSolid( solid )
    xMin_s, xMax_s, yMin_s, yMax_s, _, _ = getDimensionsOfSide( end_back )

    coord = ( (xMax_s + xMin_s)//2, (yMax_s + yMin_s)//2, zMin )

    # determining the direction
    if xMin_s == xMax_s:
        x = xMin_s
        if x == xMin:
            dir = '-x'
        elif x == xMax:
            dir = 'x'
    elif yMin_s == yMax_s:
        y = yMin_s
        if y == yMin:
            dir = '-y'
        elif y == yMax:
            dir = 'y'

    # create tele and tele door
    tot_proto = create_tele( coord, dir, filename, textures )
    tot_proto = addVMF( tot_proto, create_tele_door( coord, dir, textures ) )

    return tot_proto

def compile( type, filename, next_filename, textures: Textures, nodraw, spawn=False ):
    dummyVMF = new_vmf()
    testVMF = load_vmf(filename)
    solids = [solid for solid in testVMF.get_solids() if solid.has_texture(textures.search)]
    solids_to_remove = []
    solids_to_remove.extend( solids )

    # all the things we do for jump that we do not do for standard
    if type == 'jump':
        # create trigger_teleports on top of skips
        tele_solids = [solid for solid in testVMF.get_solids() if solid.has_texture( textures.tele )]
        for solid in tele_solids:
            dummyVMF = addVMF( dummyVMF, createSkipTeleport( solid, filename, textures ) )


        # create the info_teleport_destination
        dest_solids = [solid for solid in testVMF.get_solids() if solid.has_texture( textures.dest )]
        dest_solid = dest_solids[0]
        dummyVMF = addVMF( dummyVMF, createDestination( dest_solid, filename, textures, spawn ) )
        solids_to_remove.extend( dest_solids )

        # create the end teleport
        end_solids = [solid for solid in testVMF.get_solids() if solid.has_texture( textures.end )]
        end_solid = end_solids[0]
        dummyVMF = addVMF( dummyVMF, createEnd( end_solid, next_filename, textures ) )
        solids_to_remove.extend( end_solids )

        # create trigger_hurt and func_regenerate
        if type == 'jump':
            tiggerVMF, dim_tuple = Triggers().create( solids, textures ) 
            dummyVMF = addVMF( dummyVMF, tiggerVMF )

    edgeDataList = []
    tot_z_min, tot_z_max = None, None
    for solid in solids:
        _, _, _, _, zMin, zMax = getDimensionsOfSolid( solid )
        if tot_z_min != None:
            tot_z_min = min( zMin, tot_z_min )
        else:
            tot_z_min = zMin
        if tot_z_max != None:
            tot_z_max = max( zMax, tot_z_max )
        else:
            tot_z_max = zMax

    # create the ceiling and the floor
    for solid in solids:
        dummyVMF = addVMF( dummyVMF, solidToCeiling( solid, tot_z_max, textures, nodraw ) )
        dummyVMF = addVMF( dummyVMF, solidToFloor( solid, tot_z_min, filename, textures, type, nodraw ) )
        edgeDataList.extend(getEdgeDataOfSolid(solid))
    
    ed_x_dict = {}
    ed_y_dict = {}
    for ed in edgeDataList:
        if ed.normal == 'x' or ed.normal == '-x':
            if ed.pos not in ed_x_dict:
                ed_x_dict[ ed.pos ] = [ ed ]
            else:
                ed_x_dict[ ed.pos ].append( ed )
        else:
            if ed.pos not in ed_y_dict:
                ed_y_dict[ ed.pos ] = [ ed ]
            else:
                ed_y_dict[ ed.pos ].append( ed )

    def change_ed_dict( ed_dict, x_or_y ):
        corner_points = []
        def add_corner_point( pos, val, bot, top, n_1, n_2 ):
            if x_or_y == 'x':
                corner_points.append( cornerPoint( (pos, val), bot, top, n_1, n_2 ) )
            else:
                corner_points.append( cornerPoint( (val, pos), bot, top, n_1, n_2 ) )


        for key in ed_dict:
            if len( ed_dict[key] ) > 1:

                intervals = ed_dict[key]
                intervals.sort( key= lambda ed: ed.interval[0] )
                new_intervals = []
                i = 0
                while i < len( intervals ) - 1:
                    cur, next = intervals[i].interval, intervals[i + 1].interval # the current interval and the interval next in line
                    cur_n, next_n = intervals[i].normal, intervals[i+1].normal
                    cur_h, next_h = intervals[i].height_interval, intervals[i+1].height_interval
                    bot, top = min( cur_h[0], next_h[0] ), max( cur_h[1], next_h[1] )
                    end_condition = True

                    if cur[1] < next[1]:
                        if cur[1] < next[0]:        # Disjoint
                            new_intervals.append( intervals[i] )

                        elif cur[1] == next[0]:     # Touching
                            new_intervals.append( intervals[i] )

                        elif cur[0] < next[0]:      # Partial Overlap
                            new_intervals.append( intervals[i].change_interval( cur[0], next[0]))
                            intervals[i+1] = intervals[i+1].change_interval( cur[1], next[1])
                            if cur_n in { 'y', '-x' }:
                                n_1, n_2 = cur_n, leftDict[cur_n]
                                n_3, n_4 = next_n, leftDict[next_n]
                            else:
                                n_1, n_2 = cur_n, rightDict[cur_n]
                                n_3, n_4 = next_n, rightDict[next_n]
                            add_corner_point( key, next[0], bot, top, n_1, n_2 )
                            add_corner_point( key, cur[1], bot, top, n_3, n_4 )

                        elif cur[0] == next[0]:     # Start overlap on cur
                            intervals[i+1] = intervals[i+1].change_interval( cur[1], next[1])
                            if cur_n in { 'y', '-x' }:
                                n_1, n_2 = next_n, leftDict[next_n]
                            else:
                                n_1, n_2 = next_n, rightDict[next_n]
                            add_corner_point( key, cur[1], bot, top, n_1, n_2 )


                    elif cur[1] == next[1]:
                        if cur[0] < next[0]:        # Total overlap on next
                            new_intervals.append( intervals[i].change_interval( cur[0], next[0] ))
                            if cur_n in { 'y', '-x' }:
                                n_1, n_2 = cur_n, leftDict[cur_n]
                            else:
                                n_1, n_2 = cur_n, rightDict[cur_n]
                            add_corner_point( key, next[0], bot, top, n_1, n_2 )
                            i += 1

                        elif cur[0] == next[0]:     # Total overlap on both
                            i += 2
                            continue

                    elif cur[1] > next[1]:
                        if cur[0] < next[0]:        # Mid overlap
                            new_intervals.append( intervals[i].change_interval( cur[0], next[0]))
                            intervals[i+1] = intervals[i].change_interval(next[1], cur[1])
                            if cur_n in { 'y', '-x' }:
                                n_1, n_2 = cur_n, leftDict[cur_n]
                                n_3, n_4 = cur_n, rightDict[cur_n]
                            else:
                                n_1, n_2 = cur_n, rightDict[cur_n]
                                n_3, n_4 = cur_n, leftDict[cur_n]
                            add_corner_point( key, next[0], bot, top, n_1, n_2 )
                            add_corner_point( key, next[1], bot, top, n_3, n_4 )

                        elif cur[0] == next[0]:     # Start overlap
                            intervals[i+1] = intervals[i].change_interval( next[1], cur[1] )
                            if cur_n in { 'y', '-x' }:
                                n_1, n_2 = cur_n, rightDict[cur_n]
                            else:
                                n_1, n_2 = cur_n, leftDict[cur_n]
                            add_corner_point( key, next[1], bot, top, n_1, n_2 )

                    # here we add the last segement as there is no next
                    if end_condition and i == len( intervals ) - 2:
                        new_intervals.append( intervals[i+1] )
                    i += 1
                ed_dict[key] = new_intervals
        return corner_points

    corner_points_x = change_ed_dict( ed_x_dict, 'x' )
    corner_points_y = change_ed_dict( ed_y_dict, 'y' )

    corner_points = corner_points_x.copy()
    corner_points.extend( corner_points_y )

    edgeDataList = []
    for key in ed_x_dict:
        edgeDataList.extend(ed_x_dict[key])
    for key in ed_y_dict:
        edgeDataList.extend(ed_y_dict[key])

    # create the walls
    cp_positions = { cp.pos for cp in corner_points }
    visited = set()
    for ed in edgeDataList:
        ed.corner_points_checks( cp_positions, visited )
        dummyVMF = addVMF(dummyVMF, ed.toWall( textures ) )

    # add corners at each of the corner points
    for cp in corner_points:
        if cp.pos in visited:
            dummyVMF = addVMF(dummyVMF, cp.toCorner( textures ) )

    # we remove our data and add the results
    testVMF = removeSolids( testVMF, solids_to_remove )
    testVMF = addVMF( testVMF, dummyVMF )

    # for jump, we also need dim_tuple to get the max dimensions of each jump
    if type == 'standard':
        return testVMF
    if type == 'jump':
        return testVMF, dim_tuple

def compile_multiple( type, root, files, texture_list, nodraw ):
    textures = Textures().load_textures( texture_list )
    if type == 'standard':
        file = files[0]
        vmf = compile( type, file, '', textures, nodraw )
        withoutExtension = os.path.splitext(file)[0]
        vmf.export( f"{withoutExtension}_connected.vmf" )
    if type == 'jump':
        max_width, max_length, max_height = 0, 0, 0
        vmf_list = []
        for ind, file in enumerate(files):
            # we want to spawn at the first jump
            spawn = True if ind == 0 else False

            next_file = files[ (ind+1)%len(files) ]
            jump_vmf, dim_tuple = compile( type, file, next_file, textures, nodraw, spawn=spawn )
            a, a_max, b, b_max, c, c_max = dim_tuple
            a_rel, b_rel, c_rel = a_max - a, b_max - b, c_max - c

            # update the max_values
            max_width = max( max_width, a_rel )
            max_length = max( max_length, b_rel )
            max_height = max( max_height, c_rel )

            # get it so that it is all in one quadrant
            moveVMF( jump_vmf, (-a, -b, -c ) )

            # 100*128 feel like a good size for the radius of the cube to build in
            cube_radius = 100*128
            moveVMF( jump_vmf, (-cube_radius, -cube_radius, -cube_radius ) )

            vmf_list.append( jump_vmf )
        tot_vmf = new_vmf()

        i, j, k = 0, 0, 0
        for vmf in vmf_list:
            # first we iterate over the x-axis, then the y-axis, then the z-axis
            if ( i + 1 ) * max_width > 200*128:
                i = 0
                j += 1
            if ( j + 1 ) * max_length > 200*128:
                j = 0
                k += 1
            moveVMF( vmf, ( i * max_width , j * max_length, k * max_height ) )
            i += 1
            tot_vmf = addVMF( tot_vmf, vmf )
        map_name = os.path.basename(root)
        tot_vmf.export(os.path.join( root, f'jump_{map_name}_a1.vmf'))

