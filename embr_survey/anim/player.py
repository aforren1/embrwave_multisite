from inspect import ismethod
from collections import namedtuple
from copy import copy

TrackAttr = namedtuple('TrackAttr', 'track attr obj kwargs')


class Player(object):
    """Manages one or more Tracks, allowing for synchronization of animations.

    Notes
    -----
    Can also be used as a mixin.
    """

    def __init__(self, repeats=1, *args, **kwargs):
        """Create a Player.

        Parameters
        ----------
        repeats: number of times to repeat the animation
        *args: arbitrary (only matters if using as mixin)
        **kwargs: arbitrary (only matters if using as mixin)
        """
        self.tracks = []
        self.state = 'stopped'  # 'playing'
        self.ref_time = 0
        self.duration = 0
        self.timescale = 1
        if repeats < 1:
            raise ValueError('Number of repeats must be > 1 (or math.inf)')
        self._repeats = repeats  # track
        self.repeats = repeats

    def add(self, track, attr, obj=None, **kwargs):
        """Add a new Track to the Player.

        Parameters
        ----------
        track: toon.anim.Track
            A Track object.
        attr: str or function
            The attribute/property to change, or a function that takes (val, obj)
            as positional arguments, where `val` is the interpolated value, and
            `obj` is the object to be manipulated.
        obj: None (if mixin), object or list of objects (otherwise)
            Object that is being manipulated.
        **kwargs: Arbitrary keyword arguments, passed to `attr` if it is a function
        """
        self.tracks.append(TrackAttr(copy(track), attr, obj, kwargs))
        new_dur = track.duration()
        self.duration = new_dur if new_dur > self.duration else self.duration

    def start(self, time):
        """Start the animations.

        Parameters
        ----------
        time: float
            Reference time.
        """
        self.ref_time = time
        self._repeats = self.repeats
        self.state = 'playing'
        self.advance(time)  # start should reset everything to the initial time?

    def stop(self):
        """Stop the animations."""
        self.state = 'stopped'

    def reset(self):
        """Reset all tracks and stop animation."""
        self.start(self.ref_time)
        self.stop()

    def resume(self, time):
        """Resume playing.

        Notes
        -----
        If already playing, do nothing.
        """
        if self.state == 'playing':
            return
        self.start(time)

    def _do_update(self, attr, val, obj, **kwargs):
        # if we get a function, call function with updated val
        if callable(attr):
            # if it's a method (e.g. a setter), we call that method with the val as an arg
            if ismethod(attr):
                if kwargs:
                    attr(val, **kwargs)
                else:
                    attr(val)
                return
            if kwargs:
                attr(val, obj, **kwargs)
            else:
                attr(val, obj)
            return
        # otherwise (user gave string), directly set the attribute
        setattr(obj, attr, val)

    def advance(self, time):
        """Update all Tracks with a new time.

        Parameters
        ----------
        time: float
            Current time. Track time is `time - reference time`.
        """
        if self.state != 'playing':
            return
        if time < self.ref_time:
            return
        for trk in self.tracks:
            # if tracks are playing, will return a val
            val = trk.track.at((time - self.ref_time) * self.timescale)
            if trk.obj is not None:  # object or list provided, so we'll manipulate them
                try:  # see if single object
                    self._do_update(trk.attr, val,
                                    trk.obj, **trk.kwargs)
                except (TypeError, AttributeError):  # list of objects?
                    for obj in trk.obj:
                        self._do_update(trk.attr, val,
                                        obj, **trk.kwargs)
            else:  # operate on self
                self._do_update(trk.attr, val, self, **trk.kwargs)
            # if we've gone beyond, stop playing
            if time - self.ref_time >= self.duration:
                self._repeats -= 1
                if self._repeats < 1:
                    self.state = 'stopped'
                else:
                    self.ref_time = time

    @property
    def is_playing(self):
        return self.state == 'playing'

    @property
    def is_stopped(self):
        return self.state == 'stopped'

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, val):
        self._state = val

    @property
    def timescale(self):
        return self._timescale

    @timescale.setter
    def timescale(self, value):
        """Scales the animations.

        Parameters
        ----------
        value: float
            Value on the interval (0, Inf], where < 1 slows down the animation,
            and > 1 speeds up the animation.

        Notes
        -----
        Defaults to 1 (normal playback speed).
        """
        self._timescale = value
