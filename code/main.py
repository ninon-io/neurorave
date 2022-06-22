import Jetson.GPIO as GPIO

from audio import Audio
from button import Button
from cv import Cv
from rotary import Rotary

import yaml
from effortless_config import Config


class Args(Config):
    CONFIG = f"config.yaml"


with open(Args.CONFIG, "r") as config:
    config = yaml.safe_load(config)


class NeuroRave:
    def __init__(self):
        # Init shared state
        self._state = None
        self._manager = None
        self.init_state()
        # Classes instantiation
        self._audio = Audio(config)
        self._button = Button()
        self._cvs = Cv(config)
        self._rotary = Rotary()
        # Perform GPIO cleanup
        GPIO.cleanup()
        # Need to import Screen after cleanup
        from screen import Screen
        self._screen = Screen(self.callback_screen)
        # List of objects to create processes
        self._objects = [self._audio, self._screen, self._rotary, self._cvs, self._button]
        # Find number of CPUs
        self._nb_cpus = config["hardware"]["number_cpu"]
        # Number of available inputs
        self._number_input = config["hardware"]["number_input"]
        # Create a pool of jobs
        self._pool = mp.Pool(self._nb_cpus)
        # Handle signal information
        self.set_signals()
        # Create a queue for sharing information
        self._queue = Queue()
        self._processes = []
        for o in self._objects:
            self._processes.append(Process(target=o.callback, args=(self._state, self._queue)))

    def init_state(self):
        """
            Initialize the shared memory state for the full rack.
            The global properties are shared by a multiprocessing manager.
        """
        # Use a multi-processing Manager
        self._manager = Manager()
        self._state = self._manager.dict()
        self._state['global'] = self._manager.dict()

        self._state['cv'] = self._manager.list([0.0] * self._number_input)
        self._state['cv_active'] = self._manager.list([0] * self._number_input)
        self._state['buffer'] = self._manager.list([self._manager.list([1.0] * config["audio"]["samples"])
                                                    for _ in range(self._number_input)])
        # Screen-related parameters (dict)
        self._state['screen'] = self._manager.dict()
        self._state['screen']['mode'] = self._manager.Value(int, 0)
        self._state['screen']['event'] = self._manager.Value(int, 0)
        # Audio-related parameters (dict)
        self._state['audio'] = self._manager.dict()
        self._state['audio']['mode'] = self._manager.Value(int, 0)
        self._state['audio']['event'] = self._manager.Value(str, '')

    def set_signals(self):
        """
            Set the complete signaling mechanism.
        """
        self._signal_audio = self._audio._signal
        self._signal_rotary = self._rotary._signal
        self._signal_cvs = self._cvs._signal
        self._signal_screen = self._screen._signal
        self._signal_button = self._button._signal
        signal_set = {
            'audio': self._signal_audio,
            'rotary': self._signal_rotary,
            'cvs': self._signal_cvs,
            'screen': self._signal_screen,
            'button': self._signal_button}
        self._screen._signals = signal_set

    def callback_cv(self, type_input, input_id):
        """
            Callback for handling events from the inputs
        """
        if type_input == "gate":
            if input_id == 0:
                self._state['audio']['event'] = config.events.gate0
                self._signal_audio.set()
            elif input_id == 1:
                self._state['audio']['event'] = config.events.gate1
                self._signal_audio.set()
            elif input_id == 2:
                self._state['audio']['event'] = config.events.gate2
                self._signal_audio.set()
            elif input_id == 3:
                self._state['audio']['event'] = config.events.gate3
                self._signal_audio.set()
            elif input_id == 4:
                self._state['audio']['event'] = config.events.gate4
                self._signal_audio.set()
            else:
                self._state['audio']['event'] = config.events.gate5
                self._signal_audio.set()

        elif type_input == "cv":
            if input_id == 0:
                self._state['audio']['event'] = config.events.cv0
                self._signal_audio.set()
            elif input_id == 1:
                self._state['audio']['event'] = config.events.cv1
                self._signal_audio.set()
            elif input_id == 2:
                self._state['audio']['event'] = config.events.cv2
                self._signal_audio.set()
            elif input_id == 3:
                self._state['audio']['event'] = config.events.cv3
                self._signal_audio.set()
            elif input_id == 4:
                self._state['audio']['event'] = config.events.cv4
                self._signal_audio.set()
            else:
                self._state['audio']['event'] = config.events.cv5
                self._signal_audio.set()

    def start(self):
        """
            Start all parallel processses
        """
        for p in self._processes:
            p.start()

    def run(self):
        """
            Wait (join) on all parallel processses
        """
        for p in self._processes:
            p.join()

    def __del__(self):
        """
            Destructor - cleans up GPIO resources when the object is destroyed.
        """
        GPIO.cleanup()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Neurorack')
    # Device Information
    parser.add_argument('--device', type=str, default='cuda:0', help='device cuda or cpu')
    # Parse the arguments
    args = parser.parse_args()

    neuro = NeuroRave()
    neuro.start()
    neuro.run()
