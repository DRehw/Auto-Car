"""
Created on May 11, 2019

@author: Dave
"""

import tkinter as tk


class MainGui:
    """
    classdocs
    """

    def __init__(self, controller):
        """
        Constructor
        """
        self.controller = controller
        self.controller.gui_init(self)
        self.window = tk.Tk()
        self.window.title("Auto-Car Debug")
        self.window.bind("<KeyRelease>", self.key_release)
        self.window.bind("<KeyPress>", self.key_press)
        self.window.option_add("*font", "Helvetica 14")
        info_frame = tk.Frame(self.window)
        info_frame.grid(row=0,
                        column=0,
                        padx=(10, 10),
                        pady=(10, 10))
        button_frame = tk.Frame(self.window)
        button_frame.grid(row=0,
                          column=1,
                          padx=(10, 10),
                          pady=(10, 10),
                          sticky=tk.N)

        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=1)

        self.speedScale = tk.Scale(info_frame,
                                   from_=15,
                                   to=-15,
                                   orient=tk.VERTICAL,
                                   label="Speed",
                                   width=20,
                                   length=300,
                                   command=self.controller.on_speed_change)
        self.speedScale.set(0)
        self.speedScale.bind("<ButtonRelease-1>", self.speed_scale_mouse_release)
        self.speedScale.grid(row=0, column=1, columnspan=1)
        self.steerScale = tk.Scale(info_frame,
                                   from_=-30,
                                   to=30,
                                   orient=tk.HORIZONTAL,
                                   label="Steering",
                                   width=20,
                                   length=300,
                                   command=self.controller.on_steer_change)
        self.steerScale.set(0)
        self.steerScale.bind("<ButtonRelease-1>", self.steer_scale_mouse_release)
        self.steerScale.grid(row=0, column=0, columnspan=1)
        tk.Button(info_frame, text="Send Command", command=self.send_mqtt).grid(row=2,
                                                                                column=0,
                                                                                padx=(0, 0),
                                                                                sticky=tk.W+tk.E)
        tk.Button(info_frame, text="Stop", command=self.reset_slider).grid(row=2,
                                                                           column=1,
                                                                           padx=(0, 0),
                                                                           sticky=tk.W+tk.E)
    
        tk.Button(button_frame,
                  text="Connect to local Broker",
                  command=self.connect_to_local_broker).grid(row=1,
                                                             column=0,
                                                             sticky=tk.W+tk.E+tk.N,
                                                             pady=(5, 5))
        tk.Button(button_frame,
                  text="Connect to Car Broker",
                  command=self.connect_to_car).grid(row=1,
                                                    column=1,
                                                    sticky=tk.W+tk.E,
                                                    pady=(5, 5))
        tk.Button(button_frame,
                  text="Subscribe to 'aadc/rc','aadc/sensor','aadc/lidar'",
                  command=self.subscribe).grid(row=2,
                                               column=0,
                                               columnspan=2,
                                               sticky=tk.W+tk.E,
                                               pady=(5, 5))
        tk.Button(button_frame,
                  text="Open Cmd at Mosquitto path",
                  command=self.cmd_send).grid(row=3,
                                              column=0,
                                              columnspan=2,
                                              sticky=tk.W+tk.E,
                                              pady=(5, 5))
        tk.Button(button_frame,
                  text="Send test messages",
                  command=self.controller.send_test).grid(row=4,
                                                          column=0,
                                                          columnspan=2,
                                                          sticky=tk.W+tk.E,
                                                          pady=(5, 5))
        self.ignoreLogicButon = tk.Button(button_frame,
                                          text="Ignore Logic",
                                          command=self.controller.toggle_ignore_logic_button,
                                          bg="red")
        self.ignoreLogicButon.grid(row=5,
                                   column=0,
                                   columnspan=2,
                                   sticky=tk.W+tk.E+tk.S,
                                   pady=(5, 5))
        self.window.mainloop()

    def speed_scale_mouse_release(self, event):
        self.speedScale.set(0)
        self.controller.send_command()

    def steer_scale_mouse_release(self, event):
        self.steerScale.set(0)
        self.controller.send_command()

    @staticmethod
    def key_press(event):
        print(event.keysym)
        print(event.type)

    @staticmethod
    def key_release(event):
        print(event.keysym)
        print(event.type)

    def ignore_logic_set_color(self, color):
        self.ignoreLogicButon.configure(bg=color)
    
    def send_mqtt(self):
        self.controller.send_command()
        return
    
    def reset_slider(self):
        self.speedScale.set(0)
        self.steerScale.set(0)
        self.controller.send_command()
        return
    
    def connect_to_local_broker(self):
        self.controller.start_mosquitto_async()
        return
    
    def connect_to_car(self):
        self.controller.connect_to_car()
        return
    
    def subscribe(self):
        self.controller.subscribe()
        return
    
    def cmd_send(self):
        self.controller.start_cmd_mosq_path()
        return
