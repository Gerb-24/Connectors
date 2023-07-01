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
    def __init__(self, normal, pos,  dims ):
        self.normal = normal
        self.pos = int(pos)
        self.dims = dims
        self.x1_min, self.x1_max, self.x2_min, self.x2_max = self.dims

    def __str__(self) -> str:
        s = f'''FACE(
    normal = {self.normal}
    pos = {self.pos}
    dims = {self.dims}
)'''
        return s
    
    def has_intersection( self, pre_face ):
        x1_min, x1_max, x2_min, x2_max = pre_face
        if x1_min >= self.x1_max or x2_min >= self.x2_max or x1_max <= self.x1_min or x2_max <= self.x2_min:
            return 0
        else:
            return 1

    def has_zero_volume( self ):
        return (self.x1_min >= self.x1_max or self.x2_min >= self.x2_max)

    def to_wall( self, textures ):
        if self.has_zero_volume():
            proto = new_vmf()
            return proto

        materials_dictionary = {
                self.normal:                            NORMAL_TO_TEXTURE(self.normal),
            }
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
    solid_ed_dict = {
    'x':    FaceData( 'x', xMin, ( yMin, yMax, zMin, zMax ) ),
    '-x':   FaceData( '-x', xMax, ( yMin, yMax, zMin, zMax ) ),
    'y':    FaceData( 'y', yMin, ( xMin, xMax, zMin, zMax ) ),
    '-y':   FaceData( '-y', yMax, ( xMin, xMax, zMin, zMax ) ),
    'z':    FaceData( 'z', zMin, ( xMin, xMax, yMin, yMax ) ),
    '-z':   FaceData( '-z', zMax, ( xMin, xMax, yMin, yMax ) ),
    }
    solid_data = [ solid_ed_dict[key] for key in solid_ed_dict ]
    return solid_data

testVMF = load_vmf('vmfs/test3.vmf')
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
        intersection_matrix = []
        normal_matrix = []
        for i in range(len(x1_list)-1):
            pre_face_matrix.append([])
            intersection_matrix.append([])
            normal_matrix.append([])
            for j in range(len(x2_list)-1):
                normal_matrix[i].append('?')
                intersection_matrix[i].append(0)
                pre_face_matrix[i].append( [x1_list[i], x1_list[i+1], x2_list[j], x2_list[j+1]] )
                for fd in fd_direction_dict[pos]:
                    has_intersection =  fd.has_intersection(pre_face_matrix[i][j])
                    intersection_matrix[i][j] += has_intersection
                    if has_intersection in {1, -1}:
                        normal_matrix[i][j] = fd.normal
        

        for i in range(len(x1_list)-1):
            for j in range(len(x2_list)-1):
                if intersection_matrix[i][j] == 2:
                    pre_face_matrix[i+1][j][0] += 128
                    pre_face_matrix[i-1][j][1] -= 128
                    pre_face_matrix[i][j+1][2] += 128
                    pre_face_matrix[i][j-1][3] -= 128


        new_faces = []
        for i in range(len(x1_list)-1):
            for j in range(len(x2_list)-1):
                if intersection_matrix[i][j] == 1:
                    new_faces.append( FaceData(normal_matrix[i][j], pos, pre_face_matrix[i][j]) )

        all_new_faces.extend( new_faces )
    return all_new_faces

all_new_faces = []
all_new_faces.extend( get_new_faces( fd_x_dict ) )
print('done for x')
all_new_faces.extend( get_new_faces( fd_y_dict ) )
print('done for y')
all_new_faces.extend( get_new_faces( fd_z_dict ) )
print('done for z')

for fd in all_new_faces:
    dummy_vmf = addVMF(dummy_vmf, fd.to_wall(textures))
dummy_vmf.export('vmfs/test3_new_connected.vmf')

print('done')