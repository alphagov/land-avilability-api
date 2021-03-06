import pandas as pd
import numpy as np

log = __import__('logging').getLogger(__file__)


def school_site_size_range(**kwargs):
    '''Returns the floor space (m^2), as a range, for a school with the
    given characteristics.
    '''
    # size_req on ola
    size = school_site_size(**kwargs)
    # upper_site_req, lower_site_req on ola
    size_range = (size * 0.95, size * 1.5)
    return size_range

def school_site_size(num_pupils=0,
                     num_pupils_post16=0,
                     school_type='primary_school'):
    '''Return the expected floor space (m^2) for the given parameters.
    NB pupils post-16 should be included both figures 'num_pupils' and
    'num_pupils_post16'.
    '''
    if school_type == 'secondary_school':
        # Deal with sixth form additional space
        if num_pupils_post16 > 0:
            under16 = num_pupils - num_pupils_post16
            return (1050.0 + (6.3 * under16)) + \
                   (350 + (7 * float(num_pupils_post16)))
        else:
            return 1050 + (6.3 * float(num_pupils))
    elif school_type == 'primary_school':
        return 350.0 + (4.1 * float(num_pupils))
    else:  # default to primary_school
        return 350.0 + (4.1 * float(num_pupils))
    return 0


class SchoolRankingConfig(object):
    '''The attributes of the location ranking for building
    schools, that can be plugged into the more general z-values algorithm.

    i.e. the extraction of features from the location and query
    and the 'ideal' values (whether high is better or not)
    '''
    def __init__(self, lower_site_req, upper_site_req, school_type):
        self.lower_site_req = lower_site_req
        self.upper_site_req = upper_site_req
        self.school_type = school_type

        self.ideal_values = dict([
            ('area_suitable', 1),
            ('geoattributes.BROADBAND', 1),
            ('greenbelt overlap', 0),
            ('geoattributes.DISTANCE TO BUS STOP', 0),
            ('geoattributes.DISTANCE TO METRO STATION', 0),
            ('geoattributes.DISTANCE TO MOTORWAY JUNCTION', 1),
            ('geoattributes.DISTANCE TO OVERHEAD LINE', 1),
            ('geoattributes.DISTANCE TO PRIMARY SCHOOL',
                0 if school_type == 'secondary_school' else 1),
            ('geoattributes.DISTANCE TO RAIL STATION', 0),
            ('geoattributes.DISTANCE TO SECONDARY SCHOOL',
                0 if school_type == 'primary_school' else 1),
            ('geoattributes.DISTANCE TO SUBSTATION', 1),
        ])

    def locations_to_dataframe(self, locations):
        '''Converts location objects (as a list or ResultSet) to a DataFrame.
        The fields kept are exactly the attributes needed for the scoring.
        '''
        # TODO
        # Check that distances are correctly either euclidean or network.
        # Network:
        #   'geoattributes.DISTANCE TO BUS STOP_zscore',
        #   'geoattributes.DISTANCE TO METRO STATION_zscore',
        #   'geoattributes.DISTANCE TO PRIMARY SCHOOL_zscore',
        #   'geoattributes.DISTANCE TO RAIL STATION_zscore',
        #   'geoattributes.DISTANCE TO SECONDARY SCHOOL_zscore'
        # Euclidean:
        #   'geoattributes.DISTANCE TO MOTORWAY JUNCTION',
        #   'geoattributes.DISTANCE TO OVERHEAD LINE',
        #   'geoattributes.DISTANCE TO SUBSTATION'

        df = pd.DataFrame([
            {
                'estimated_floor_space': l.estimated_floor_space,
                'geoattributes.BROADBAND': 1.0 if l.nearest_broadband_fast else 0.0,
                'greenbelt overlap': l.greenbelt_overlap,
                'geoattributes.DISTANCE TO BUS STOP': l.nearest_busstop_distance,
                'geoattributes.DISTANCE TO METRO STATION': l.nearest_metrotube_distance,
                'geoattributes.DISTANCE TO MOTORWAY JUNCTION': l.nearest_motorway_distance,
                'geoattributes.DISTANCE TO OVERHEAD LINE': l.nearest_ohl_distance,
                'geoattributes.DISTANCE TO PRIMARY SCHOOL': l.nearest_primary_school_distance,
                'geoattributes.DISTANCE TO RAIL STATION': l.nearest_trainstop_distance,
                'geoattributes.DISTANCE TO SECONDARY SCHOOL': l.nearest_secondary_school_distance,
                'geoattributes.DISTANCE TO SUBSTATION': l.nearest_substation_distance,
                }
            for l in locations
            ],
            index=[l.id for l in locations])
        df = df.apply(lambda x: pd.to_numeric(x, errors='ignore'))

        return df

    def extract_features(self, df):
        '''Create further features, based on the location data and the query.

        Inserts them into the df (in-place).
        '''
        # work out if the site size is suitable
        df['area_suitable'] = is_area_suitable(
            df['estimated_floor_space'], self.lower_site_req, self.upper_site_req)


