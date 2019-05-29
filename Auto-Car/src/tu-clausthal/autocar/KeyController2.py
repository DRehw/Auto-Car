from KeyHandler import register_observer_func, unregister_observer_func, is_pressed
from time import time
speed = 0
speed_change = 0
steer = 0
steer_change = 0
max_speed = 15
max_steer = 30
speed_acc = 150
steer_acc = 50
cur_ms = int(round(time()*1000))
last_key_press_ms_dict = {"Up": cur_ms, "Down": cur_ms, "Left": cur_ms, "Right": cur_ms, "space": cur_ms}


def start():
    register_observer_func(["Up", "Down", "Left", "Right", "space"], on_key_event)
    return


def stop():
    unregister_observer_func(on_key_event)
    return


def update():
    global key_history_dict, last_update_ms, speed_acc, steer_acc, speed, steer
    d_speed = 0
    d_steer = 0
    for key_str, change_list in key_history_dict:
        change = 0
        for i in range(len(change_list)):
            d_time = 0
            if i == 0:
                d_time = int(round(time()*1000)) - last_update_ms
            d_time = int(round(time()*1000)) - change_list[i][1]
            if key_str is "Up" or key_str is "Down":
                mult = 1
                if key_str is "Down":
                    mult = -1
                d_speed += mult * int(round(d_time/speed_acc))
            elif key_str is "Left" or key_str is "Right":
                mult = 1
                if key_str is "Right":
                    mult = -1
                d_steer += mult * int(round(d_time/steer_acc))

    last_update_ms = int(round(time()*1000))


def get_cur_speed_and_steer():
    global speed, steer
    update()
    return speed, steer


def set_speed_change(key, if_pressed):
    global speed, speed_change, speed_acc
    cur_ms = int(round(time()*1000))
    d_time_ms = cur_ms - last_key_press_ms_dict[key]
    if if_pressed:
        if speed != 0:
            sign = -1
            if speed < 0:
                sign = 1
            speed_change += sign * int(round(d_time_ms / speed_acc))
            if abs(speed_change) > abs(speed):
                speed_change = speed
    else:
        sign = 1
        if key == "Down":
            sign = -1
        speed_change += sign * int(round(d_time_ms / speed_acc))


def on_key_event(key_str, if_pressed):
    global last_key_press_ms_dict, speed, steer, speed_acc, steer_acc, speed_change, steer_change
    cur_ms = int(round(time()*1000))
    if key_str == "Up" or key_str == "Down":
        set_speed_change(key_str, if_pressed)
        if speed_change != 0:
            if abs(speed + speed_change) > max_speed:
                sign = 1
                if speed_change < 0:
                    sign = -1
                speed_change - (speed + speed_change - sign * max_speed)
            speed = speed_change
            speed_change = 0

    print("Speed: {}, speed_change: {}".format(speed, speed_change))

    last_key_press_ms_dict[key_str] = cur_ms
    return
