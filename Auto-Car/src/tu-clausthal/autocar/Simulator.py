from os import path
from threading import Thread
from time import time, sleep
from json import loads

from CurrentData import CurrentData

__is_recording = False
__is_playing = False
__buffer_size = -1  # -1 would use system default buffer size
__sim_buffer_size = 20  # number of messages before a write operation
__sim_buffer = []
__sim_file_loc = ""
__stop_thread = False
__thread = None


def start_recording(location):
    global __sim_file_loc, __is_recording
    # __sim_file = open(location, "w+")
    try:
        file = open(location, "w")
    except (OSError, IOError) as e:
        print("Could not open or create file: '{}'".format(location))
        return
    __sim_file_loc = location
    __is_recording = True
    file.close()
    CurrentData.register_method_as_observer(on_new_data)
    print("Started recording.")
    return


def stop_recording():
    global __is_recording, __sim_buffer
    if __is_recording:
        if len(__sim_buffer) > 0:
            write_buffer_to_file()
        CurrentData.remove_method_as_observer(on_new_data)
        __is_recording = False
        print("Stopped recording!")
    else:
        print("Currently not recording.")
    return


def on_new_data(new_data_str):
    # print("On new data")
    global __sim_buffer, __sim_buffer_size
    msg = None
    if new_data_str == "lidar":
        msg = ("aadc/lidar", CurrentData.get_lidar_json())
    elif new_data_str == "sensor":
        msg = ("aadc/sensor", CurrentData.get_sensor_json())
    if msg:
        timestamp = msg[1].get("timestamp")
        i = 0
        for i in range(len(__sim_buffer)):
            if __sim_buffer[i][0] > timestamp:
                i -= 1
                break
        __sim_buffer.insert(i+1, (timestamp, msg))
        # print("Insert to buffer")
        if len(__sim_buffer) >= __sim_buffer_size:
            # print("Write buffer to file")
            write_buffer_to_file()


def write_buffer_to_file():
    global __sim_buffer, __sim_file_loc
    if len(__sim_file_loc) > 4:
        try:
            file = open(__sim_file_loc, "a")
        except (OSError, IOError) as e:
            print("Could not open file: '{}'".format(__sim_file_loc))
            return
        for entry in __sim_buffer:
            new_line = "\n"
            file.write(entry[1][0] + "," + str(entry[1][1]) + new_line)
        file.close()
        __sim_buffer = []
    return


def start_playback(location, mqtt_connection):

    if not path.isfile(location):
        print("File path {} does not exist.".format(location))
    elif not location[-4:] == ".txt":
        print("No text file selected!")
    else:
        global __thread, __stop_thread
        __stop_thread = False
        __thread = Thread(target=playback_thread, args=[location, mqtt_connection, __stop_thread])
        __thread.start()
    return


def stop_playback():
    global __thread, __stop_thread, __is_playing
    if __is_playing:
        print("stopping playback")
        __stop_thread = True
    return


def playback_thread(location, mqtt_connection, __stop_thread):

    def get_n_next_lines(file, n):
        lines = []
        reached_eof = False
        for i in range(n):
            line = file.readline()
            if line == "":
                reached_eof = True
                return lines, reached_eof
            line = line.split(",", 1)
            if len(line) != 2:
                print("Wrong format of data in line: '{}' in file: '{}'".format(line, location))
                return [], reached_eof
            try:
                line[1] = line[1].replace("'", '"')
                loads(line[1])
            except ValueError as e:
                print("Could not parse line: '{}' of file: '{}'".format(line, location))
                return [], reached_eof
            lines.append(line)
        return lines, reached_eof

    global __is_playing
    if location and len(location) > 4 and mqtt_connection:
        __is_playing = True
        last_timestamp = 0
        target_os_time = 0
        try:
            file = open(location, "r")
        except (OSError, IOError) as e:
            print("Could not open file: ".format(location))
            return
        if file:
            reached_eof = False
            while not reached_eof:
                lines, reached_eof = get_n_next_lines(file, 20)
                if len(lines) > 0:
                    index = 0
                    while not reached_eof:
                        if __stop_thread:
                            print("Stopped successful")
                            return
                        current_ms = int(round(time() * 1000))
                        if last_timestamp == 0 or current_ms >= target_os_time:
                            last_timestamp = loads(lines[index][1]).get("timestamp")
                            if last_timestamp is None:
                                print("Could not get Timestamp!")
                                return
                            mqtt_connection.publish(lines[index][0], lines[index][1])
                            if index+1 >= len(lines):
                                if reached_eof:
                                    print("Played back all data.")
                                    return
                                break
                            target_os_time = current_ms + (loads(lines[index + 1][1]).get("timestamp") - last_timestamp)
                            index += 1
                        else:
                            sleep(0.03)
                else:
                    print("Played back all data.")
                    return
