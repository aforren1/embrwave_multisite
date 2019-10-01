from collections import namedtuple
from embr_survey.anim.easing import linear
from embr_survey.anim.interpolators import lerp, select


class Track(object):
    """Storage for (keyframe, value) pairs.

    Also handles interpolation and easing between keyframes.
    """

    def __init__(self, data, interpolator=lerp, easing=linear):
        """Creates a Track.

        Parameters
        ----------
        data: list of (keyframe, value) pairs
        interpolator: function
            `lerp` for linear interpolation, `select` for stepwise behavior.
        easing: function
            Rate of change of the value over time. See toon.anim.easing, or
            specificy a custom function that takes a single parameter, and
            returns a value on the interval [0, 1].
        """
        # data is list of tuples
        self.data = data
        self.interpolator = interpolator
        self.easing = easing
        # if data is non-numeric, force user to use select
        if not isinstance(data[0][1], (float, int)):
            self.interpolator = select
            self.easing = linear

    def at(self, time):
        """Get the interpolated value of a track at a given time.

        Parameters
        ----------
        time: float
            Time of interest.

        Returns
        -------
        The interpolated value at the given point in time.
        """
        # find the two keyframes to interpolate between
        # rel_time is the time relative to the start
        if time < self.data[0][0]:
            # TODO: extrapolation (currently equivalent to constant)
            return self.data[0][1]
        try:
            index, goal = next((i, x) for i, x in enumerate(self.data) if x[0] > time)
        except StopIteration:
            # TODO: Extrapolation (currently equivalent to constant)
            return self.data[-1][1]
        # prev keyframe to check against
        reference = self.data[index - 1]
        # calculate time stuff
        goal_time = goal[0] - reference[0]
        new_time = time - reference[0]
        time_warp = self.easing(1 - ((goal_time - new_time)/goal_time))
        return self.interpolator(reference[1], goal[1], time_warp)

    def duration(self):
        """The maximum duration of the track."""
        # last time in keyframes
        return self.data[-1][0]
