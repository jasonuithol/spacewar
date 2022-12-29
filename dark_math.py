import math

class Rect:
    def __init__(self, pos, dim):
        self.pos = pos
        self.dim = dim

    def left(self):
        return math.min(self.pos[0], self.pos[0] + self.dim[0])

    def right(self):
        return math.max(self.pos[0], self.pos[0] + self.dim[0])

    def top(self):
        return math.min(self.pos[1], self.pos[1] + self.dim[1])

    def bottom(self):
        return math.max(self.pos[1], self.pos[1] + self.dim[1])

    def clip(self, other):
        left = math.max(self.left(), other.left())
        right = math.min(self.right(), other.right())
        top = math.max(self.top(), other.top())
        bottom = math.min(self.bottom(), other.bottom())
        return Rect((left,top),(right - left, bottom - top))

    def intersects(self, other):
        # TODO: Could get tricky on boundary conditions.
        if isinstance(other, Rect):
            clipped = self.clip(other)
            return clipped.dim[0] >= 0 and clipped.dim[1] >= 0
        else:
            return self.intersects(Rect(other, (0,0)))

def add2(a, b):
    ax,ay = a
    bx,by = b
    return (ax + bx, ay + by)

def sub2(a, b):
    ax,ay = a
    bx,by = b
    return (ax - bx, ay - by)

def len2(a):
    ax,ay = a
    return math.sqrt(ax**2 + ay**2)

def distance2(a, b):
    return len2(sub2(a, b))

def mul2(a, b):
    ax,ay = a
    if isinstance(b, (int, float)):
        return (ax*b, ay*b)
    else:
        bx,by = b
        return (ax*bx, ay*by)

def div2(a, b):
    ax,ay = a
    if isinstance(b, (int, float)):
        return (ax/b, ay/b)
    else:
        bx,by = b
        return (ax/bx, ay/by)

def normal2(a):
    ax,ay = a
    vector_length = len2(a)
    return ax/vector_length, ay/vector_length

def normal_to_degrees2(a):
    x, y = a
    return (math.atan2(x, y) * 180 / math.pi) - 90

def degrees_to_normal2(a):
    return math.cos(math.radians(a + 90)), math.sin(math.radians(a + 90))

def confine2(position, size, boundary):
    x, y = position
    limx, limy = boundary
    sizex, sizey = size
    
    if x > limx - sizex:
        x = limx - sizex
    if x < 0:
        x = 0
    if y > limy - sizey:
        y = limy - sizey
    if y < 0:
        y = 0
    
    return x, y

def midpoint2(a, b):
    ax,ay = a
    bx,by = b
    return (ax + bx)/2, (ay + by)/2

def floor2(a):
    ax,ay = a
    return math.floor(ax), math.floor(ay)
