
def lerp(v0, v1, t):
    return (1.0 - t) * v0 + t * v1


def select(v0, v1, t):
    return v0 if t < 1.0 else v1
