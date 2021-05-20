import math


def theta(dx, W, t_x):
    """calculate the theta angle between object and the center of robot

    """
    return math.pi/2 - math.atan((math.tan(math.pi/2 - (t_x * 2 * dx / W))*math.tan(21*math.pi/180)))*180/math.pi
