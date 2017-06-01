
# Find Conflicts in Points
    for a given AIRSPACE_SIZE , CONFLICT_RADIUS and NUM_DRONES this script finds
    the total number of conflicting points when the distance between two points is <= CONFLICT_RADIUS

## Problem
    Given a square airspace, 128km x 128km, and N=10,000 points occupying the airspace
    our challenge is to efficiently compute how many points are flying too close to one
    another.
    Point positions will be provided as an Nx2 array of [x,y] coordinates (in meters).
    Points must maintain a horizontal separation of radius 0.5km from other points.
    If a point is within 0.5km of another point, both are "in conflict".
    Have count_conflicts return the total n

## Data Structure Used
    I used QuadTree Data Structure. The idea is for a conflict radius of M, divide the AIRSAPCE
    into smaller quadTree till height and width >= conflict_radius/2. This way we can guarantee
    that if there are more than 1 points in a quad then they are in conflict.
    As for the case where is 1 point we need to find its nearest neighbor and check its distance.
    For a quadtree I am also keeping grid which has access to all the quadTree at max depth.
    Buy using this I dont have to use the recuriise solution to find nearest neighbour

## Find Points Process
    For MIN_WIDTH_QUAD_NODE=250 if there are 2 or more points in a QuadTree then its conflicting.
    If there is only 1 point then Algo uses root.grid to access sorrounding grids.
    Only nodes with row (& column) +/- 2 are searched from current positions. This cause when a point is
    at the edge of a quadtree then it can conflict with nodes that are +/-2 x/y as height of each QuadTree is 250
    for conflict radius of 500

## Platforms
    Python 2.

## Dependencies
    It used python math library

## License:
This code is free to share, use, reuse, and modify according to the MIT license

## Credits:
- Chintamani Lonkar

