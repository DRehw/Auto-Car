from tkinter import EventType
__key_dict = {}
__key_func_dict = {}


def on_key_event(key_event):
    if key_event.type == EventType.KeyPress and not __key_dict.get(key_event.keysym):
        __key_dict[key_event.keysym] = True
        notify_observer(key_event.keysym, True)
    elif key_event.type == EventType.KeyRelease:
        __key_dict[key_event.keysym] = False
        notify_observer(key_event.keysym, False)


def register_observer_func(key_str, func):
    if "list" not in str(type(key_str)):
        key_str = [key_str]
    for key in key_str:
        if __key_func_dict.get(key):
            __key_func_dict[key] = __key_func_dict[key].append(func)
        else:
            __key_func_dict[key] = [func]


def unregister_observer_func(func):
    for key_str, func_list in __key_func_dict:
        if func in func_list:
            func_list.remove(func)


def notify_observer(key_str, if_pressed):
    if __key_func_dict.get(key_str):
        for func in __key_func_dict.get(key_str):
            try:
                func(key_str, if_pressed)
            except(Exception) as e:
                print("Error {} in function or method: {}".format(str(e), str(func).split(" ")[2]))


def is_pressed(key):
    if __key_dict.get(key):
        return True
    else:
        return False
