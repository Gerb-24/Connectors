from src.PyVMF import *
from main import *
import os

prototypeVMF = load_vmf('vmfs/prototype.vmf')
fileName = 'vmfs/test2.vmf'
search_tex = 'tools/toolsskip'
wall_tex = 'dev/dev_blendmeasure2'
ceiling_tex = 'dev/reflectivity_70'
corner_tex = 'dev/reflectivity_10'
floor_tex = 'orange_dev/dev_measurewall_green03'
nodraw = 'tools/toolsnodraw'
sideTextures = [f"dev/reflectivity_{10*(i+1)}" for i in range(6)]

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

sideDict = {
    "x":    sideTextures[0],
    "y":    sideTextures[1],
    "z":    sideTextures[2],
    "-x":   sideTextures[3],
    "-y":   sideTextures[4],
    "-z":   sideTextures[5],
}

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

    def toWall( self ):
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
            if side.material == sideDict[self.normal].upper():
                side.material = wall_tex
            else:
                side.material = nodraw.upper()
        return proto

class cornerPoint:
    def __init__(self, pos, z_min, z_max, n_1, n_2 ):
        self.pos = pos
        self.z_min, self.z_max = z_min, z_max
        if n_1 in {'x', '-x'}:
            self.n_x, self.n_y = n_1, n_2
        else:
            self.n_x, self.n_y = n_2, n_1

    def toCorner( self ):
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
            if side.material == sideDict[self.n_x].upper() or side.material == sideDict[self.n_y].upper():
                side.material = nodraw.upper()
            elif side.material == sideDict['z'].upper() or side.material == sideDict['-z'].upper():
                side.material = nodraw.upper()
            else:
                side.material = corner_tex.upper()
        return proto

def solidToCeiling( solid: Solid, tot_z_max ):
    proto = createDuplicateVMF(prototypeVMF)
    verts = {
    'x':    VertexManipulationBox( 0, 512, -512, 512, -512, 512).getVerticesInBox(proto),
    'y':    VertexManipulationBox( -512, 512, 0, 512, -512, 512).getVerticesInBox(proto),
    'z':    VertexManipulationBox( -512, 512, -512, 512, 0, 512).getVerticesInBox(proto),
    '-x':   VertexManipulationBox( -512, 0, -512, 512, -512, 512).getVerticesInBox(proto),
    '-y':   VertexManipulationBox( -512, 512, -512, 0, -512, 512 ).getVerticesInBox(proto),
    '-z':   VertexManipulationBox( -512, 512, -512, 512, -512, 0).getVerticesInBox(proto),
    }
    def set_to_zero( verts ):
        for vertex in verts['z']:
            vertex.move(0, 0, -384)
        for vertex in verts['y']:
            vertex.move(0, -384, 0)
        for vertex in verts['x']:
            vertex.move(-384, 0, 0)
        for vertex in verts['-z']:
            vertex.move(0, 0, 384)
        for vertex in verts['-y']:
            vertex.move(0, 384, 0)
        for vertex in verts['-x']:
            vertex.move(384, 0, 0)
    set_to_zero( verts )

    xMin, xMax, yMin, yMax, zMin, zMax = getDimensionsOfSolid( solid )

    for vertex in verts['z']:
        vertex.move(0, 0, tot_z_max + 128)
    for vertex in verts['y']:
        vertex.move(0, yMax, 0)
    for vertex in verts['x']:
        vertex.move(xMax, 0, 0)
    for vertex in verts['-z']:
        vertex.move(0, 0, zMax)
    for vertex in verts['-y']:
        vertex.move(0, yMin, 0)
    for vertex in verts['-x']:
        vertex.move(xMin, 0, 0)

    solid = proto.get_solids()[0]
    for side in solid.get_sides():
        if side.material == sideDict['-z'].upper():
            side.material = ceiling_tex.upper()
        elif side.material == sideDict['z'].upper():
            side.material = nodraw.upper()
        else:
            # side.material = nodraw.upper()
            side.material = wall_tex.upper()
    return proto

