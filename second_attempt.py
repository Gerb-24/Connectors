from src.PyVMF import *
from main import *
from sidewalls import prototypeVMF, BrushVertexManipulationBox, Textures


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
            ans = 1 if self.normal in {'x', 'y', 'z'} else -1
            return ans

    def to_wall( self, textures ):
        proto = createDuplicateVMF(prototypeVMF)
        verts = BrushVertexManipulationBox( proto ).createVerticesInBoxDict().moveToZero()

        if self.normal == 'x':
            verts.full_move( self.pos, self.x1_max, self.x2_max, self.pos - 128, self.x1_min, self.x2_min  )

        elif self.normal == 'y':
            verts.full_move( self.x1_max, self.pos, self.x2_max, self.x1_min, self.pos - 128, self.x2_min  )

        elif self.normal == '-x':
            verts.full_move( self.pos + 128, self.x1_max, self.x2_max, self.pos, self.x1_min, self.x2_min  )

        elif self.normal == '-y':
            verts.full_move( self.x1_max, self.pos + 128, self.x2_max, self.x1_min, self.pos, self.x2_min  )

        elif self.normal == 'z':
            verts.full_move( self.x1_max, self.x2_max, self.pos, self.x1_min, self.x2_min, self.pos - 128  )

        elif self.normal == '-z':
            verts.full_move( self.x1_max, self.x2_max, self.pos + 128, self.x1_min, self.x2_min, self.pos  )

        solid = proto.get_solids()[0]
        for side in solid.get_sides():
            if side.material in textures.to_sides( self.normal ):
                if self.normal == 'z':
                    side.material = 'orange_dev/dev_measurewall_green03'.upper()
                elif self.normal == '-z':
                    side.material = 'dev/reflectivity_70'.upper()
                else:
                    side.material = 'dev/dev_blendmeasure2'.upper()
            else:
                side.material = textures.nodraw
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
                }
    return direction_dict[direction][s]


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



def get_new_faces( fd_direction_dict, pos_neg_dir ):
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
        pre_face_list = []
        for i in range( len(x1_list) - 1):
            for j in range( len(x2_list) - 1 ):
                pre_face_list.append( (x1_list[i], x1_list[i+1], x2_list[j], x2_list[j+1]) )
        intersection_numbers = [0]*len(pre_face_list)
                
        for i in range( len(pre_face_list) ):
            for fd in fd_direction_dict[pos]:
                intersection_numbers[i] += fd.has_intersection(pre_face_list[i])
        new_faces = []
        for i in range( len(pre_face_list) ):
            if intersection_numbers[i]!= 0:
                normal = pos_neg_dir[0] if intersection_numbers[i] == 1 else pos_neg_dir[1]
                new_faces.append( FaceData(normal, pos, pre_face_list[i]) )

        all_new_faces.extend( new_faces )
    return all_new_faces

all_new_faces = []
all_new_faces.extend( get_new_faces( fd_x_dict, ['x', '-x'] ) )
all_new_faces.extend( get_new_faces( fd_y_dict, ['y', '-y'] ) )
all_new_faces.extend( get_new_faces( fd_z_dict, ['z', '-z'] ) )

for fd in all_new_faces:
    dummy_vmf = addVMF(dummy_vmf, fd.to_wall(textures))
dummy_vmf.export('vmfs/test3_new_connected.vmf')