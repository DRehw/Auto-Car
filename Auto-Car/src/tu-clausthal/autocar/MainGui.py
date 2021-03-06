"""
Created on May 11, 2019

@author: Dave
"""

import tkinter as tk
from time import time
from traceback import print_exc
from sys import gettrace


small_map = False


class MainGui:
    """
    classdocs
    """

    def __init__(self, controller, oc_map):
        global small_map
        map_edge = 800
        """
        Constructor
        """
        self.controller = controller
        self.controller.gui_init(self)
        self.map = oc_map
        self.map.gui_init(self)
        self.window = tk.Tk()
        self.window.title("Auto-Car Debug")
        self.window.option_add("*font", "Helvetica 9")
        self.record_path_string_var = tk.StringVar()
        self.play_path_string_var = tk.StringVar()
        self.__display_speed = tk.StringVar()
        self.__display_steer = tk.StringVar()
        self.__display_pos = tk.StringVar()
        self.__display_heading = tk.StringVar()
        self.image = None
        self.image_on_canvas = None
        self.draw_map_press_ms = int(round(time() * 1000))
        self.debug_gui = gettrace()

        """
        FRAMES
        """

        main_frame = tk.Frame(self.window)
        main_frame.grid(row=2,
                        column=2,
                        padx=(5, 5),
                        pady=(5, 5),
                        sticky=tk.N + tk.S + tk.E + tk.W)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)

        if self.debug_gui:
            control_frame = tk.Frame(self.window)
            control_frame.grid(row=0,
                               column=0,
                               sticky=tk.N,
                               padx=(10, 10),
                               pady=(10, 10))
            button_frame = tk.Frame(self.window)
            button_frame.grid(row=0,
                              column=1,
                              padx=(10, 10),
                              pady=(10, 10),
                              sticky=tk.N)
            simulator_frame = tk.Frame(self.window)
            simulator_frame.grid(row=1,
                                 column=0,
                                 columnspan=2,
                                 padx=(10, 10),
                                 pady=(10, 10),
                                 sticky=tk.E + tk.W + tk.N + tk.S)
            simulator_frame.columnconfigure(0, weight=1)
            simulator_frame.columnconfigure(1, weight=1)

            simulator_record_frame = tk.Frame(simulator_frame)
            simulator_record_frame.grid(row=0,
                                        column=0,
                                        sticky=tk.W + tk.E + tk.N + tk.S,
                                        pady=(5, 5),
                                        padx=(5, 5))
            simulator_record_frame.columnconfigure(0, weight=3)
            simulator_record_frame.columnconfigure(1, weight=1)

            simulator_play_frame = tk.Frame(simulator_frame)
            simulator_play_frame.grid(row=0,
                                      column=1,
                                      sticky=tk.W + tk.E + tk.N + tk.S,
                                      pady=(5, 5),
                                      padx=(5, 5))
            simulator_play_frame.columnconfigure(0, weight=3)
            simulator_play_frame.columnconfigure(1, weight=1)

        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=1)

        """
        Main Window widgets
        """

        if small_map:
            map_edge /= 2
        self.map_canvas = tk.Canvas(self.window, width=map_edge, height=map_edge, bg="white")
        self.map_canvas.grid(row=0,
                             column=2,
                             rowspan=2,
                             padx=(5, 5),
                             pady=(5, 5))
        self.image_on_canvas = self.map_canvas.create_image(0, 0, image=tk.PhotoImage(), anchor=tk.NW)
        self.car_rect = self.map_canvas.create_rectangle(0, 0, 1, 1, fill='red')

        """
        Main Frame Widgets
        """

        self.connect_to_car_btn = tk.Button(main_frame,
                                            text="Connect to Car Broker",
                                            command=self.connect_to_car)
        self.connect_to_car_btn.grid(row=0,
                                     column=1,
                                     rowspan=2,
                                     padx=(1, 1),
                                     pady=(1, 1),
                                     sticky=tk.E + tk.W + tk.N + tk.S)

        self.stop_btn = tk.Button(main_frame,
                                  text="Stop",
                                  command=self.stop)
        self.stop_btn.grid(row=1,
                           column=0,
                           padx=(1, 1),
                           pady=(1, 1),
                           sticky=tk.E + tk.W + tk.N + tk.S)

        tk.Button(main_frame,
                  text="Reset Map",
                  command=self.controller.reset_map_btn).grid(row=0,
                                                              column=2,
                                                              columnspan=1,
                                                              sticky=tk.E + tk.W + tk.N + tk.S,
                                                              padx=(1, 1),
                                                              pady=(1, 1))
        tk.Button(main_frame,
                  text="Reset Euler",
                  command=self.controller.reset_euler_btn).grid(row=1,
                                                                column=2,
                                                                columnspan=1,
                                                                sticky=tk.E + tk.W + tk.N + tk.S,
                                                                padx=(1, 1),
                                                                pady=(1, 1))
        self.autopilot_control_btn = tk.Button(main_frame,
                                               text="Enable Autopilot",
                                               command=self.controller.toggle_autopilot_button)

        self.autopilot_control_btn.grid(row=0,
                                        column=0,
                                        columnspan=1,
                                        sticky=tk.E + tk.W + tk.N + tk.S,
                                        padx=(1, 1),
                                        pady=(1, 1))

        """
        Control Frame Widgets
        """

        if self.debug_gui:
            self.speed_scale = tk.Scale(control_frame,
                                        from_=15,
                                        to=-15,
                                        orient=tk.VERTICAL,
                                        label="Speed",
                                        width=20,
                                        length=300,
                                        command=self.controller.on_speed_change_scale)
            self.speed_scale.set(0)
            self.speed_scale.bind("<ButtonRelease-1>", self.speed_scale_mouse_release)
            self.speed_scale.grid(row=0, column=1, columnspan=1)
            self.steer_scale = tk.Scale(control_frame,
                                        from_=-30,
                                        to=30,
                                        orient=tk.HORIZONTAL,
                                        label="Steering",
                                        width=20,
                                        length=300,
                                        command=self.controller.on_steer_change_scale)
            self.steer_scale.set(0)
            self.steer_scale.grid(row=0, column=0, columnspan=1)
            tk.Button(control_frame, text="Send Command", command=self.send_mqtt).grid(row=2,
                                                                                       column=0,
                                                                                       padx=(0, 0),
                                                                                       sticky=tk.W+tk.E)


            """
            Debug/Connection Frame Widgets
            """

            tk.Button(button_frame,
                      text="Open Cmd at Mosquitto path",
                      command=self.cmd_send).grid(row=1,
                                                  column=0,
                                                  columnspan=2,
                                                  sticky=tk.W+tk.E,
                                                  pady=(5, 5))
            tk.Button(button_frame,
                      text="Send test messages",
                      command=self.controller.send_test_btn).grid(row=2,
                                                                  column=0,
                                                                  columnspan=2,
                                                                  sticky=tk.W+tk.E,
                                                                  pady=(5, 5))
            self.manual_control_btn = tk.Button(button_frame,
                                                text="Manual Control",
                                                command=self.controller.toggle_manual_control_button)
            self.manual_control_btn.grid(row=0,
                                         column=0,
                                         columnspan=2,
                                         sticky=tk.W+tk.E+tk.S,
                                         pady=(5, 5))

            self.speed_label = tk.Label(button_frame, textvariable=self.__display_speed)
            self.speed_label.grid(row=6,
                                  column=1,
                                  sticky=tk.W + tk.E + tk.N,
                                  pady=(5, 5))
            self.steer_label = tk.Label(button_frame, textvariable=self.__display_steer)
            self.steer_label.grid(row=6,
                                  column=0,
                                  sticky=tk.W + tk.E + tk.N,
                                  pady=(5, 5))
            self.pos_label = tk.Label(button_frame, textvariable=self.__display_pos)
            self.pos_label.grid(row=7,
                                column=0,
                                sticky=tk.W + tk.E + tk.N,
                                pady=(5, 5))
            self.heading_label = tk.Label(button_frame, textvariable=self.__display_heading)
            self.heading_label.grid(row=7,
                                    column=1,
                                    sticky=tk.W + tk.E + tk.N,
                                    pady=(5, 5))

            """
            Simulator Play Frame Widgets
            """

            tk.Label(simulator_play_frame, text="Play data").grid(row=0,
                                                                  column=0,
                                                                  columnspan=2,
                                                                  padx=(5, 5),
                                                                  pady=(5, 5))
            self.play_data_path_entry = tk.Entry(simulator_play_frame,
                                                 textvariable=self.play_path_string_var,
                                                 font="Helvetica 9")
            self.play_data_path_entry.grid(row=1,
                                           column=0,
                                           sticky=tk.W + tk.E,
                                           padx=(5, 5),
                                           pady=(5, 5))

            self.play_data_select_path_btn = tk.Button(simulator_play_frame,
                                                       text="Change Path",
                                                       command=self.controller.path_change_play_btn)
            self.play_data_select_path_btn.grid(row=1,
                                                column=1,
                                                sticky=tk.E + tk.W + tk.N + tk.S,
                                                padx=(5, 5),
                                                pady=(5, 5))

            self.play_data_play_btn = tk.Button(simulator_play_frame,
                                                text="Play",
                                                command=self.controller.play_btn)
            self.play_data_play_btn.grid(row=2,
                                         column=0,
                                         sticky=tk.N + tk.S + tk.E + tk.W,
                                         padx=(5, 5),
                                         pady=(5, 5))

            self.play_data_stop_btn = tk.Button(simulator_play_frame,
                                                text="Stop Playing",
                                                command=self.controller.stop_playing_btn,
                                                font="Helvetica 10")
            self.play_data_stop_btn.grid(row=2,
                                         column=1,
                                         sticky=tk.N + tk.S + tk.E + tk.W,
                                         padx=(5, 5),
                                         pady=(5, 5))

            """
            Simulator Record Frame Widgets
            """

            tk.Label(simulator_record_frame, text="Record data").grid(row=0,
                                                                      column=0,
                                                                      columnspan=2,
                                                                      padx=(5, 5),
                                                                      pady=(5, 5))
            self.record_data_path_entry = tk.Entry(simulator_record_frame,
                                                   textvariable=self.record_path_string_var,
                                                   font="Helvetica 9")
            self.record_data_path_entry.grid(row=1,
                                             column=0,
                                             sticky=tk.W + tk.E,
                                             padx=(5, 5),
                                             pady=(5, 5))

            self.record_data_select_path_btn = tk.Button(simulator_record_frame,
                                                         text="Change Path",
                                                         command=self.controller.path_change_record_btn)
            self.record_data_select_path_btn.grid(row=1,
                                                  column=1,
                                                  sticky=tk.E + tk.W + tk.N + tk.S,
                                                  padx=(5, 5),
                                                  pady=(5, 5))

            self.record_data_record_btn = tk.Button(simulator_record_frame,
                                                    text="Start Record",
                                                    command=self.controller.record_btn)
            self.record_data_record_btn.grid(row=2,
                                             column=0,
                                             sticky=tk.N + tk.S + tk.E + tk.W,
                                             padx=(5, 5),
                                             pady=(5, 5))

            self.record_data_stop_btn = tk.Button(simulator_record_frame,
                                                  text="Stop Recording",
                                                  command=self.controller.stop_recording_btn,
                                                  font="Helvetica 10")
            self.record_data_stop_btn.grid(row=2,
                                           column=1,
                                           sticky=tk.N + tk.S + tk.E + tk.W,
                                           padx=(5, 5),
                                           pady=(5, 5))

        self.controller.gui_init(self)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()


    def on_closing(self):
        """
        closes all windows
        """
        self.controller.on_window_close()
        self.window.destroy()
        return


    def speed_scale_set(self, speed):
        """
        set speed interval [-15,15]
        """
        if -15 <= speed <= 15:
            self.speed_scale.set(speed)


    def steer_scale_set(self, steer):
        """
        set steer interval [-30,30]
        """
        if -30 <= steer <= 30:
            self.steer_scale.set(steer)


    def speed_scale_mouse_release(self, event):
        """
        if mouse is released set speed to 0
        """
        self.speed_scale.set(0)


    def update_map(self, tk_photo_image):
        """
        updates map with newest picture of the occupancy grid
        """
        self.image = tk_photo_image
        self.map_canvas.itemconfig(self.image_on_canvas, image=self.image)


    def connect_to_car_btn_set_color(self, color):
        """
        sets color of buttons if pressed
        """
        self.connect_to_car_btn.configure(bg=color)

    def manual_control_btn_set_color(self, color):
        self.manual_control_btn.configure(bg=color)
        return

    def autopilot_control_btn_set_color(self, color):
        self.autopilot_control_btn.configure(bg=color)

    def stop_btn_set_color(self, color):
        self.stop_btn.configure(bg=color)
        return

    """
    Simulator Functions
    """

    def set_record_path(self, path):
        self.record_path_string_var.set(path)
        return

    def get_record_path(self):
        return self.record_path_string_var.get()

    def set_play_path(self, path):
        self.play_path_string_var.set(path)
        return

    def get_play_path(self):
        return self.play_path_string_var.get()


    def set_auto_speed_label_text(self, speed):
        """
        displays current speed
        """
        self.__display_speed.set((speed-90)*(-1))


    def set_auto_steer_label_text(self, steer):
        """
        displays current steer
        """
        self.__display_steer.set((steer-90)*(-1))


    def update_car_pos_label(self, car_pos):
        """
        update car position on map
        """
        x = car_pos[0]/10
        y = car_pos[1]/10
        self.__display_pos.set("{:6.1f} | {:6.1f}".format(x, y))


    def update_car_heading_label(self, heading):
        """
        sets car heading label
        """
        self.__display_heading.set("{:4.1f}".format(heading))

    def send_mqtt(self):
        return
    
    def stop(self):
        try:
            self.controller.stop_cmd_btn()
        except Exception:
            print_exc()
        return


    def connect_to_local_broker(self):
        """
        connect to car or local broker
        """
        self.controller.start_mosquitto_async()
        return
    
    def connect_to_car(self):
        self.controller.connect_to_car_btn()
        return
    
    def subscribe(self):
        self.controller.subscribe()
        return


    def cmd_send(self):
        """
        send drive commands
        """
        self.controller.start_cmd_mosq_path()
        return
