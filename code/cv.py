"""
Helpers:
https://shop.pimoroni.com/products/rgb-encoder-breakout?variant=32236590399571
https://github.com/pimoroni/ioe-python/tree/master/examples

I2S Bus (pins 12, 35, 40) (gpios 79, 76, 78)
I2C Bus for inputs (cv, gate and rotary encoder) (pins 3, 4) (gpio )
"""

import time
from ads1015 import ADS1015
from multiprocess import ProcessInput
from multiprocessing import Event
import concurrent.futures
import Jetson.GPIO as GPIO
import numpy as np


class Cv(ProcessInput):
    def __init__(self, config):
        super().__init__()
        # Create callback and event to deal with multiprocess
        self._callback = callback
        self._signal = Event()
        # Set signaling
        channels = ['in0/ref', 'in1/ref', 'in2/ref']
        i2c_addr = [0x48, 0x49]

        ads1015 = ADS1015()
        # Get the type of the chipset
        chip_type = ads1015.detect_chip_type()
        print("Found: {}".format(chip_type))
        # What for ?
        ads1015.set_mode('single')
        ads1015.set_programmable_gain(2.048)
        # Set sample rate
        ads1015.set_sample_rate(16000)
        # Get reference voltage
        self._ref = ads1015.get_reference_voltage()
        print("Reference voltage: {:6.3f}v \n".format(reference))
        # Assign cvs and gates
        self._cv_type = [config["hardware"]["in0"],
                         config["hardware"]["in1"],
                         config["hardware"]["in2"],
                         config["hardware"]["in3"],
                         config["hardware"]["in4"],
                         config["hardware"]["in5"]]
        self._low_threshold = self._ref + 1
        self._buffer = config["audio"]["buffers"]

        try:
            while True:
                for channel in CHANNELS:
                    value = ads1015.get_compensated_voltage(channel=channel, reference_voltage=reference)
                    print("{}: {:6.3f}v".format(channel, value))

                print("")
                time.sleep(0.5)

        except KeyboardInterrupt:
            pass

    def callback(self, state, queue, delay=0.001):
        """
            Function for reading the current CV values.
            Also updates the shared memory (state) with all CV values
            Parameters:
                state:      [Manager]
                            Shared memory through a Multiprocessing manager
                queue:      [Queue]
                            Shared memory queue through a Multiprocessing queue
                delay:      [int], optional
                            Specifies the wait delay between read operations [default: 0.001s]
        """
        try:
            self.read_loop(state)
        except KeyboardInterrupt:
            pass

    def read_loop(self, state):
        """
        Function to create thread that read each cv values
        :param state: shared memory
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=(len(self._cvs) * len(self._channels))) as executor:
            cur_v = 0
            futures_cv = []
            for cv in self._cvs:
                futures_cv.append(executor.submit(self.thread_read, cv=cv, cv_full_id=cur_v, state=state))
                cur_v += 1
            for futures_cv in concurrent.futures.as_completed(futures_cv):
                futures_cv.result()

    def thread_read(self, cv, cv_full_id, state):
        """
        Function to read the value in each thread
        :param cv: pin of cv
        :param cv_full_id: id of the cv
        :param state: shared memory
        """
        buffer = []
        n_inactive = []
        for _ in range(3):
            buffer.append([])
            n_inactive.append(0)
        while True:
            c = 0
            for chan in self._channels:
                cv_id = (cv_full_id * 3) + c
                # Set the behavior if triggering a gate input
                if self._cv_type[cv_id] == "gate":
                    value = cv.get_compensated_voltage(channel=chan, reference_voltage=self._ref)
                    self.handle_gate(cv_id, value, state)
                # Set the behavior if triggering a CV input
                if self._cv_type[cv_id] == "cv":
                    value = cv.get_compensated_voltage(channel=chan, reference_voltage=self._ref)
                    buffer[cv_id % 3].append(value)
                    if len(buffer[cv_id % 3]) > self._buffer:
                        buffer[cv_id % 3].pop(0)
                    if np.abs(value - state['cv'][cv_id]) < 0.05:
                        n_inactive[cv_id % 3] += 1
                        if n_inactive[cv_id % 3] > self._n_active and state['cv_active'][cv_id]:
                            state['cv_active'][cv_id] = 0
                    else:
                        if not state['cv_active'][cv_id]:
                            state['cv_active'][cv_id] = 1
                        n_inactive[cv_id % 3] = 0
                        self.handle_cv(cv_id, buffer[cv_id % 3], state)
                        state['cv'][cv_id] = value
                c += 1

    def handle_gate(self, cv_id, value, state):
        cur_state = state["cv"][cv_id]
        cur_time = time.monotonic()
        if cur_state == 0:
            if value > self._low_threshold:
                state['cv'][cv_id] = cur_time
                self._callback("gate", cv_id, value)
        else:
            elapsed_time = cur_time - state['cv'][cv_id]
            if (value < self._low_threshold) and (elapsed_time > self._gate_time):
                state["cv"][cv_id] = 0

    def handle_cv(self, cv_id, buffer, state):
        if len(buffer) == self._buffer:
            state['buffer'][cv_id] = buffer.copy()
