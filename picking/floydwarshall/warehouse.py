import collections
import numpy #type: ignore





# Define the node type as a namedtuple
Node = collections.namedtuple ("Node", "x y")







def _euclidean (n, m):
    """
    This method returns the euclidean distance between 2 nodes.

    :param n: First node.
    :param m: Second node.
    :return: The distance.

    """
    return int(((n.x - m.x)**2 + (n.y - m.y)**2)**0.5)






class Warehouse (object):
    """
    An instance of this class represents a warehouse.
    It is formalised as a set of archs and node.

    Note that a method would be enough for this generation, but a class
    is preferrable to keep track of all its elements.

    """
 
    def __init__(self,
                blocks,
                racks_per_block,
                locations_per_side,
                locations_size,
                aisles_size,
                crossaisles_size):
        """
        Initialize.

        :param blocks: <int> The number of blocks divided by a cross aisle.
        :param racks_per_block: <int> The number of racks in each block.
        :param locations_per_side: <int> The number of storage locations facing on each aisle in each rack.
        :param locations_size: <tuple[int,int]> The x and y size of the locations.
        :param aisles_size: <int> The width of the aisles.
        :param crossaisles_size: <int> The width of the cross asisles.

        """
        self.blocks = blocks
        self.racks_per_block = racks_per_block
        self.locations_per_side = locations_per_side
        self.locations_size = locations_size
        self.aisles_size = aisles_size
        self.crossaisles_size = crossaisles_size


        self.aisles = racks_per_block + 1
        self.crossaisles = self.blocks - 1

        y_coordinates = numpy.zeros(self.blocks * self.locations_per_side + self.crossaisles + 2, dtype=int)
        index : int = 1
        for block in range (self.blocks):
            for loc in range (self.locations_per_side):
                if loc == 0 and block > 0:
                    y_coordinates[index] = y_coordinates[index - 1] + crossaisles_size/2 + locations_size[1]/2
                else:
                    y_coordinates[index] = y_coordinates[index - 1] + locations_size[1]
                index += 1

            if block < self.blocks - 1:
                y_coordinates[index] = y_coordinates[index - 1] + crossaisles_size/2 + locations_size[1]/2
                index += 1
            else:
                y_coordinates[index] = y_coordinates[index - 1] + locations_size[1]
                index += 1


        x_coordinates = numpy.zeros(self.aisles, dtype=int)
        index = 0
        for i in range (self.aisles):
            x_coordinates[index] = i * (aisles_size + locations_size[0] * 2)
            index += 1

        self.nodes = { i : {j : Node (x, y) for j, y in enumerate(y_coordinates)} for i, x in enumerate(x_coordinates)}

        self.graph = {}
        
        node_id : int = 0
        for x, dic in self.nodes.items():
            for y, node in dic.items():
                if y < numpy.size(y_coordinates) - 1:

                    oth = node_id + 1
                    dist = _euclidean (node, self.nodes[x][y + 1])

                    if self.graph.get(node_id):
                        self.graph[node_id][oth] = dist
                    else:
                        self.graph[node_id] = {oth : dist}

                    if self.graph.get(oth):
                        self.graph[oth][node_id] = dist
                    else:
                        self.graph[oth] = {node_id : dist}



                if y % (self.locations_per_side + 1) == 0 and x < len(self.nodes) - 1:

                    oth = node_id + numpy.size(y_coordinates)
                    dist = _euclidean (node, self.nodes[x + 1][y])
                    if self.graph.get(node_id):
                        self.graph[node_id][oth] = dist
                    else:
                        self.graph[node_id] = {oth : dist}

                    if self.graph.get(oth):
                        self.graph[oth][node_id] = dist
                    else:
                        self.graph[oth] = {node_id : dist}

                node_id += 1
