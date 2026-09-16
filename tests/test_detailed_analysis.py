import numpy as np
import pandas as pd
import pytest
from src.detailed_analysis import point_deviation, evaluate_conditions, follow_up_estimate


def test_missing_measurement_does_not_become_zero_or_change_denominator():
    data=pd.DataFrame({'condition_id':[1,1,2,2], 'point':[1,2,1,2], 'thickness':[100.,120.,200.,np.nan]})
    result=point_deviation(data).set_index('point')
    assert result.loc[1,'mean_absolute_deviation']==5
    assert result.loc[2,'mean_absolute_deviation']==10
    assert result.loc[2,'valid_wafer_count']==1


def test_uniformity_does_not_prove_all_points_are_inside_spec():
    d=pd.DataFrame({'average_thickness':[3500], 'min_thickness':[3150], 'max_thickness':[3700], 'range':[550], 'time_sec':[55]})
    r=evaluate_conditions(d,3500,300).iloc[0]
    assert r.uniformity_pct < 300/3500*100
    assert not r.observed_points_within_spec


def test_historical_estimate_reproduces_excel():
    r=follow_up_estimate()
    assert r['calculated_temperature_c']==pytest.approx(234.7156078)
    assert r['calculated_time_sec']==pytest.approx(55.29569279)
    assert r['predicted_average_a']==pytest.approx(3481.197448)
