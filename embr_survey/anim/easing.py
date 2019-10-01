from math import sin, pi, pow
# from https://github.com/mosra/magnum/blob/master/src/Magnum/Animation/Easing.h

pihalf = pi/2.0


def linear(x):
    return x


def step(x):
    return 0.0 if x < 0.5 else 1.0


def smoothstep(x):
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    return (3.0 - 2.0 * x) * pow(x, 2)


def smootherstep(x):
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    return pow(x, 3) * (x * (x * 6.0 - 15.0) + 10.0)


def quadratic_in(x):
    return pow(x, 2)


def quadratic_out(x):
    return -x * (x - 2.0)


def quadratic_in_out(x):
    if x < 0.5:
        return 2.0*pow(x, 2)
    return 1.0 - 2.0*pow(1.0 - x, 2)


def exponential_in(x):
    return 0.0 if x <= 0.0 else pow(2.0, 10.0 * (x - 1.0))


def exponential_out(x):
    return 1.0 if x >= 1.0 else 1.0 - pow(2.0, -10.0 * x)


def exponential_in_out(x):
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    if x < 0.5:
        return 0.5 * pow(2.0, 20.0*x - 10.0)
    return 1.0 - 0.5 * pow(2.0, 10.0 - 20.0 * x)


def elastic_in(x):
    return pow(2.0, 10.0 * (x - 1.0)) * sin(13.0 * pihalf * x)


def elastic_out(x):
    return 1.0 - pow(2.0, -10.0 * x) * sin(13.0 * pihalf * (x + 1.0))


def elastic_in_out(x):
    if x < 0.5:
        return 0.5 * pow(2.0, 10.0 * (2.0 * x - 1.0)) * sin(13.0 * pi * x)
    return 1.0 - 0.5 * pow(2.0, 10.0 * (1.0 - 2.0 * x)) * sin(13.0 * pi * x)


def back_in(x):
    return x * (x * x - sin(pi * x))


def back_out(x):
    inv = 1.0 - x
    return 1 - inv*(inv*inv - sin(pi*inv))


def back_in_out(x):
    if x < 0.5:
        x2 = 2.0 * x
        return 0.5 * x2 * (x2 * x2 - sin(pi * x2))
    inv = 2.0 - 2.0 * x
    return 1.0 - 0.5 * inv * (inv * inv - sin(pi * inv))


def bounce_out(x):
    if x == 0:
        return 0
    if x < 4.0/11.0:
        return 121.0*x*x/16.0
    if x < 8.0/11.0:
        return 363.0/40.0*x*x - 99.0/10.0 * x + 17.0/5.0
    if x < 9.0/10.0:
        return 4356.0/361.0*x*x - 35442.0/1805.0*x + 16061.0/1805.0
    if x == 1:
        return 1
    return 54.0/5.0 * x*x - 513.0/25.0*x + 268.0/25.0


def bounce_in(x):
    return 1.0 - bounce_out(1.0 - x)


def bounce_in_out(x):
    if x < 0.5:
        return 0.5 * bounce_in(2*x)
    return 0.5 * bounce_out(2.0 * x - 1) + 0.5
