"""Utility functions."""
import numpy as np


def moving_average(time_series, window_len):
  """Calculates the moving average of an unevenly spaced time series.

  This moving average implementation weights each value by the time it remained
  unchanged, which conceptually matches smart recording on GPS devices: a sample
  is taken when some value changes sufficiently, so before a new sample is taken
  the previous one is assumed to be more or less constant.

  The term "area" below means a sum of time-weighted values.

  This implementation follows the SMA_last algorithm proposed in
  http://eckner.com/papers/Algorithms%20for%20Unevenly%20Spaced%20Time%20Series.pdf

  Args:
    time_series: A pandas.Series of the values to average,
                 indexed with timestamps.
    window_len: The size of the moving average window, in seconds.

  Returns:
    A numpy array of length len(time_series) containing the
    moving average values
  """
  # Re-index the time series with duration in seconds from the first value
  time_series.index = (
      (time_series.index
       - time_series.index[0]) / np.timedelta64(1, 's')).astype('int')

  window_area = time_series.iloc[0] * window_len

  # It may not always be possible to construct a window of length exactly equal
  # to window_len using timestamps present in the data. To handle this, the left
  # side of the window is allowed to fall between timestamps (the right side is
  # always fixed to a timestamp in the data). Therefore we need to separately
  # compute the area of the inter-timestamp region on the left side of the
  # window so that it can be added to the window area. left_area is that value.
  left_area = window_area

  out = np.zeros(len(time_series))
  out[0] = time_series.iloc[0]

  # i is the left side of the window and j is the right
  i = 0
  for j in xrange(1, len(time_series)):
    # Remove the last iteration's left_area as a new right window bound may
    # change the left_area required in this iteration
    window_area -= left_area

    # Expand window to the right
    window_area += time_series.iloc[j-1] * (time_series.index[j]
                                            - time_series.index[j-1])

    # Shrink window from the left if expanding to the right has created too
    # large a window. new_left_time may fall between timestamps present in the
    # data, which is fine, since that's handled by left_area.
    new_left_time = time_series.index[j] - window_len
    while time_series.index[i] < new_left_time:
      window_area -= time_series.iloc[i] * (time_series.index[i+1]
                                            - time_series.index[i])
      i += 1

    # Add left side inter-timestamp area to window
    left_area = time_series.iloc[max(0, i - 1)] * (time_series.index[i]
                                                   - new_left_time)
    window_area += left_area

    out[j] = window_area / window_len

  return out


def print_full(df):
  """Prints a DataFrame in full."""
  pandas.set_option('display.max_rows', len(df))
  print df
  pandas.reset_option('display.max_rows')