def is_area_suitable(area, lower_site_req, upper_site_req):
    return (area > lower_site_req) & \
        (area < upper_site_req)


def score_results_dataframe(results_dataframe, ranking_config):
    '''Given search results (locations) as rows of a dataframe (with columns
    roughly scoring_columns), return another dataframe with those rows and
    a column 'score'. A higher score means a higher suitability for building
    the specified school.
    '''
    df = results_dataframe

    # filter to only the columns that we'll score against
    scoring_columns = ranking_config.ideal_values.keys()
    df2 = pd.concat([df[col] for col in scoring_columns], axis=1)

    # z-score scaling
    # (not really necessary because we scale it again, but useful for
    #  analysis)
    if False:
        z_score_scaling(df2)

    # Rescale minimum = 0 and maximum = 1 for each column
    df3 = rescale_columns_0_to_1(df2)

    flip_columns_so_1_is_always_best(df3, ranking_config)

    # Assume gaps in the data score 0
    # NaN -> 0
    df3 = df3.fillna(0)

    calculate_score(df3)
    return df3


def z_score_scaling(df):
    '''Given inputs as rows of a dataframe, for every given column (apart from
    'area_suitable'), this function scales the values to a z-score and stores
    them in new columns '<column>_zscore'.
    '''
    for col in df.columns:
        if col == 'area_suitable':
            continue
        col_zscore = col + '_zscore'
        # zscore calculation: x = (x - column_mean)/column_stdev
        col_mean_normalized = df[col] - df[col].mean()
        standard_deviation = df[col].std(ddof=0)
        if standard_deviation == 0.0:
            # can't divide by zero
            df[col_zscore] = col_mean_normalized
        else:
            df[col_zscore] = col_mean_normalized / standard_deviation


def rescale_columns_0_to_1(df):
    '''Rescale values in each column so that they are between 0 and 1.'''
    return df.apply(
        lambda x: (x.astype(float) - min(x)) / ((max(x) - min(x)) or 0.1),
        axis=0)


def flip_columns_so_1_is_always_best(df, ranking_config):
    '''Given inputs as rows of a dataframe, scaled 0 to 1, flip value of
    particular columns, so that 1 is always means a positive thing and 0
    negative. Changes the df in-place.'''
    missing_ideal_values = set(df.columns) - set(ranking_config.ideal_values)
    assert not missing_ideal_values
    columns_to_flip = [
        col for col, ideal_value in ranking_config.ideal_values.items()
        if ideal_value == 0]
    for col in columns_to_flip:
        df[col] = df[col].map(lambda x: 1.0 - x)

def calculate_score(df):
    '''Given inputs as rows of a dataframe, that are scaled 0 to 1, this
    function appends a column 'score' for ranking. (Score: bigger=better)
    '''
    df['score'] = np.linalg.norm(df, axis=1)
