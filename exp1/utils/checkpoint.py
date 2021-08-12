import multiprocessing as mp
import os
import pickle
import functools

lock: mp.Lock = None


def set_checkpoint_lock(l: mp.Lock):
    """
    When we are using the checkpoint functions in the processing pools, we
    need to have a resource lock on the checkpoint.pickle file.
    This is called to initialize the process with the RLock
    :param l:
    :return:
    """
    global lock
    lock = l


def init_checkpoints():
    if not os.path.exists('checkpoint.pickle'):
        pickle.dump(set(), open('checkpoint.pickle', 'wb'))


def set_checkpoint(name):
    if lock is not None:
        lock.acquire()
    _checkpoint: set = pickle.load(open('checkpoint.pickle', 'rb'))
    _checkpoint.add(name)
    pickle.dump(_checkpoint, open('checkpoint.pickle', 'wb'))
    print(f'reached checkpoint {name}')
    if lock is not None:
        lock.release()


def get_checkpoint(name):
    if lock is not None:
        lock.acquire()
    contains = name in pickle.load(open('checkpoint.pickle', 'rb'))
    if lock is not None:
        lock.release()
    return contains


def checkpoint(checkpoint_name: str):
    def _decorator(func):
        @functools.wraps(func)
        def _wrapper(state=None):
            if get_checkpoint(checkpoint_name):
                return

            res = func(state)

            set_checkpoint(checkpoint_name)

            return res
        return _wrapper
    return _decorator