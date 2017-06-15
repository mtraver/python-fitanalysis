# fitanalysis
fitanalysis is a Python library for analysis of ANT/Garmin `.fit` files.

It's geared toward cycling and allows for easy extraction of data such as the
following from a `.fit` file:
- elapsed time
- moving time
- average heart rate
- average power
- normalized power (based on information publicly available about
  TrainingPeaks' NP®)
- intensity (based on information publicly available about TrainingPeaks' IF®)
- training stress (based on information publicly available about
  TrainingPeaks' TSS®)

My impetus for this project was to better understand how platforms like
TrainingPeaks analyze power and heart rate data to arrive at an estimation
of training stress. As such, this project attempts to match those platforms'
calculations as closely as possible.

# Dependencies and installation
[Pandas](http://pandas.pydata.org/), [NumPy](http://www.numpy.org/), and
[fitparse](https://github.com/dtcooper/python-fitparse) are required.

`python setup.py install` (or `python setup.py install --user`) to install.

# Example

fitanalysis provides the `Activity` class.

```python
import fitanalysis

activity = fitanalysis.Activity('my_activity.fit')

print activity.elapsed_time
print activity.moving_time

# Also available for heart rate and cadence
print activity.mean_power

print activity.norm_power

# Intensity and training stress calculations require
# a functional threshold power value (in Watts)
print activity.intensity(310)
print activity.training_stress(310)
```

Construction of an `Activity` parses the `.fit` file and detects periods of
inactivity, as such periods must be removed from the data for heart rate-,
cadence-, and power-based calculations.

# Comparison of activity analysis platforms

Here is a comparison for a few of my rides of varying profiles across the
various platforms.

<table>
  <tr>
    <th></th>
    <th></th>
    <th>fitanalysis</th>
    <th>TrainingPeaks</th>
    <th>Garmin Connect</th>
    <th>Strava</th>
  </tr>

  <tr>
    <th rowspan="7">Ride 1: epic ride<br>126.5 mi<br>15207 ft climbing</th>
  </tr>
  <tr>
    <th>Elapsed time</th>
    <td>12:19:40</td>
    <td>*</td>
    <td>12:19:20</td>
    <td>12:19:40</td>
  </tr>
  <tr>
    <th>Moving time</th>
    <td>9:07:14</td>
    <td>-</td>
    <td>9:06:12</td>
    <td>9:09:26</td>
  </tr>
  <tr>
    <th>Mean power</th>
    <td>182 W</td>
    <td>183 W</td>
    <td>183 W</td>
    <td>183 W</td>
  </tr>
  <tr>
    <th>Norm. power</th>
    <td>232 W</td>
    <td>232 W</td>
    <td>232 W</td>
    <td>-</td>
  </tr>
  <tr>
    <th>Intensity</th>
    <td>0.74</td>
    <td>0.74</td>
    <td>0.74</td>
    <td>-</td>
  </tr>
  <tr>
    <th>Training stress</th>
    <td>504.0</td>
    <td>505.1</td>
    <td>503.2</td>
    <td>-</td>
  </tr>

  <tr>
    <th rowspan="7">Ride 2: interval workout<br>11.9 mi<br>1352 ft climbing</th>
  </tr>
  <tr>
    <th>Elapsed time</th>
    <td>1:32:34</td>
    <td>*</td>
    <td>1:32:34</td>
    <td>1:32:34</td>
  </tr>
  <tr>
    <th>Moving time</th>
    <td>57:17</td>
    <td>-</td>
    <td>57:11</td>
    <td>57:51</td>
  </tr>
  <tr>
    <th>Mean power</th>
    <td>172 W</td>
    <td>168 W</td>
    <td>168 W</td>
    <td>172 W</td>
  </tr>
  <tr>
    <th>Norm. power</th>
    <td>289 W</td>
    <td>286 W</td>
    <td>287 W</td>
    <td>-</td>
  </tr>
  <tr>
    <th>Intensity</th>
    <td>0.93</td>
    <td>0.92</td>
    <td>0.92</td>
    <td>-</td>
  </tr>
  <tr>
    <th>Training stress</th>
    <td>81.7</td>
    <td>82.3</td>
    <td>83.1</td>
    <td>-</td>
  </tr>

  <tr>
    <th rowspan="7">Ride 3: tempo<br>25.4 mi<br>2451 ft climbing</th>
  </tr>
  <tr>
    <th>Elapsed time</th>
    <td>2:09:02</td>
    <td>2:08:58</td>
    <td>2:08:58</td>
    <td>2:09:02</td>
  </tr>
  <tr>
    <th>Moving time</th>
    <td>1:32:39</td>
    <td>-</td>
    <td>1:32:23</td>
    <td>1:32:43</td>
  </tr>
  <tr>
    <th>Mean power</th>
    <td>201 W</td>
    <td>201 W</td>
    <td>201 W</td>
    <td>202 W</td>
  </tr>
  <tr>
    <th>Norm. power</th>
    <td>270 W</td>
    <td>269 W</td>
    <td>270 W</td>
    <td>-</td>
  </tr>
  <tr>
    <th>Intensity</th>
    <td>0.86</td>
    <td>0.86</td>
    <td>0.87</td>
    <td>-</td>
  </tr>
  <tr>
    <th>Training stress</th>
    <td>115.3</td>
    <td>114.1</td>
    <td>115.1</td>
    <td>-</td>
  </tr>

  <tr>
    <th rowspan="7">Ride 4: "coffee pace"<br>13.4 mi<br>902 ft climbing</th>
  </tr>
  <tr>
    <th>Elapsed time</th>
    <td>1:41:24</td>
    <td>1:41:23</td>
    <td>1:41:23</td>
    <td>1:41:24</td>
  </tr>
  <tr>
    <th>Moving time</th>
    <td>57:15</td>
    <td>-</td>
    <td>57:02</td>
    <td>57:23</td>
  </tr>
  <tr>
    <th>Mean power</th>
    <td>138 W</td>
    <td>139 W</td>
    <td>139 W</td>
    <td>139 W</td>
  </tr>
  <tr>
    <th>Norm. power</th>
    <td>251 W</td>
    <td>252 W</td>
    <td>252 W</td>
    <td>-</td>
  </tr>
  <tr>
    <th>Intensity</th>
    <td>0.80</td>
    <td>0.81</td>
    <td>0.81</td>
    <td>-</td>
  </tr>
  <tr>
    <th>Training stress</th>
    <td>61.6</td>
    <td>61.6</td>
    <td>61.2</td>
    <td>-</td>
  </tr>
</table>

\- Data not available on this platform

\* Didn't calculate. TrainingPeaks doesn't directly report elapsed time so it
   has to be manually summed from lap durations, and these rides have lots of
   laps.

## Conclusions

- Garmin Connect is the most aggressive when calculating moving time, Strava is
  the most lenient, and fitanalysis falls in between.
- Mean power calculated by fitanalysis is at most 1 W different than mean power
  calculated by another platform.
- Normalized power calculated by fitanalysis is at most 2 W different than
  normalized power calculated by another platform.
- Training stress calculated by fitanalysis corresponds well to other platforms
  across a large range.

## Autopause and inactivity handling

All of the activities in the table above were recorded with autopause enabled,
so they don't highlight any differences in how each platform handles long
periods of inactivity. To test this I recorded a ride with autopause disabled,
and then used fitanalysis to analyze it in two ways: detecting and removing
periods of inactivity (the default for fitanalysis), and leaving the data as-is.
This activity includes a 2-minute period of inactivity, in addition to shorter
stops e.g. at stop lights.

<table>
  <tr>
    <th></th>
    <th>fitanalysis<br>(inactivity removed)</th>
    <th>fitanalysis<br>(inactivity not removed)</th>
    <th>TrainingPeaks</th>
    <th>Garmin Connect</th>
    <th>Strava</th>
  </tr>

  <tr>
    <th>Elapsed time</th>
    <td>34:54</td>
    <td>34:54</td>
    <td>34:54</td>
    <td>34:54</td>
    <td>34:54</td>
  </tr>
  <tr>
    <th>Moving time</th>
    <td>30:48</td>
    <td>34:54</td>
    <td>-</td>
    <td><b>30:57</b></td>
    <td>31:12</td>
  </tr>
  <tr>
    <th>Mean power</th>
    <td><b>247 W</b></td>
    <td>219 W</td>
    <td>220 W</td>
    <td>220 W</td>
    <td><b>248 W</b></td>
  </tr>
  <tr>
    <th>Norm. power</th>
    <td><b>279 W</b></td>
    <td>271 W</td>
    <td>272 W</td>
    <td>272 W</td>
    <td>-</td>
  </tr>
  <tr>
    <th>Intensity</th>
    <td>0.89</td>
    <td>0.87</td>
    <td>0.87</td>
    <td>0.87</td>
    <td>-</td>
  </tr>
  <tr>
    <th>Training stress</th>
    <td><b>41.1</b></td>
    <td>43.8</td>
    <td>43.6</td>
    <td>43.7</td>
    <td>-</td>
  </tr>
</table>

Average power with periods of inactivity removed matches Strava's average power,
but not TrainingPeaks or Garmin Connect. They calculate average power from the
raw data.

TrainingPeaks and Garmin Connect also calculate normalized power from the
raw data.

Garmin Connect does calculate moving time but it appears not to use it for the
power calculations. If inactivity isn't removed from the power data then
elapsed time should indeed be used for consistency, but the choice to remove
the inactivity for the purpose of moving time calculation and not do so for
power is puzzling.

Because Strava removes inactivity for power calculations, both approaches seem
to be accepted. It's my opinion that removing inactivity is the correct
approach because, depending on the length of inactivity, not doing so can lead
to an inflated or deflated estimation of the effort during periods of activity.
One counter-argument I can see is for structured workouts: it may be desirable
to include the rest periods in calculations of intensity and training stress
because in this case the length of the rest is deliberately chosen as part of
the workout. Perhaps this is the reason for TrainingPeaks' implementation?

This is only one data point, so looking at some more rides would be interesting,
but one takeaway from this example is this: want to inflate your TSS? Try
disabling autopause (and don't take _really_ long breaks, but apparently
moderately long breaks are fine).

# References

Coggan, Andrew. (2012, June 20). _Calculate Normalised Power for an Interval._ [Forum comment]. Retrieved June 14, 2017, from http://www.timetriallingforum.co.uk/index.php?/topic/69738-calculate-normalised-power-for-an-interval/&do=findComment&comment=978386

Coggan, Andrew. (2016, February 10). _Normalized Power, Intensity Factor and Training Stress Score._ Retrieved June 14, 2017, from
https://www.trainingpeaks.com/blog/normalized-power-intensity-factor-training-stress/

Coggan, Andrew. (2003, March 13). _TSS and IF - at last!_ Retrieved June 14, 2017, from http://lists.topica.com/lists/wattage/read/message.html?mid=907028398&sort=d&start=9353

Eckner, Andreas. (2017, April 3). _Algorithms for Unevenly Spaced Time Series: Moving Averages and Other Rolling Operators._ Retrieved June 14, 2017, from http://eckner.com/papers/Algorithms%20for%20Unevenly%20Spaced%20Time%20Series.pdf

# License
This project is licensed under the MIT License. See
[LICENSE](https://github.com/mtraver/fitanalysis/blob/master/LICENSE) file
for details.
