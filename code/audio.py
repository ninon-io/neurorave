"""
We need to create new child processes in our program in order to execute code concurrently.
Python provides the ability to create and manage new processes via the multiprocessing.Process class.
In concurrent programming, sometimes we need to coordinate processes with a boolean variable.
This might be to trigger an action or signal some result: this can be achieved using an event object.

"""

import sounddevice as sd

from multiprocessing import Event, Process

from models.ddsp import DDSP
from models.nsf_impacts import NSF

from multiprocess import ProcessInput


class Audio(ProcessInput):
    def __init__(self, config):
        super().__init__()
        # Setup audio callback
        self._callback = callback()
        # Create our own signal for multiprocessing communication
        self._signal = Event()
        # Configure parameters
        self._sr = config["audio"]["sr"]
        self._model = config["model"]["name"]
        # Set devices default
        self.set_default()
        # Set model
        self.load_model()

    def callback(self, state, queue):
        # First perform a model burn-in
        print('Performing model burn-in')
        # state["audio"]["mode"].value = config.audio.mode_burnin
        self.model_burn_in()
        # Then switch to wait (idle) mode
        print('Audio ready')
        state["audio"]["mode"].value = config.audio.mode_idle
        while True:
            self._signal.wait()
            if self._signal.is_set():
                self._signal.clear()
                self.handle_signal_event(state)

    def model_burn_in(self):
        '''
            The model burn-in allows to warm up the GPU.
            The first PyTorch Tensor creation is extremely slow.
            Therefore, we just make two useless pass during the init.
        '''
        self._model.preload()

    def set_defaults(self):
        '''
            Sets default parameters for the soundevice library.
        '''
        sd.default.samplerate = self._sr
        sd.default.device = 1
        sd.default.latency = 'low'
        sd.default.dtype = 'float32'
        sd.default.blocksize = 0
        sd.default.clip_off = False
        sd.default.dither_off = False
        sd.default.never_drop_input = False

    def load_model(self):
        if self._model_name == 'ddsp':
            self._model = DDSP()
        elif self._model_name == 'nsf':
            self._model = NSF()
        elif self._model == 'faderave':
            self._model = FadeRave()
        else:
            raise NotImplementedError

    def handle_signal_event(self, state):
        cur_event = state["audio"]["event"]
        if cur_event in [config.event.input_0]:
            self.in0_activated()
        if cur_event in [config.event.input_1]:
            self.in1_activated()
        if cur_event in [config.event.input_2]:
            self.in2_activated()
        if cur_event in [config.event.input_3]:
            self.in3_activated()
        if cur_event in [config.event.input_4]:
            self.in4_activated()
        # TODO: implement each activation of input for neurorave
