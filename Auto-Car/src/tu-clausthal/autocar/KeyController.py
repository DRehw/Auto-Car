from KeyHandler import register_observer_func, unregister_observer_func, is_pressed
from time import time
speed = 0
steer = 0
max_speed = 15
max_steer = 30
speed_acc = 100
steer_acc = 10
round_perc = 0.8
cur_ms = int(round(time()*1000))
last_key_press_ms_dict = {"Up": cur_ms, "Down": cur_ms, "Left": cur_ms, "Right": cur_ms, "space": cur_ms}


def start():
    register_observer_func(["Up", "Down", "Left", "Right", "space"], on_key_event)
    return


def stop():
    unregister_observer_func(on_key_event)
    return


def get_cur_speed_and_steer():
    global speed, steer
    _update(None)
    return speed, steer


def on_key_event(key_str, if_pressed):
    _update(key_str)
    # print("Speed: {}, Steer: {}".format(speed, steer))
    return


def _update(pressed_key_str):
    print("Update")
    global last_key_press_ms_dict, speed_acc, steer_acc, speed, steer, max_speed, max_steer
    d_speed = 0
    d_steer = 0
    is_pressed_dict = {"Up": is_pressed("Up"), "Down": is_pressed("Down"), "Left": is_pressed("Left"),
                       "Right": is_pressed("Right"), "space": is_pressed("space")}
    cur_ms = int(round(time()*1000))
    if pressed_key_str is not None:  # Invert the status of key of the event in order to use it properly,
        # because it it will be already inversed when this is called
        # e.g.: when key "Right" is pressed, is_pressed returns already true, but when the event happens, you need to
        # only consider the change in the past where it was false
        is_pressed_dict[pressed_key_str] = not is_pressed_dict[pressed_key_str]
        last_key_press_ms_dict[pressed_key_str] = cur_ms
        if pressed_key_str == "space":
            print("Breaking!")

    # Calculate the change depending on the current status of each key
    if is_pressed_dict["space"]:
        d_speed = -speed
    else:
        if is_pressed_dict["Up"]:
            max_change = _get_change(cur_ms - last_key_press_ms_dict["Up"], speed_acc)
            if max_change > 0:
                d_speed += max_change
                last_key_press_ms_dict["Up"] += max_change * speed_acc
        if is_pressed_dict["Down"]:
            max_change = _get_change(cur_ms - last_key_press_ms_dict["Down"], speed_acc)
            if max_change > 0:
                d_speed -= max_change
                last_key_press_ms_dict["Down"] += max_change * speed_acc

    if is_pressed_dict["Left"]:
        max_change = _get_change(cur_ms - last_key_press_ms_dict["Left"], steer_acc)
        if max_change > 0:
            d_steer += max_change
            last_key_press_ms_dict["Left"] += max_change * steer_acc
    if is_pressed_dict["Right"]:
        max_change = _get_change(cur_ms - last_key_press_ms_dict["Right"], speed_acc)
        if max_change > 0:
            d_steer -= max_change
            last_key_press_ms_dict["Right"] += max_change * steer_acc
    # Mechanism for steer to converge to 0 when both left and right are not pressed
    if not is_pressed_dict["Right"] and not is_pressed_dict["Left"] and steer != 0:
        last_press_ms = max(last_key_press_ms_dict["Right"], last_key_press_ms_dict["Left"])
        max_change = _get_change(cur_ms - last_press_ms, speed_acc)
        if max_change > 0:
            last_key_press_ms_dict["Right"] += max_change * steer_acc
            last_key_press_ms_dict["Left"] += max_change * steer_acc
            if abs(max_change) > abs(steer):
                d_steer = steer * -1
            else:
                if steer > 0:
                    d_steer -= max_change
                else:
                    d_steer += max_change
    # apply the changes to speed and steer
    if d_speed != 0:
        if abs(speed + d_speed) > max_speed:
            if speed + d_speed > 0:
                speed = max_speed
            else:
                speed = -max_speed
        else:
            speed += d_speed
        # print("Speed: {}".format(speed))
    if d_steer != 0:
        if abs(steer + d_steer) > max_steer:
            if steer + d_steer > 0:
                steer = max_steer
            else:
                steer = -max_steer
        else:
            steer += d_steer
        # print("Steer: {}".format(steer))


def _round(value):
    if value % 1 >= round_perc:
        return int(value) + 1
    else:
        return int(value)


def _get_change(time_dif, time_per_step):
    return _round(time_dif / time_per_step)
