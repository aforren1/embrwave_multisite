
# clock_fun should be time.perf_counter, time.monotonic,
# timeit.default_timer (for best compatibility)

# start should be attached to win.callOnFlip()
# next_frame should be attached to win.callOnFlip()
from timeit import default_timer


class Timeline(object):
    """Keeps track of the amount of time between frames."""

    def __init__(self, clock_fun=default_timer):
        """Create the Timeline object.

        Parameters
        ----------
        clock_fun: function or method
            Used to get the current time. Defaults to timeit.default_timer,
            which picks the highest-resolution timer available given the platform
            and version of python.
        """
        self.clock_fun = clock_fun
        self.running = False

    def start(self):
        """Start taking the time."""
        self.running = True
        self.start_time = self.clock_fun()
        self.prev_frame_time = self.start_time
        self.prev_frame_dur = 0

    def stop(self):
        """Stop taking the time."""
        self.running = False
        self.start_time = self.clock_fun()
        self.prev_frame_time = self.start_time
        self.prev_frame_dur = 0

    def next_frame(self):
        """Record the time of the frame.

        If using psychopy, use with callOnFlip (so it's called immediately
        after the flip is done).
        """
        # should be run by win.callOnFlip
        now = self.clock_fun()
        if not self.running:
            return
        self.prev_frame_dur = now - self.prev_frame_time
        self.prev_frame_time = now

    @property
    def frame_time(self):
        """Time relative to the start time."""
        return self.prev_frame_time - self.start_time

    @property
    def delta_time(self):
        """Time between last two frames."""
        return self.prev_frame_dur