def solidToFloor( solid: Solid, tot_z_min ):
    proto = createDuplicateVMF(prototypeVMF)
    verts = {
    'x':    VertexManipulationBox( 0, 512, -512, 512, -512, 512).getVerticesInBox(proto),
    'y':    VertexManipulationBox( -512, 512, 0, 512, -512, 512).getVerticesInBox(proto),
    'z':    VertexManipulationBox( -512, 512, -512, 512, 0, 512).getVerticesInBox(proto),
    '-x':   VertexManipulationBox( -512, 0, -512, 512, -512, 512).getVerticesInBox(proto),
    '-y':   VertexManipulationBox( -512, 512, -512, 0, -512, 512 ).getVerticesInBox(proto),
    '-z':   VertexManipulationBox( -512, 512, -512, 512, -512, 0).getVerticesInBox(proto),
    }
    def set_to_zero( verts ):
        for vertex in verts['z']:
            vertex.move(0, 0, -384)
        for vertex in verts['y']:
            vertex.move(0, -384, 0)
        for vertex in verts['x']:
            vertex.move(-384, 0, 0)
        for vertex in verts['-z']:
            vertex.move(0, 0, 384)
        for vertex in verts['-y']:
            vertex.move(0, 384, 0)
        for vertex in verts['-x']:
            vertex.move(384, 0, 0)
    set_to_zero( verts )

    xMin, xMax, yMin, yMax, zMin, zMax = getDimensionsOfSolid( solid )

    for vertex in verts['z']:
        vertex.move(0, 0, zMin )
    for vertex in verts['y']:
        vertex.move(0, yMax, 0)
    for vertex in verts['x']:
        vertex.move(xMax, 0, 0)
    for vertex in verts['-z']:
        vertex.move(0, 0, tot_z_min - 128)
    for vertex in verts['-y']:
        vertex.move(0, yMin, 0)
    for vertex in verts['-x']:
        vertex.move(xMin, 0, 0)

    solid = proto.get_solids()[0]
    for side in solid.get_sides():
        if side.material == sideDict['z'].upper():
            side.material = floor_tex.upper()
        elif side.material == sideDict['-z'].upper():
            side.material = nodraw.upper()
        else:
            # side.material = nodraw.upper()
            side.material = wall_tex.upper()

    return proto

def getDimensionsOfSolid( solid: Solid ):
    allVertices = solid.get_all_vertices()
    xMin = min([ vertex.x for vertex in allVertices ])
    yMin = min([ vertex.y for vertex in allVertices ])
    zMin = min([ vertex.z for vertex in allVertices ])
    xMax = max([ vertex.x for vertex in allVertices ])
    yMax = max([ vertex.y for vertex in allVertices ])
    zMax = max([ vertex.z for vertex in allVertices ])
    return xMin, xMax, yMin, yMax, zMin, zMax

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

def compile( fileName, search_tex, wall_tex, floor_tex, ceiling_tex, corner_tex ):
    dummyVMF = new_vmf()
    testVMF = load_vmf(fileName)
    solids = [solid for solid in testVMF.get_solids() if solid.has_texture(search_tex)]
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


    for solid in solids:
        dummyVMF = addVMF(dummyVMF, solidToCeiling( solid, tot_z_max ) )
        dummyVMF = addVMF(dummyVMF, solidToFloor( solid, tot_z_min ) )
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

    cp_positions = { cp.pos for cp in corner_points }
    visited = set()
    for ed in edgeDataList:
        ed.corner_points_checks( cp_positions, visited )
        dummyVMF = addVMF(dummyVMF, ed.toWall() )

    for cp in corner_points:
        if cp.pos in visited:
            dummyVMF = addVMF(dummyVMF, cp.toCorner() )

    # dummyVMF.export(f'vmfs/walls.vmf')
    withoutExtension = os.path.splitext(fileName)[0]
    dummyVMF.export(f"{withoutExtension}_connected.vmf")

# compile( fileName, search_tex, wall_tex, floor_tex, ceiling_tex, corner_tex )
