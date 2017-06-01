
import random, math

NUM_DRONES = 30 # 10000
AIRSPACE_SIZE = 160  # Meters. 128000
CONFLICT_RADIUS = 20  # Meters. 500
MIN_WIDTH_QUAD_NODE = CONFLICT_RADIUS / 2
MIN_HEIGHT_QUAD_NODE = CONFLICT_RADIUS / 2
conflicting_box_size = math.sqrt(CONFLICT_RADIUS * CONFLICT_RADIUS/2)
max_depth_quad_tree = 0
size = AIRSPACE_SIZE
while size >= MIN_HEIGHT_QUAD_NODE:
    max_depth_quad_tree += 1
    size /= 2
max_depth_quad_tree -= 1

def is_conflicting_points(point1, point2):
    if abs(point1.x - point2.x) > CONFLICT_RADIUS:  return False
    elif abs(point1.y - point2.y) > CONFLICT_RADIUS:  return False
    elif abs(point1.x - point2.x) <= conflicting_box_size and abs(point1.y - point2.y) <= conflicting_box_size: return True
    else:
        x, y = (point1.x - point2.x, point1.y - point2.y)
        distance = math.sqrt(x*x + y*y)
        if distance <= CONFLICT_RADIUS: return True
        else: return False

def _loop_all_children(parent, depth=0):
    if parent.depth != max_depth_quad_tree - depth:
        for child in parent.nodes:
            # this if loop avoids  looping through children if total count at child is 0
            # Imagine only 2 points in huge QuadTree with depth of 9
            if child.total_children == 0: continue
            if child.nodes:
                for subchild in _loop_all_children(child):
                    yield subchild
            yield child
    else: yield parent

