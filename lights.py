from src.PyVMF import *
from main import *

testVMF = load_vmf('vmfs/bezier_test.vmf')
solids = [solid for solid in testVMF.get_solids() if solid.has_texture('tools/toolsskip'.upper())]
interval = 2*128
dummy_vmf = new_vmf()
for solid in solids:
    xMin, xMax, yMin, yMax, zMin, zMax = getDimensionsOfSolid( solid )
    boundary = 2*128
    x_quot, x_res = divmod(xMax-xMin-2*boundary, interval)
    y_quot, y_res = divmod(yMax-yMin-2*boundary, interval)
    z_quot, z_res = divmod(zMax-zMin-2*boundary, interval)
    for i in range( int(x_quot) + 1 ):
        for j in range( int(y_quot) + 1 ):
            for k in range( int(z_quot) + 1 ):
                    x_val = xMin + i*interval + x_res/2 + boundary
                    y_val = yMin + j*interval + y_res/2 + boundary
                    z_val = zMin + k*interval + z_res/2 + boundary
                    dic = {
                            'classname':    'light',
                            'origin':       f'{x_val} {y_val} {z_val}',
                            '_light':       '255 255 255 400'
                        }
                    light = Entity(dic=dic)
                    dummy_vmf.add_entities( light )
dummy_vmf.export('vmfs/bezier_light_test.vmf')
    
    
    
