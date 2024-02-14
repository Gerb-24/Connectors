from src.PyVMF import *
from main import *
from sidewalls import prototypeVMF, BrushVertexManipulationBox, Textures

class AbstractBrush:
    def __init__( self, move_dic, mat_dic ):
        self.move_dic = move_dic
        self.mat_dic = mat_dic

    def create( self, coord, textures, combined = None ):
        proto = createDuplicateVMF(prototypeVMF)
        verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()
        verts.translate( *coord )
        verts.move_to_dic( self.move_dic )
        textures.mat_to_dic( proto, self.mat_dic )

        if combined:
            for vertex in verts.verticesDict[ combined['keys'][ 0 ] ]:
                if vertex in verts.verticesDict[ combined['keys'][ 1 ] ]:
                    vertex.move( *verts.getMove( 'z', combined['val'] ))

        return proto

class FaceData:
    def __init__(self, normal, pos,  dims):
        self.normal = normal
        self.pos = int(pos)
        self.dims = dims
        self.x1_min, self.x1_max, self.x2_min, self.x2_max = self.dims

        ''' data for new faces '''
        self.parents = []
        self.additional_colored_directions = set([])

        ''' data for starting brushes '''
        self.x1, self.x2 = None, None
        self.children = None
        self.next = None

    def __str__(self) -> str:
        s = f'''FACE(
    normal = {self.normal}
    pos = {self.pos}
    dims = {self.dims}
)'''
        return s

    def initial_faces( self, cube_list ):
        self.x1, self.x2 = NORMAL_TO_AXES(self.normal)
        self.children = {
            DIRECTION_HANDLER(self.x1, 'o'):    [],
            self.x1:                            [],
            DIRECTION_HANDLER(self.x2, 'o'):    [],
            self.x2:                            [],
        }
        self.next = {
            DIRECTION_HANDLER(self.x1, 'o'):    cube_list[DIRECTION_HANDLER(self.x1, 'o')],
            self.x1:                            cube_list[self.x1],
            DIRECTION_HANDLER(self.x2, 'o'):    cube_list[DIRECTION_HANDLER(self.x2, 'o')],
            self.x2:                            cube_list[self.x2],
        }
        
    def has_intersection( self, fd ):
        x1_min, x1_max, x2_min, x2_max = fd.dims
        if x1_min >= self.x1_max or x2_min >= self.x2_max or x1_max <= self.x1_min or x2_max <= self.x2_min:
            return
        
        fd.normal = self.normal
        fd.parents.append(self)
        if x1_min == self.x1_min:
            self.children[DIRECTION_HANDLER(self.x1, 'o')].append( fd )
        if x1_max == self.x1_max:
            self.children[self.x1].append( fd )
        if x2_min == self.x2_min:
            self.children[DIRECTION_HANDLER(self.x2, 'o')].append( fd )
        if x2_max == self.x2_max:
            self.children[self.x2].append( fd )
        
    def has_zero_volume( self ):
        return (self.x1_min >= self.x1_max or self.x2_min >= self.x2_max)

    def to_wall( self, textures ):
        if self.has_zero_volume():
            proto = new_vmf()
            return proto

        materials_dictionary = {
                self.normal:                            NORMAL_TO_TEXTURE(self.normal),
            }
        for direction in self.additional_colored_directions:
            materials_dictionary[direction] = NORMAL_TO_TEXTURE(direction)

        x1, x2 = NORMAL_TO_AXES( self.normal )
        sign = DIRECTION_IS_POSITIVE( self.normal )
        move_dictionary = {
            self.normal:                                -1*sign*self.pos,
            DIRECTION_HANDLER(self.normal, 'o'):        sign*(self.pos + sign*128),
            x1:                                         self.x1_max,
            DIRECTION_HANDLER(x1, 'o'):                 -1*self.x1_min,
            x2:                                         self.x2_max,
            DIRECTION_HANDLER(x2, 'o'):                 -1*self.x2_min,
        }
        proto = AbstractBrush(move_dictionary, materials_dictionary).create( (0, 0, 0), textures )
        return proto

def DICT_LIST_HELPER( dict, key, obj ):
    if key not in dict:
        dict[key] = [ obj ]
    else:
        dict[key].append( obj )

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
        return -1
    return 1

def NORMAL_TO_AXES( normal ):
    ''' I am not sure if I will ever need this, but it seems good to keep track of '''
    dict = {
        'x':    ('y', 'z'),
        '-x':   ('y', 'z'),
        'y':    ('x', 'z'),
        '-y':   ('x', 'z'),
        'z':    ('x', 'y'),
        '-z':   ('x', 'y'),
    }
    return dict[normal]

def NORMAL_TO_TEXTURE( normal ):
    if normal == 'z':
        return 'orange_dev/dev_measurewall_green03'.upper()
    elif normal == '-z':
        return 'dev/reflectivity_70'.upper()
    else:
        return 'dev/dev_blendmeasure2'.upper()