class Point(object):
    """
    Point prepresents the point location on a map.
    x, y are the point co-ordinates
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.conflicted_with = {}

    def __str__(self):
        return ' '.join([str(self.x) , str(self.y)])

    def get_conflicts_total(self):
        return len(self.conflicted_with)

    def add_conflicting_point(self, point):
        value = str(point.x) + ' ' + str(point.y)
        self.conflicted_with.update({value: True})

    def is_conflicting_point(self, point):
        value = str(point.x) +  ' ' +str(point.y)
        if value in self.conflicted_with: return True
        return False

class QuadTree(object):
    """
    QuadTree Data structure  is used to store the point location as a 'Point'
    Every QuadTree can have 4 sub QuadTree as nodes. The children keeps track of points
    in the tree. Every QuadTree keeps a track of left, right, bottom & top 'most' Point/Point
    """
    def __init__(self, width, height, center_x, center_y, depth=0, parent=None, root=None):
        self.nodes,  self.children = ([], [])
        self.width, self.height = float(width), float(height)
        # Total children in each of the sub quadtree nodes + its children
        self.total_children = 0
        self.depth = depth
        self.center = (center_x, center_y)
        # At depth = 0, this is the grid that has access to all the nodes(at depth = max_depth_quad_tree)
        self.nodes_grid = None
        # This was defined initally for a recurrsive approach to find neighbour
        self.parent = parent
        if self.depth == 0:  self.root = self
        else:  self.root = root
        # print self
        self._create_child_nodes()

    def __iter__(self):
        for child in _loop_all_children(self):
            yield child

    def __str__(self):
        return ' '.join([str(float(self.center[0])) , str(float(self.center[1])) , str(self.depth),
                        str(self.width), str(self.height)])

    def insert(self, x ,y):
        if (int(self.depth) == int(max_depth_quad_tree)):
            self._insert_children(x, y)
            # print self, ':' ,x, y
        else:
            if (x < self.center[0]):
                if (y < self.center[1]):
                    self.nodes[0].insert(x, y)
                    self.nodes[0].incremet_total_children()
                elif (y >= self.center[1]):
                    self.nodes[1].insert(x, y)
                    self.nodes[1].incremet_total_children()
            if (x >= self.center[0]):
                if (y < self.center[1]):
                    self.nodes[2].insert(x, y)
                    self.nodes[2].incremet_total_children()
                elif (y >= self.center[1]):
                    self.nodes[3].insert(x, y)
                    self.nodes[3].incremet_total_children()

    def _insert_children(self, x, y):
        point = Point(x, y)
        self.children.append(point)
        self.add_node_to_grid(self)

    def _create_child_nodes(self):
        # Add 4 nodes to QuadTree till depth <=max_depth
        child_node_width, child_node_height = (self.width / 2, self.height / 2)
        new_width, new_height = (self.width / 4,  self.height / 4)
        child_node_depth = self.depth + 1
        if(child_node_depth <= max_depth_quad_tree
            and child_node_width >= MIN_WIDTH_QUAD_NODE
            and child_node_height >= MIN_HEIGHT_QUAD_NODE ):
            x1, y1 = (self.center[0] - new_width, self.center[1] - new_height)
            x2, y2 = (self.center[0] + new_width, self.center[1] + new_height)
            self.nodes = [QuadTree(child_node_width, child_node_height,
                                   x1, y1, child_node_depth, self, self.root),
                          QuadTree(child_node_width, child_node_height,
                                   x1, y2, child_node_depth, self, self.root),
                          QuadTree(child_node_width, child_node_height,
                                   x2, y1, child_node_depth, self, self.root),
                          QuadTree(child_node_width, child_node_height,
                                   x2, y2, child_node_depth, self, self.root)
                         ]
            if self.depth == 0:
                # initalize the matrix/ grid to None
                # When we insert Point to QuadTree then the grid is updated with the pointer to current QuadTree at MAX depth
                self.nodes_grid = []
                num_columns = AIRSPACE_SIZE / MIN_HEIGHT_QUAD_NODE
                for i in xrange(0, num_columns):
                    current_row = [None] * num_columns
                    self.nodes_grid.append(current_row)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def get_conflicts(self):
        return len(self.children)

    def add_node_to_grid(self, quad_node):
        (row, column) = quad_node.center
        row =  int(row / MIN_WIDTH_QUAD_NODE)
        column = int(column / MIN_WIDTH_QUAD_NODE )
        if not self.root.nodes_grid[row][column]:
            self.root.nodes_grid[row][column] = quad_node

    def incremet_total_children(self):
         self.total_children += 1

    def get_children(self):
        return self.children

    def find_conflcits_in_grid(self, query_point):
        (row, column) = self.center
        row =  int(row / MIN_WIDTH_QUAD_NODE)
        column = int(column / MIN_WIDTH_QUAD_NODE)
        num_columns = AIRSPACE_SIZE/ MIN_HEIGHT_QUAD_NODE
        # Search sorrounding row/column in matrix for depth -2 to 2 Basically +/-500m
        # Since each QuadTree height is 250m
        for i in [-1,0,1,-2, 2]:
            for j in [-1,0,1,-2, 2]:
                if i == 0 and j == 0: continue
                if row + i < 0 or column + j < 0 or row + i > num_columns -1 \
                or column + j > num_columns -1 : continue
                current_row, currnet_column = row + i, column + j
                current_quad = self.root.nodes_grid[current_row][currnet_column]
                if current_quad:
                    current_quad_children = current_quad.get_children()
                    for point in current_quad_children:
                        if is_conflicting_points(point, query_point):
                            query_point.add_conflicting_point(point)
                            if len(current_quad_children) == 1 and not point.get_conflicts_total():
                                # both point and query_point are only children in each quad tree
                                # So increment by 2 and mark point as conflicting
                                point.add_conflicting_point(query_point)
                                return 2
                            else:
                                return 1
        return 0

    def find_conflicts(self):
        current_conflicts, total_conflicts = (0, 0)
        for each_node in self:
            current_conflicts = each_node.get_conflicts()
            if current_conflicts == 1:
                query_point = each_node.get_children()[0]
                current_conflicts = 0 if query_point.get_conflicts_total() \
                else each_node.find_conflcits_in_grid(query_point)
            total_conflicts += current_conflicts
        return total_conflicts

def gen_coord():
    return int(random.random() * AIRSPACE_SIZE)

random.seed(1)  # Setting random number generator seed for repeatability
import time
def timetaken(func):
    def wrapper(*args):
        start_time = time.time()
        print "Starting Execution of '{0}' ".format(func.__name__)
        result = func(*args)
        elapsed_time = time.time() - start_time
        print "Execution of '{0}{1}' took {2} seconds".format(func.__name__, args, elapsed_time)
        return result
    return wrapper

@timetaken
def find_conflicts_in_points():
    print "AIRSPACE_SIZE: '{0}', NUM_DRONES: '{1}', CONFLICT_RADIUS: '{2}'".format(AIRSPACE_SIZE, NUM_DRONES, CONFLICT_RADIUS)
    if AIRSPACE_SIZE == 128000:
        print 'For AIRSPACE_SIZE = 128000 coderpad dosent create quad_tree. ' \
            'Works on my local machine in ~5 sec'
    quad_tree = QuadTree(AIRSPACE_SIZE, AIRSPACE_SIZE, AIRSPACE_SIZE/2,
                AIRSPACE_SIZE/2, 0)
    print "inserting coords"
    ## Edge case when two Points in 1 quad tree
    # quad_tree.insert(1, 1)
    # quad_tree.insert(2, 2)
    ## Case when there there are 4 Points near center
    # quad_tree.insert(79, 79)
    # quad_tree.insert(81, 81)
    # quad_tree.insert(81, 79)
    # quad_tree.insert(79, 81)
    # Add another Point at a higher level Count should be 3
    # quad_tree.insert(1, 1)
    # quad_tree.insert(2, 2)
    # quad_tree.insert(11, 11)
    for i in xrange(NUM_DRONES):
        x, y = gen_coord(), gen_coord()
        try:
            quad_tree.insert(x, y)
        except Exception, err:
            print "Exception:", x, y
            print Exception, err
    print "Finding Conflicts for NUM_DRONES: {} ".format(NUM_DRONES)
    conflicts = quad_tree.find_conflicts()
    print "Points in conflict: {}".format(conflicts)

# conflicts = count_conflicts(positions, CONFLICT_RADIUS)
# print "Points in conflict: {}".format(conflicts)

find_conflicts_in_points()

NUM_DRONES = 10000
AIRSPACE_SIZE = 128000  # Meters
CONFLICT_RADIUS = 500  # Meters
MIN_WIDTH_QUAD_NODE = CONFLICT_RADIUS / 2
MIN_HEIGHT_QUAD_NODE = CONFLICT_RADIUS / 2
conflicting_box_size = math.sqrt(CONFLICT_RADIUS * CONFLICT_RADIUS/2)
max_depth_quad_tree = 0
size = AIRSPACE_SIZE
while size >= MIN_HEIGHT_QUAD_NODE:
    max_depth_quad_tree += 1
    size /= 2
max_depth_quad_tree -= 1
print '\n'
find_conflicts_in_points()


# Given a square airspace, 128km x 128km, and N=10,000 points occupying the airspace
# our challenge is to efficiently compute how many points are flying too close to one
# another.

# Point positions will be provided as an Nx2 array of [x,y] coordinates (in meters).
# Points must maintain a horizontal separation of radius 0.5km from other points.

# If a point is within 0.5km of another point, both are "in conflict".
# Have count_conflicts return the total number of points that are in a conflicted state.
# Not the total number of conflicts).

# Do all of your work and testing in this pad.
# Some common libraries can be imported, but not all, so relying on niche algorithm won't work.
# This is very solvable with standard python libraries, several ways.

# Coding style, readability, scalability, and documentation all matter! Consider the
# computational complexity of your solution.

# The N^2 answer can be coded up in 5 minutes and # 10 lines; we'd like to see something better!
