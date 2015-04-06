b1_counter = 0
b2_counter = 0

def b1_pressed():
    global b1_counter
    b1_counter += 1

def b2_pressed():
    global b2_counter
    if b2_counter < 3: # ADDED LINE
        b2_counter += 1

def xert_asserts(old, new):
    assert(old.b1_counter == new.b1_counter)
    assert(old.b2_counter == new.b2_counter)
