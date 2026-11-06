
previous_mode = None

def control_system(temperature, occupied):

    global previous_mode
    if occupied == False:
        target_mode = "OFF"

    elif temperature < 18:
        target_mode = "HEATING"

    elif temperature > 26:
        target_mode = "COOLING"

    else:
        target_mode = "OFF"
    if target_mode != previous_mode:
        send_command = True
    else:
        send_command = False
    previous_mode = target_mode

    return target_mode, send_command
print("Test 1:", control_system(17, True))
print("Test 2:", control_system(17, True))
print("Test 3:", control_system(18, True))
print("Test 4:", control_system(26, True))
print("Test 5:", control_system(27, True))
print("Test 6:", control_system(22, False))