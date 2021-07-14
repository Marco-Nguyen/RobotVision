import math


def theta(dx, W, t_x):
    """calculate the theta angle between object and the center of robot

    """
    return math.atan(t_x * math.tan((2 * dx / W) * math.tan(34.5*math.pi/180)))*180/math.pi
