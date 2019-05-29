from KeyHandler import is_pressed
from threading import Thread
from time import time, sleep
__controller = None
__speed_interval = 20
__steer_interval = 4
__max_speed = 15
__max_steer = 30
__speed = 0
__steer = 0
__no_change = False
__stop = False


def start_loop(controller):
    global __stop, __controller
    __controller = controller
    proc = Thread(target=loop)
    proc.start()


def loop():
    global __speed, __steer, __max_speed, __max_steer, __no_change, __stop, \
        __speed_interval, __steer_interval, __controller
    speed_mark = int(round(time() * 100))
    steer_mark, mark, left_mark, right_mark, up_mark, down_mark, brake_mark = [speed_mark] * 7
    brake = False
    brake_interval = 200
    has_changed = False
    v1 = False

    while True:
        current_time = int(round(time() * 100))
        if v1:
            if current_time - speed_mark >= __speed_interval:
                speed_mark = current_time
                if is_pressed("Up"):
                    if -__max_speed <= __speed < __max_speed:
                        __speed += 1
                        has_changed = True
                if is_pressed("Down"):
                    if -__max_speed < __speed <= __max_speed:
                        __speed -= 1
                        has_changed = True
            if current_time - steer_mark >= __steer_interval:
                steer_mark = current_time
                if is_pressed("Left"):
                    if -__max_steer < __steer <= __max_steer:
                        __steer -= 1
                        has_changed = True
                if is_pressed("Right"):
                    if -__max_steer <= __steer < __max_steer:
                        __steer += 1
                        has_changed = True
        else:
            if current_time - mark >= 1:
                mark = current_time
                if is_pressed("Up") and not brake:
                    if current_time - up_mark >= __speed_interval:
                        up_mark = current_time
                        if -__max_speed <= __speed < __max_speed:
                            __speed += 1
                            has_changed = True
                if is_pressed("Down") and not brake:
                    if current_time - down_mark >= __speed_interval:
                        down_mark = current_time
                        if -__max_speed < __speed <= __max_speed:
                            __speed -= 1
                            has_changed = True
                if is_pressed("Right") and not brake:
                    if current_time - right_mark >= __steer_interval:
                        right_mark = current_time
                        if -__max_steer <= __steer < __max_steer:
                            __steer += 1
                            has_changed = True
                if is_pressed("Left") and not brake:
                    if current_time - left_mark >= __steer_interval:
                        left_mark = current_time
                        if -__max_steer < __steer <= __max_steer:
                            __steer -= 1
                            has_changed = True
                if is_pressed("space") and not brake:
                    print("Brake")
                    brake = True
                    __speed = 0
                    brake_mark = current_time
                    has_changed = True
                if brake and current_time - brake_mark >= brake_interval:
                    print("Turn off brake")
                    brake = False

        if has_changed:
            __controller.set_speed(__speed)
            __controller.set_steer(__steer)
            has_changed = False
        if __stop:
            break
    __stop = False
    sleep(0.04)


def stop_proc():
    global __stop
    __stop = True