def GET_FACE_DATA( solid ):
    xMin, xMax, yMin, yMax, zMin, zMax = getDimensionsOfSolid( solid )
    solid_fd_dict = {
    'x':    FaceData( 'x', xMin, ( yMin, yMax, zMin, zMax )),
    '-x':   FaceData( '-x', xMax, ( yMin, yMax, zMin, zMax )),
    'y':    FaceData( 'y', yMin, ( xMin, xMax, zMin, zMax )),
    '-y':   FaceData( '-y', yMax, ( xMin, xMax, zMin, zMax )),
    'z':    FaceData( 'z', zMin, ( xMin, xMax, yMin, yMax )),
    '-z':   FaceData( '-z', zMax, ( xMin, xMax, yMin, yMax )),
    }
    for normal in solid_fd_dict:
        fd = solid_fd_dict[normal]
        fd.initial_faces(solid_fd_dict)

    solid_data = [ solid_fd_dict[key] for key in solid_fd_dict ]
    return solid_data

testVMF = load_vmf('vmfs/bezier_test.vmf')
textures = Textures()
solids = [solid for solid in testVMF.get_solids() if solid.has_texture('tools/toolsskip'.upper())]
dummy_vmf = new_vmf()
face_data_list = []
for solid in solids:
    face_data_list.extend( GET_FACE_DATA( solid ) )

''' Get all the faces with the same position and the same or opposite normal '''
fd_x_dict = {}
fd_y_dict = {}
fd_z_dict = {}
for fd in face_data_list:
    if fd.normal in { 'x', '-x' }:
        DICT_LIST_HELPER( fd_x_dict, fd.pos, fd )
    elif fd.normal in { 'y', '-y' }:
        DICT_LIST_HELPER( fd_y_dict, fd.pos, fd )
    elif fd.normal in { 'z', '-z' }:
        DICT_LIST_HELPER( fd_z_dict, fd.pos, fd )



def get_new_faces( fd_direction_dict ):
    all_new_faces = []
    all_new_holes = []
    for pos in fd_direction_dict:
        x1_set, x2_set = set([]), set([])
        for fd in fd_direction_dict[pos]:
            x1_set = x1_set.union( {fd.x1_min, fd.x1_max} )
            x2_set = x2_set.union( {fd.x2_min, fd.x2_max} )
        x1_list = list(x1_set)
        x2_list = list(x2_set)
        x1_list.sort()
        x2_list.sort()
        pre_face_matrix = []
        for i in range(len(x1_list)-1):
            pre_face_matrix.append([])
            for j in range(len(x2_list)-1):
                new_pre_face = FaceData( '?', pos, [x1_list[i], x1_list[i+1], x2_list[j], x2_list[j+1]] )
                pre_face_matrix[i].append( new_pre_face )
                for fd in fd_direction_dict[pos]:
                    fd.has_intersection( new_pre_face )
        
        holes = []
        for i in range(len(x1_list)-1):
            for j in range(len(x2_list)-1):
                pre_face = pre_face_matrix[i][j]
                if len(pre_face.parents) == 2:
                    holes.append( pre_face )
                    if i < (len(x1_list) - 2):
                        pre_face_matrix[i+1][j].x1_min += 128
                    if i > 0:
                        pre_face_matrix[i-1][j].x1_max -= 128
                    if j < (len(x2_list) - 2):
                        pre_face_matrix[i][j+1].x2_min += 128
                    if j > 0:
                        pre_face_matrix[i][j-1].x2_max -= 128

        new_faces = []
        for i in range(len(x1_list)-1):
            for j in range(len(x2_list)-1):
                pre_face = pre_face_matrix[i][j]
                if len(pre_face.parents) == 1:
                    new_faces.append( pre_face )

        all_new_faces.extend( new_faces )
        all_new_holes.extend( holes )
    return all_new_faces, all_new_holes

def update_holes( holes ):
    for fd in holes:
        for parent in fd.parents:
            for key in parent.children:
                if fd in parent.children[ key ]:
                    for _fd in parent.next[ DIRECTION_HANDLER(key, 'o') ].children[ DIRECTION_HANDLER(parent.normal, 'o') ]:
                        _fd.additional_colored_directions.add( DIRECTION_HANDLER(parent.normal, 'o') )

x_faces, x_holes = get_new_faces( fd_x_dict )
print('done for x')
y_faces, y_holes = get_new_faces( fd_y_dict )
print('done for y')
z_faces, z_holes = get_new_faces( fd_z_dict )
print('done for z')

all_new_faces = x_faces + y_faces + z_faces

update_holes( x_holes )
print('x-holes done')
update_holes( y_holes )
print('y-holes done')
update_holes( z_holes )
print('z-holes done')

print( len(x_holes), len(y_holes), len(z_holes) )

for fd in all_new_faces:
    dummy_vmf = addVMF(dummy_vmf, fd.to_wall(textures))
dummy_vmf.export('vmfs/bezier_test_connected.vmf')
print('done')