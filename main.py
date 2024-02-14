from src.PyVMF import *

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

class VertexManipulationBox:
    def __init__( self, xMin, xMax, yMin, yMax, zMin, zMax ):
        self.xMin, self.xMax, self.yMin, self.yMax, self.zMin, self.zMax = xMin, xMax, yMin, yMax, zMin, zMax

    def getVerticesInBox( self, vmf ):
        allVertices = []
        for solid in vmf.get_solids():
            allVertices.extend(solid.get_all_vertices())
        verticesInBox = []
        for vertex in allVertices:
            if self.xMin < vertex.x < self.xMax and self.yMin < vertex.y < self.yMax and self.zMin < vertex.z < self.zMax:
                verticesInBox.append( vertex )
        return verticesInBox
    
    def getVerticesOfSolid( self, solid: Solid ):
        verticesInSolid = []
        for vertex in solid.get_all_vertices():
            if self.xMin <= vertex.x <= self.xMax and self.yMin <= vertex.y <= self.yMax and self.zMin <= vertex.z <= self.zMax:
                verticesInSolid.append( vertex )
        return verticesInSolid

# functions that handle vmfs

def addVMF( vmf: VMF, vmf_to_add: VMF ):
    total_vmf = createDuplicateVMF( vmf )

    #add solids
    solids = vmf_to_add.get_solids( include_solid_entities=False )
    copiedSolids = [ solid.copy() for solid in solids ]
    total_vmf.add_solids(*copiedSolids)

    # add entities
    entities = vmf_to_add.get_entities( include_solid_entities=True )
    copiedEntities = [ entity.copy() for entity in entities ]
    total_vmf.add_entities(*copiedEntities)

    return total_vmf

def createDuplicateVMF(vmf: VMF):
    duplicateVMF = new_vmf()
    solids = vmf.get_solids( include_solid_entities=False )
    copiedSolids = [solid.copy() for solid in solids]
    duplicateVMF.add_solids(*copiedSolids)

    entities = vmf.get_entities( include_solid_entities=True )
    copiedEntities = [ entity.copy() for entity in entities ]
    duplicateVMF.add_entities(*copiedEntities)
    return duplicateVMF

def removeSolids(vmf: VMF, solidsToRemove):
    vmf.world.solids = [ solid for solid in vmf.world.solids if solid not in solidsToRemove ]
    return vmf

def moveVMF( vmf: VMF, coord ):
    solids = vmf.get_solids( include_solid_entities=True )
    for solid in solids:
        solid.move( *coord )
    entities = vmf.get_entities( include_solid_entities=True )
    for entity in entities:
        if "origin" in entity.other:
            origin = entity.other["origin"]
            entity.other["origin"] = Vertex( origin.x + coord[0], origin.y + coord[1], origin.z + coord[2] )

# functions that handle solids

def getDimensionsOfSolid( solid: Solid ):
    allVertices = solid.get_all_vertices()
    xMin = min([ vertex.x for vertex in allVertices ])
    yMin = min([ vertex.y for vertex in allVertices ])
    zMin = min([ vertex.z for vertex in allVertices ])
    xMax = max([ vertex.x for vertex in allVertices ])
    yMax = max([ vertex.y for vertex in allVertices ])
    zMax = max([ vertex.z for vertex in allVertices ])
    return xMin, xMax, yMin, yMax, zMin, zMax

def getMaxDimensionsOfList( solids ):
    xMin_l, xMax_l, yMin_l, yMax_l, zMin_l, zMax_l = set(), set(), set(), set(), set(), set()
    for solid in solids:
        xMin, xMax, yMin, yMax, zMin, zMax = getDimensionsOfSolid( solid )
        xMin_l.add(xMin)
        xMax_l.add(xMax)
        yMin_l.add(yMin)
        yMax_l.add(yMax)
        zMin_l.add(zMin)
        zMax_l.add(zMax)
    xMin, xMax, yMin, yMax, zMin, zMax = min( xMin_l ), max( xMax_l ), min( yMin_l ), max( yMax_l ), min( zMin_l ), max( zMax_l )
    return ( xMin, xMax, yMin, yMax, zMin, zMax )

# functions that handle sids

def getDimensionsOfSide( side: Side ):
    allVertices = side.get_vertices()
    xMin = min([ vertex.x for vertex in allVertices ])
    yMin = min([ vertex.y for vertex in allVertices ])
    zMin = min([ vertex.z for vertex in allVertices ])
    xMax = max([ vertex.x for vertex in allVertices ])
    yMax = max([ vertex.y for vertex in allVertices ])
    zMax = max([ vertex.z for vertex in allVertices ])
    return xMin, xMax, yMin, yMax, zMin, zMax



