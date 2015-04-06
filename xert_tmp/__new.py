def b1_pressed(b1_counter):
    b1_counter += 1
    return {'b1_counter': b1_counter}
def b2_pressed(b2_counter):
    if (b2_counter < 3):
        b2_counter += 1
    return {'b2_counter': b2_counter}
