from src.PyVMF import *

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

sideTextures = [f"dev/reflectivity_{10*(i+1)}" for i in range(6)]
sideDict = {
    sideTextures[0]:   "x",
    sideTextures[1]:   "y",
    sideTextures[2]:   "z",
    sideTextures[3]:  "-x",
    sideTextures[4]:  "-y",
    sideTextures[5]:  "-z",
}

def createDuplicateVMF(vmf: VMF):
    duplicateVMF = new_vmf()
    solids = vmf.get_solids()
    copiedSolids = [solid.copy() for solid in solids]
    duplicateVMF.add_solids(*vmf.get_solids())
    return duplicateVMF

def getDimensionsOfSide( side: Side ):
    allVertices = side.get_vertices()
    xMin = min([ vertex.x for vertex in allVertices ])
    yMin = min([ vertex.y for vertex in allVertices ])
    zMin = min([ vertex.z for vertex in allVertices ])
    xMax = max([ vertex.x for vertex in allVertices ])
    yMax = max([ vertex.y for vertex in allVertices ])
    zMax = max([ vertex.z for vertex in allVertices ])
    return xMin, xMax, yMin, yMax, zMin, zMax

prototypeVMF = load_vmf('vmfs/prototype.vmf')
testVMF = load_vmf('vmfs/test.vmf')
solid = testVMF.get_solids()[0]



topVertexManipulationBox = VertexManipulationBox( -512, 512, -512, 512, 0, 512)
bottomVertexManipulationBox = VertexManipulationBox( -512, 512, -512, 512, -512, 0)
backVertexManipulationBox = VertexManipulationBox( -512, 512, 0, 512, -512, 512)
frontVertexManipulationBox = VertexManipulationBox( -512, 512, -512, 0, -512, 512 )
startVertexManipulationBox = VertexManipulationBox( 0, 512, -512, 512, -512, 512)
endVertexManipulationBox = VertexManipulationBox( -512, 0, -512, 512, -512, 512)

def solidToBox( solid: Solid):
    dummyVMF = new_vmf()
    for side in solid.get_sides():
        prototypeDuplicate = createDuplicateVMF(prototypeVMF)
        topVertices = topVertexManipulationBox.getVerticesInBox(prototypeDuplicate)
        bottomVertices = bottomVertexManipulationBox.getVerticesInBox(prototypeDuplicate)
        backVertices = backVertexManipulationBox.getVerticesInBox(prototypeDuplicate)
        frontVertices = frontVertexManipulationBox.getVerticesInBox(prototypeDuplicate)
        startVertices = startVertexManipulationBox.getVerticesInBox(prototypeDuplicate)
        endVertices = endVertexManipulationBox.getVerticesInBox(prototypeDuplicate)

        # set to zero, note that the size of the prototype is 2*384^3
        for vertex in topVertices:
            vertex.move(0, 0, -384)
        for vertex in backVertices:
            vertex.move(0, -384, 0)
        for vertex in startVertices:
            vertex.move(-384, 0, 0)
        for vertex in bottomVertices:
            vertex.move(0, 0, 384)
        for vertex in frontVertices:
            vertex.move(0, 384, 0)
        for vertex in endVertices:
            vertex.move(384, 0, 0)

        xMin, xMax, yMin, yMax, zMin, zMax = getDimensionsOfSide(side)
        if side.material == sideTextures[2].upper():
            print('yeppo')
            for vertex in topVertices:
                vertex.move(0, 0, zMax)
            for vertex in backVertices:
                vertex.move(0, yMax, 0)
            for vertex in startVertices:
                vertex.move(xMax, 0, 0)
            for vertex in bottomVertices:
                vertex.move(0, 0, zMax-128)
            for vertex in frontVertices:
                vertex.move(0, yMin, 0)
            for vertex in endVertices:
                vertex.move(xMin, 0, 0)

            dummyVMF = addVMF( prototypeDuplicate, dummyVMF )

        if side.material == sideTextures[5].upper():
            # print('yes')
            # for vertex in topVertices:
            #     vertex.move(0, 0, 128)
            # for vertex in backVertices:
            #     vertex.move(0, yMax, 0)
            # for vertex in startVertices:
            #     vertex.move(xMax, 0, 0)
            # for vertex in bottomVertices:
            #     vertex.move(0, 0, 0)
            # for vertex in frontVertices:
            #     vertex.move(0, yMin, 0)
            # for vertex in endVertices:
            #     vertex.move(xMin, 0, 0)

            dummyVMF = addVMF( prototypeDuplicate, dummyVMF )

    return dummyVMF

boxVMF = solidToBox( solid )
boxVMF.export('vmfs/box.vmf')
