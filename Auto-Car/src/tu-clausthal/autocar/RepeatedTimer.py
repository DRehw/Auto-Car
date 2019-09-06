from threading import Timer
from time import time
from traceback import print_exc


class RepeatedTimer(object):
    """
    Class RepeatedTimer implements a self-correcting timer (to remove drift) using class Timer from threading,
    which runs a function every interval_ms milli seconds.
    """

    def __init__(self, interval_ms, function):
        """
        :param interval_ms: Interval for the timer
        :param function: Function to be executed when the timer runs out
        """
        self.interval_ms = interval_ms
        self.function = function
        self._start_time_ms = int(round(time() * 1000))
        self._timer = None
        self.is_running = False
        self.start()

    def _run(self):
        """
        Private function _run, which is executed whenever the timer runs out. This function calls the function given in
        the constructor.
        :return:
        """
        # Calculate the time in ms the timer is off from the target time
        current_time_ms = int(round(time() * 1000))
        time_dif_ms = current_time_ms - self._start_time_ms
        current_offset_ms = time_dif_ms % self.interval_ms
        if current_offset_ms > self.interval_ms / 2:
            compensation_interval_ms = self.interval_ms + (self.interval_ms - current_offset_ms)
        else:
            compensation_interval_ms = self.interval_ms-current_offset_ms
        self._timer = Timer(compensation_interval_ms/1000, self._run)
        self._timer.start()
        try:
            self.function()
        except Exception:
            print_exc()

    def start(self):
        """
        Starts the timer
        :return:
        """
        if not self.is_running:
            self._timer = Timer(self.interval_ms/1000, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        """
        Stops the timer
        :return:
        """
        if self.is_running:
            self._timer.cancel()
            self.is_running = False
