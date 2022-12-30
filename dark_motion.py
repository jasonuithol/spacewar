def invert(func, x):
    return 1 - func(x)

def reverse(func, x):
    return func(1 - x)

def linear(x):
    return x

# source: https://easings.net
def ease_out_bounce(x):
    n1 = 7.5625
    d1 = 2.75

    if x < 1 / d1:
        return n1 * x * x
    elif x < 2 / d1:
        return n1 * (x - 1.5 / d1) * (x - 1.5) + 0.75
    elif x < 2.5 / d1:
        return n1 * (x - 2.25 / d1) * (x - 2.25) + 0.9375
    else:
        return n1 * (x - 2.625 / d1) * (x - 2.625) + 0.984375

def ease_in_out_bounce(x):
    if x < 0.5:
        return (1 - ease_out_bounce(1 - 2 * x)) / 2
    else:
        return (1 + ease_out_bounce(2 * x - 1)) / 2
