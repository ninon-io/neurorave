import multiprocess as mp
from multiprocess import Process, Queue


class Input:
    '''
        The Input class defines basic functions for input.
    '''

    def __init__(self):
        '''
            Constructor - Creates a new instance of the Input class.
        '''

    def callback(self, state, queue):
        '''
            Function for starting the input.
            Here it will be a sequential (blocking) input
            Parameters:
                state:      [Manager]
                            Shared memory through a Multiprocessing manager
                queue:      [Queue]
                            Shared memory queue through a Multiprocessing queue
        '''


class ThreadInput(Input):
    '''
        The ThreadInput class defines threaded versions of the inputs.
    '''

    def __init__(self):
        '''
            Constructor - Creates a new instance of the ThreadInput class.
        '''
        super().__init__()

    def callback(self, state, queue):
        '''
            Function for starting the input.
            Here it will be a threaded input
            Parameters:
                state:      [Manager]
                            Shared memory through a Multiprocessing manager
                queue:      [Queue]
                            Shared memory queue through a Multiprocessing queue
        '''
        super().callback(state, queue)
        print(mp.current_process())


class ProcessInput(Input):

    def __init__(self):
        '''
            Constructor - Creates a new instance of the ProcessInput class.
        '''
        super().__init__()

    def callback(self, state, queue):
        '''
            Function for starting the input.
            Here it will be an independent process input
            Parameters:
                state:      [Manager]
                            Shared memory through a Multiprocessing manager
                queue:      [Queue]
                            Shared memory queue through a Multiprocessing queue
        '''
        super().callback(state, queue)
        print(mp.current_process())


# class InterruptInput(Input):
#
#     def __init__(self,
#                  name: str):
#         '''
#             Constructor - Creates a new instance of the InterruptInput class.
#             Parameters:
#                 name:       [str]
#                             Name of the input
#         '''
#         super().__init__(name)