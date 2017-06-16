import datetime
import numpy as np
import pandas

import fitparse

import fitanalysis.util


# Set to True to add a column to the DataFrame indicating whether a row would
# have been removed if removal of stopped periods were enabled, but don't
# actually remove it.
DEBUG_EXCISE = False


class Activity(fitparse.FitFile):
  """Represents an activity recorded as a .fit file.

  Construction of an Activity parses the .fit file and detects periods of
  inactivity, as such periods must be removed from the data for heart rate-,
  cadence-, and power-based calculations.
  """

  EVENT_TYPE_START = 'start'
  EVENT_TYPE_STOP = 'stop'

  TIMER_TRIGGER_DETECTED = 'detected'

  # Speeds less than or equal to this value (in m/s) are
  # considered to be stopped
  STOPPED_THRESHOLD = 0.3

  def __init__(self, file_obj, remove_stopped_periods=True):
    """Creates an Activity from a .fit file.

    Args:
      file_obj: A file-like object representing a .fit file.
      remove_stopped_periods: If True, regions of data with speed below a
                              threshold will be removed from the data. Default
                              is True.
    """
    super(Activity, self).__init__(file_obj)

    self._remove_stopped_periods = remove_stopped_periods or DEBUG_EXCISE

    self.records = list(self.get_messages('record'))

    # Get elapsed time before modifying the data
    self.start_time = self.records[0].get('timestamp').value
    self.end_time = self.records[-1].get('timestamp').value
    self.elapsed_time = self.end_time - self.start_time

    # Calculated when needed and memoized here
    self._moving_time = None
    self._norm_power = None

    self.events = self._df_from_messages(
        self.get_messages('event'),
        ['event', 'event_type', 'event_group', 'timer_trigger', 'data'],
        timestamp_index=True)

    # We will build a DataFrame with these fields as columns. Values for each
    # of these fields will be extracted from each record from the .fit file.
    fields = ['timestamp', 'speed', 'heart_rate', 'power', 'cadence']

    # The primary index of the DataFrame is the "block". A block is defined as
    # a period of movement. Blocks may be defined by start/stop event messages
    # from the .fit file, or they may be detected based on speed in the case
    # that the recording device did not automatically pause recording when
    # stopped.
    blocks = []
    curr_block = -1

    # The secondary index is the duration from the start of the activity
    time_offsets = []

    # Get start/stop events from .fit file and combine with the events detected
    # from speed data, keeping the event from the .fit file if timestamps are
    # identical
    timer_events = self.events[self.events['event'] == 'timer']

    if self._remove_stopped_periods:
      # Detect start/stop events based on stopped threshold speed. If the
      # recording device did not have autopause enabled then this is the only
      # way periods of no movement can be detected and removed.
      detected_events = self._detect_start_stop_events(self.records)
      timer_events = timer_events.combine_first(detected_events)

    # Build the rows and indices of the DataFrame
    excise = False
    event_index = 0
    rows = []
    for record in self.records:
      curr_timestamp = record.get('timestamp').value

      # Match data record timestamps with event timestamps in order to mark
      # "blocks" as described above. Periods of no movement will be excised
      # (if the recording device did not have autopause enabled there will be
      # blocks of no movement that should be removed before data analysis).
      if event_index < len(timer_events) and (
          curr_timestamp >= timer_events.iloc[event_index].name):

        # Events usually have timestamps that correspond to a data timestamp,
        # but this isn't always the case. Process events until the events catch
        # up with the data.
        while True:
          event_type = timer_events.iloc[event_index]['event_type']
          trigger = timer_events.iloc[event_index]['timer_trigger']

          if event_type == self.EVENT_TYPE_START:
            curr_block += 1

            # If we've seen a start event we should not be excising data
            # TODO(mtraver) Do I care if the start event is detected or from
            # the .fit file? I don't think so.
            excise = False
          elif event_type.startswith(self.EVENT_TYPE_STOP):
            # If the stop event was detected based on speed, excise the region
            # until the next start event, because we know that it's a region of
            # data with speed under the stopped threshold.
            if trigger == self.TIMER_TRIGGER_DETECTED:
              excise = True

          event_index += 1

          # Once the event timestamp is ahead of the data timestamp we can
          # continue processing data; the next event will be processed as the
          # data timestamps catch up with it.
          if event_index >= len(timer_events) or (
              curr_timestamp < timer_events.iloc[event_index].name):
            break

      if not excise or DEBUG_EXCISE:
        # Build indices
        time_offsets.append(curr_timestamp - self.start_time)
        blocks.append(curr_block)

        row = []
        for field_name in fields:
          field = record.get(field_name)
          row.append(field.value if field is not None else None)

        if DEBUG_EXCISE:
          row.append(excise)

        rows.append(row)

    assert len(blocks) == len(time_offsets)

    if DEBUG_EXCISE:
      fields += ['excise']

    self.data = pandas.DataFrame(rows, columns=fields,
                                 index=[blocks, time_offsets])
    self.data.index.names = ['block', 'offset']

    self._clean_up_power_and_cadence()

  def _df_from_messages(self, messages, fields, timestamp_index=False):
    """Creates a DataFrame from an iterable of fitparse messages.

    Args:
      messages: Iterable of fitparse messages.
      fields: List of message fields to include in the DataFrame. Each one will
              be a separate column, and if a field isn't present in a particular
              message, its value will be set to None.
      timestamp_index: If True, message timestamps will be used as the index of
                       the DataFrame. Otherwise the default index is used.
                       Default is False.

    Returns:
      A DataFrame with one row per message and columns for each of
      the given fields.
    """
    rows = []
    timestamps = []
    for m in messages:
      timestamps.append(m.get('timestamp').value)

      row = []
      for field_name in fields:
        field = m.get(field_name)
        row.append(field.value if field is not None else None)

      rows.append(row)

    if timestamp_index:
      return pandas.DataFrame(rows, columns=fields, index=timestamps)
    else:
      return pandas.DataFrame(rows, columns=fields)

  def _detect_start_stop_events(self, records):
    """Detect periods of inactivity by comparing speed to a threshold value.

    Args:
      records: Iterable of fitparse messages. They must contain a 'speed' field.

    Returns:
      A DataFrame indexed by timestamp with these columns:
        - 'event_type': value is one of {'start','stop'}
        - 'timer_trigger': always the string 'detected', so that these
          start/stop events can be distinguished from those present in the
          .fit file.

      Each row is one event, and its timestamp is guaranteed to be that of a
      record in the given iterable of messages.

      When the speed of a record drops below the threshold speed a 'stop' event
      is created with its timestamp, and when the speed rises above the
      threshold speed a 'start' event is created with its timestamp.
    """
    stopped = False
    timestamps = []
    events = []
    for i, record in enumerate(records):
      ts = record.get('timestamp').value

      if i == 0:
        timestamps.append(ts)
        events.append([self.EVENT_TYPE_START, self.TIMER_TRIGGER_DETECTED])
      elif record.get('speed') is not None:
        speed = record.get('speed').value
        if speed <= self.STOPPED_THRESHOLD:
          if not stopped:
            timestamps.append(ts)
            events.append([self.EVENT_TYPE_STOP, self.TIMER_TRIGGER_DETECTED])

          stopped = True
        else:
          if stopped:
            timestamps.append(ts)
            events.append([self.EVENT_TYPE_START, self.TIMER_TRIGGER_DETECTED])
            stopped = False

    return pandas.DataFrame(events, columns=['event_type', 'timer_trigger'],
                            index=timestamps)

  def _clean_up_power_and_cadence(self):
    """Infers true of NaN power and cadence values in simple cases."""
    # If cadence in NaN and power is 0, assume cadence is 0
    self.data.loc[self.data['cadence'].isnull()
                  & (self.data['power'] == 0.0), 'cadence'] = 0.0

    # If power in NaN and cadence is 0, assume power is 0
    self.data.loc[self.data['power'].isnull()
                  & (self.data['cadence'] == 0.0), 'power'] = 0.0

    # If both power and cadence are NaN, assume they're both 0
    power_and_cadence_null = (
        self.data['cadence'].isnull() & self.data['power'].isnull())
    self.data.loc[power_and_cadence_null, 'power'] = 0.0
    self.data.loc[power_and_cadence_null, 'cadence'] = 0.0

  @property
  def moving_time(self):
    if self._moving_time is None:
      moving_time = 0
      for _, block_df in self.data.groupby(level='block'):
        # Calculate the number of seconds elapsed since the previous data point
        # and sum them to get the moving time
        moving_time += (
            (block_df['timestamp'] - block_df['timestamp'].shift(1).fillna(
                block_df.iloc[0]['timestamp'])) / np.timedelta64(1, 's')).sum()

      self._moving_time = datetime.timedelta(seconds=moving_time)

    return self._moving_time

  @property
  def cadence(self):
    if self._remove_stopped_periods:
      return self.data[
          self.data['cadence'].notnull() & (self.data['cadence'] > 0)
          & (self.data['speed'] > self.STOPPED_THRESHOLD)]['cadence']

    return self.data[
        self.data['cadence'].notnull() & (self.data['cadence'] > 0)]['cadence']

  @property
  def mean_cadence(self):
    return self.cadence.mean()

  @property
  def heart_rate(self):
    if self._remove_stopped_periods:
      return self.data[
          self.data['heart_rate'].notnull()
          & self.data['speed'] > self.STOPPED_THRESHOLD]['heart_rate']

    return self.data[self.data['heart_rate'].notnull()]['heart_rate']

  @property
  def mean_heart_rate(self):
    return self.heart_rate.mean()

  @property
  def power(self):
    if self._remove_stopped_periods:
      return self.data[self.data['power'].notnull()
                       & self.data['speed'] > self.STOPPED_THRESHOLD]['power']

    return self.data[self.data['power'].notnull()]['power']

  @property
  def mean_power(self):
    return self.power.mean()

  @property
  def norm_power(self):
    """Calculates the normalized power.

    See (Coggan, 2003) cited in README for details on the rationale behind the
    calculation.

    Normalized power is based on a 30-second moving average of power. Coggan's
    algorithm specifies that the moving average should start at the 30 second
    point in the data, but this implementation does not (it starts with the
    first value, like a standard moving average). This is an acceptable
    approximation because normalized power shouldn't be relied upon for efforts
    less than 20 minutes long (Coggan, 2012), so how the first 30 seconds are
    handled doesn't make much difference. Also, the values computed by this
    implementation are very similar to those computed by TrainingPeaks, so
    changing the moving average implementation doesn't seem to be critical.

    This function also does not specially handle gaps in the data. When a pause
    is present in the data (either from autopause on the recording device or
    removal of stopped periods in post-processing) the timestamp may jump by a
    large amount from one sample to the next. Ideally this should be handled in
    some way that takes into account the physiological impact of that rest, but
    currently this algorithm does not. But again, the values computed by this
    implementation are very similar to those computed by TrainingPeaks, so
    changing gap handling doesn't seem to be critical.

    Returns:
      Normalized power as a float
    """
    if self._norm_power is None:
      p = self.power
      p.index = p.index.droplevel(level='block')
      self._norm_power = (
          np.sqrt(np.sqrt(
              np.mean(fitanalysis.util.moving_average(p, 30) ** 4))))

    return self._norm_power

  def intensity(self, ftp):
    """Calculates the intensity factor of the activity.

    Intensity factor is defined as the ratio of normalized power to FTP.
    See (Coggan, 2016) cited in README for more details.

    Args:
      ftp: Functional threshold power in Watts.

    Returns:
      Intensity factor as a float
    """
    return self.norm_power / float(ftp)

  def training_stress(self, ftp):
    """Calculates the training stress of the activity.

    This is essentially a power-based version of Banister's heart rate-based
    TRIMP (training impulse). See (Coggan, 2003) cited in README for details.
    The formula in that post specifies that average power should be used in
    the calculation, but normalized power is used here instead because it
    yields values in line with the numbers from TrainingPeaks; using average
    power does not.

    Args:
      ftp: Functional threshold power in Watts.

    Returns:
      Training stress as a float
    """
    return (self.moving_time.total_seconds() * self.norm_power
            * self.intensity(ftp)) / (float(ftp) * 3600.0) * 100.0
