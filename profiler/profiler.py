from statistics import mean
from time import time


class Profile(object):
    """
    Decorator that keeps track of the number of times a function is called and
    their execution times.
    """

    __instances = {}

    def __init__(self, func):
        self.__func = func
        self.__number_of_samples = 0
        self.__times = []
        Profile.__instances[func] = self

    def __call__(self, *args, **kwargs):
        """
        Calculate the difference between the start and end time of a function's
        execution
        """
        start = time()
        result = self.__func(*args, **kwargs)
        end = time()
        self.__number_of_samples += 1
        self.__times.append(end-start)
        return result

    @staticmethod
    def str(value):
        return ('\nFunction: {function}\n'
                'NumSamples: {number_of_samples}\n'
                'Min: {min}\n'
                'Max: {max}\n'
                'Average: {average}'.format(**value))

    @staticmethod
    def individual_function(func):
        """
        Calculate and return the number of samples, and the min, max & average
        execution times
        """
        instances = Profile.__instances[func]
        times = instances.__times if len(instances.__times) else [0]
        return {'function': func.__name__,
                'number_of_samples': instances.__number_of_samples,
                'min': '{:.8f}'.format(min(times)),
                'max': '{:.8f}'.format(max(times)),
                'average': '{:.8f}'.format(mean(times))}

    @staticmethod
    def all_functions():
        """ Return statistics for all functions"""
        return dict([(func, Profile.individual_function(func))
                     for func in Profile.__instances])
