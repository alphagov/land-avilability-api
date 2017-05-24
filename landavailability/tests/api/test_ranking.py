from unittest import TestCase
import json
import os.path
from pprint import pprint
from collections import OrderedDict

import pandas as pd
from pandas.util.testing import assert_frame_equal, assert_series_equal

from api import ranking


class TestRanking(TestCase):
    def _test_scoring_with_elastic_search_conversions(self):
        # i.e. we wrap the scoring routing with ola-specific stuff so that
        # we can check the result directly with the the ola result
        class Result(str):
            def to_dict(self):
                return json.loads(self)
        terms = dict(
            build='primary_school',
        )
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'data/ola_sample_results.json'), 'r') as f:
            results = ResultList(
                [Result(json.dumps(hit['_source']))
                 for hit in json.loads(f.read())['hits']['hits']]
                )
        # I ran the scoring on ola roughly like this:
        #   processor = get_processor(terms.get('build', 'primary_school'))
        #   ola_scored_result = processor.rank_results(terms, results)
        ola_scored_result = [
            {'address': None,
             'area_suitable': False,
             'authority': 'Oldham',
             'centre': {'lat': 53.5116476, 'lon': -2.1275541},
             'dist': 7.2111025509,
             'footage': '',
             'geoattributes': {'AREA': 8711.7258599034,
                               'BROADBAND': '67',
                               'COVERAGE BY GREENBELT': 0.0,
                               'DISTANCE TO BUS STOP': 2.06696443,
                               'DISTANCE TO METRO STATION': 1591.414955752,
                               'DISTANCE TO MOTORWAY JUNCTION': 1394.947379297,
                               'DISTANCE TO OVERHEAD LINE': 3371.176664415,
                               'DISTANCE TO PRIMARY SCHOOL': 71.867401834,
                               'DISTANCE TO RAIL STATION': 3117.229318753,
                               'DISTANCE TO SECONDARY SCHOOL': 824.753126148,
                               'DISTANCE TO SUBSTATION': 2981.508831039,
                               'FLOORSPACE': 8711.7258599034},
             'id': 3830,
             'lower_site_req': 332.5,
             'name': 'Lower Lame Road - Land At, Lameside',
             'owner': 'Oldham',
             'postcode': None,
             'region': None,
             'structures': '',
             'upper_site_req': 525.0,
             'uprn': []},
            {'address': None,
             'area_suitable': False,
             'authority': 'Oldham',
             'centre': {'lat': 53.5129299, 'lon': -2.1582243},
             'dist': 7.2111025509,
             'footage': '',
             'geoattributes': {'AREA': 1321.1736732156,
                               'BROADBAND': '100',
                               'COVERAGE BY GREENBELT': 0.0,
                               'DISTANCE TO BUS STOP': 175.924922778,
                               'DISTANCE TO METRO STATION': 386.560575227,
                               'DISTANCE TO MOTORWAY JUNCTION': 1206.127109438,
                               'DISTANCE TO OVERHEAD LINE': 1936.069138069,
                               'DISTANCE TO PRIMARY SCHOOL': 382.742359075,
                               'DISTANCE TO RAIL STATION': 1412.324901656,
                               'DISTANCE TO SECONDARY SCHOOL': 984.728804015,
                               'DISTANCE TO SUBSTATION': 1738.073428322,
                               'FLOORSPACE': 1321.1736732156},
             'id': 3825,
             'lower_site_req': 332.5,
             'name': 'Alfrod St - Land North East Of, (Sorplus), Filesworth',
             'owner': 'Oldham',
             'postcode': None,
             'region': None,
             'structures': '',
             'upper_site_req': 525.0,
             'uprn': []}]

        lower_site_req, upper_site_req = \
            ranking.school_site_size_range_from_terms(terms)
        scored_result = \
            convert_df_to_elastic_results(
                ranking.score_results(
                    convert_elastic_results_to_dicts(results),
                    lower_site_req, upper_site_req,
                    school_type=terms.get('build')),
                terms
                )
        self.assertEqual(ola_scored_result, scored_result)

    def test_scoring(self):
        # we test just the scoring routine. we hacked ola to see what format
        # the data was going in and out of it and see if our version of it
        # does the same thing. but the ola results are not quite right
        terms = dict(
            build='primary_school',
        )
        # Get result_dicts by running:
        # with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        #                        'data/ola_sample_results.json'), 'r') as f:
        #     results = ResultList(
        #         [Result(json.dumps(hit['_source']))
        #          for hit in json.loads(f.read())['hits']['hits']]
        #         )
        # result_dicts = convert_elastic_results_to_dicts(results)
        result_dicts = [
            {'address': None,
             'authority': 'Oldham',
             'centre': {'lat': 53.5116476, 'lon': -2.1275541},
             'footage': '',
             'geoattributes': {'AREA': 8711.72585990344,
                               'BROADBAND': '67',
                               'COVERAGE BY GREENBELT': 0.0,
                               'DISTANCE TO BUS STOP': 2.06696443,
                               'DISTANCE TO METRO STATION': 1591.414955752,
                               'DISTANCE TO MOTORWAY JUNCTION': 1394.947379297,
                               'DISTANCE TO OVERHEAD LINE': 3371.176664415,
                               'DISTANCE TO PRIMARY SCHOOL': 71.867401834,
                               'DISTANCE TO RAIL STATION': 3117.229318753,
                               'DISTANCE TO SECONDARY SCHOOL': 824.753126148,
                               'DISTANCE TO SUBSTATION': 2981.508831039,
                               'FLOORSPACE': 8711.72585990344},
             'id': 3830,
             'name': 'Lower Lame Road - Land At, Lameside',
             'owner': 'Oldham',
             'postcode': None,
             'region': None,
             'structures': '',
             'uprn': []},
            {'address': None,
             'authority': 'Oldham',
             'centre': {'lat': 53.5129299, 'lon': -2.1582243},
             'footage': '',
             'geoattributes': {'AREA': 1321.17367321562,
                               'BROADBAND': '100',
                               'COVERAGE BY GREENBELT': 0.0,
                               'DISTANCE TO BUS STOP': 175.924922778,
                               'DISTANCE TO METRO STATION': 386.560575227,
                               'DISTANCE TO MOTORWAY JUNCTION': 1206.127109438,
                               'DISTANCE TO OVERHEAD LINE': 1936.069138069,
                               'DISTANCE TO PRIMARY SCHOOL': 382.742359075,
                               'DISTANCE TO RAIL STATION': 1412.324901656,
                               'DISTANCE TO SECONDARY SCHOOL': 984.728804015,
                               'DISTANCE TO SUBSTATION': 1738.073428322,
                               'FLOORSPACE': 1321.17367321562},
             'id': 3825,
             'name': 'Alfrod St - Land North East Of, (Sorplus), Filesworth',
             'owner': 'Oldham',
             'postcode': None,
             'region': None,
             'structures': '',
             'uprn': []}]
        # I ran the scoring on ola roughly like this:
        #   processor = get_processor(terms.get('build', 'primary_school'))
        #   ola_scored_result = processor.rank_results(terms, results)
        # and before that returns:
        #   pprint(df_final.to_dict())
        # and move dist and area_suitable to the end, to fix ordering that got
        # lost during the to_dict.
        expected_scored_result = pd.DataFrame({
            'address': {0: None, 1: None},
            'authority': {0: 'Oldham', 1: 'Oldham'},
            'centre.lat': {0: 53.511647600000003, 1: 53.512929900000003},
            'centre.lon': {0: -2.1275540999999998, 1: -2.1582243000000001},
            'footage': {0: '', 1: ''},
            'geoattributes.AREA': {0: 8711.7258599034394, 1: 1321.1736732156201},
            'geoattributes.BROADBAND': {0: '67', 1: '100'},
            'geoattributes.COVERAGE BY GREENBELT': {0: 0.0, 1: 0.0},
            'geoattributes.DISTANCE TO BUS STOP': {0: 2.0669644300000001,
                                                   1: 175.924922778},
            'geoattributes.DISTANCE TO METRO STATION': {0: 1591.414955752,
                                                        1: 386.56057522700002},
            'geoattributes.DISTANCE TO MOTORWAY JUNCTION': {0: 1394.947379297,
                                                            1: 1206.1271094379999},
            'geoattributes.DISTANCE TO OVERHEAD LINE': {0: 3371.1766644149998,
                                                        1: 1936.069138069},
            'geoattributes.DISTANCE TO PRIMARY SCHOOL': {0: 71.867401834000006,
                                                         1: 382.74235907500002},
            'geoattributes.DISTANCE TO RAIL STATION': {0: 3117.2293187529999,
                                                       1: 1412.3249016560001},
            'geoattributes.DISTANCE TO SECONDARY SCHOOL': {0: 824.75312614799998,
                                                           1: 984.72880401500004},
            'geoattributes.DISTANCE TO SUBSTATION': {0: 2981.5088310390001,
                                                     1: 1738.0734283219999},
            'geoattributes.FLOORSPACE': {0: 8711.7258599034394, 1: 1321.1736732156201},
            'id': {0: 3830, 1: 3825},
            'name': {0: 'Lower Lame Road - Land At, Lameside',
                     1: 'Alfrod St - Land North East Of, (Sorplus), Filesworth'},
            'owner': {0: 'Oldham', 1: 'Oldham'},
            'postcode': {0: None, 1: None},
            'region': {0: None, 1: None},
            'structures': {0: '', 1: ''},
            'uprn': {0: [], 1: []}})
        expected_scored_result['score'] = pd.Series({0: 2.000000,
                                                     1: 2.645751})
        expected_scored_result['area_suitable'] = pd.Series({0: False, 1: False})

        lower_site_req, upper_site_req = \
            ranking.school_site_size_range_from_terms(terms)
        scored_result = ranking.score_result_dicts(
            result_dicts,
            lower_site_req, upper_site_req, school_type=terms.get('build'))
        pprint('Expected:')
        pprint(expected_scored_result)
        pprint('Our func:')
        pprint(scored_result)
        assert_frame_equal(expected_scored_result, scored_result)

    def test_calculate_is_area_suitable(self):
        df = pd.DataFrame({
            'geoattributes.AREA': {0: 1000.0, 1: 2000.0, 2: 3000.0},
            })
        ranking.calculate_is_area_suitable(
            df, lower_site_req=1900.0, upper_site_req=2500.0)
        assert_frame_equal(
            df,
            pd.DataFrame(OrderedDict((
                ('geoattributes.AREA', {0: 1000.0, 1: 2000.0, 2: 3000.0}),
                ('area_suitable', {0: False, 1: True, 2: False}),
            ))))

    def test_z_score_scaling(self):
        df = pd.DataFrame({
            'area_suitable': {0: 1.0, 1: 1.0, 2: 1.0},
            'geoattributes.BROADBAND': {0: 67.0, 1: 100.0, 2: 0.0},
            'geoattributes.COVERAGE BY GREENBELT': {0: 0.0, 1: 0.0, 2: 0.0},
            })
        ranking.z_score_scaling(df)
        pprint(df.to_dict())
        self.assertEqual(
            df.to_dict(),
            {'area_suitable': {0: 1.0, 1: 1.0, 2: 1.0},
             'geoattributes.BROADBAND': {0: 67.0, 1: 100.0, 2: 0.0},
             'geoattributes.BROADBAND_zscore': {0: 0.2724100132220425,
                                                1: 1.0656038752509309,
                                                2: -1.3380138884729731},
             'geoattributes.COVERAGE BY GREENBELT': {0: 0.0, 1: 0.0, 2: 0.0},
             'geoattributes.COVERAGE BY GREENBELT_zscore':
                 {0: 0.0, 1: 0.0, 2: 0.0},
             })

    def test_rescale(self):
        df = pd.DataFrame({
            'area_suitable': {0: True, 1: True, 2: False},
            'geoattributes.BROADBAND': {0: 65, 1: 100.0, 2: 0.0},
            'geoattributes.COVERAGE BY GREENBELT': {0: 0.0, 1: 0.0, 2: 0.0},
            'geoattributes.DISTANCE TO BUS STOP': {0: 1.0, 1: 1.0, 2: 1.0},
            })
        df_out = ranking.rescale_columns_0_to_1(df)
        df_out.applymap(lambda x: round(x, 2))
        pprint(df_out.to_dict())
        assert_frame_equal(
            df_out, pd.DataFrame(OrderedDict([
                ('area_suitable', {0: 1.0, 1: 1.0, 2: 0.0}),
                ('geoattributes.BROADBAND', {0: 0.65, 1: 1.0, 2: 0.0}),
                ('geoattributes.COVERAGE BY GREENBELT', {0: 0.0, 1: 0.0, 2: 0.0}),
                ('geoattributes.DISTANCE TO BUS STOP', {0: 0.0, 1: 0.0, 2: 0.0}),
                ]))
            )

    def test_flip_columns_primary_school(self):
        df = pd.DataFrame({
            'area_suitable': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.BROADBAND': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.COVERAGE BY GREENBELT': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO BUS STOP': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO METRO STATION': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO MOTORWAY JUNCTION': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO OVERHEAD LINE': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO PRIMARY SCHOOL': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO RAIL STATION': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO SECONDARY SCHOOL': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO SUBSTATION': {0: 0.0, 1: 0.6, 2: 1.0},
            })
        ranking.flip_columns_so_1_is_always_best(
            df, school_type='primary_school')
        pprint(df.to_dict())
        assert_frame_equal(df, pd.DataFrame({
            'area_suitable': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.BROADBAND': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.COVERAGE BY GREENBELT': {0: 1.0, 1: 0.4, 2: 0.0},
            'geoattributes.DISTANCE TO BUS STOP': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO METRO STATION': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO MOTORWAY JUNCTION': {0: 1.0, 1: 0.4, 2: 0.0},
            'geoattributes.DISTANCE TO OVERHEAD LINE': {0: 1.0, 1: 0.4, 2: 0.0},
            'geoattributes.DISTANCE TO PRIMARY SCHOOL': {0: 1.0, 1: 0.4, 2: 0.0},
            'geoattributes.DISTANCE TO RAIL STATION': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO SECONDARY SCHOOL': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO SUBSTATION': {0: 1.0, 1: 0.4, 2: 0.0},
            }))

    def test_flip_columns_secondary_school(self):
        df = pd.DataFrame({
            'area_suitable': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.BROADBAND': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.COVERAGE BY GREENBELT': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO BUS STOP': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO METRO STATION': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO MOTORWAY JUNCTION': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO OVERHEAD LINE': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO PRIMARY SCHOOL': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO RAIL STATION': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO SECONDARY SCHOOL': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO SUBSTATION': {0: 0.0, 1: 0.6, 2: 1.0},
            })
        ranking.flip_columns_so_1_is_always_best(
            df, school_type='secondary_school')
        pprint(df.to_dict())
        assert_frame_equal(df, pd.DataFrame({
            'area_suitable': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.BROADBAND': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.COVERAGE BY GREENBELT': {0: 1.0, 1: 0.4, 2: 0.0},
            'geoattributes.DISTANCE TO BUS STOP': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO METRO STATION': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO MOTORWAY JUNCTION': {0: 1.0, 1: 0.4, 2: 0.0},
            'geoattributes.DISTANCE TO OVERHEAD LINE': {0: 1.0, 1: 0.4, 2: 0.0},
            'geoattributes.DISTANCE TO PRIMARY SCHOOL': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO RAIL STATION': {0: 0.0, 1: 0.6, 2: 1.0},
            'geoattributes.DISTANCE TO SECONDARY SCHOOL': {0: 1.0, 1: 0.4, 2: 0.0},
            'geoattributes.DISTANCE TO SUBSTATION': {0: 1.0, 1: 0.4, 2: 0.0},
            }))

    def test_calculate_score(self):
        df = pd.DataFrame({
            'area_suitable':         {0: 0.0,  1: 0.0, 2: 0.0, 3: 1.0},
            'BROADBAND':             {0: 0.67, 1: 1.0, 2: 0.0, 3: 1.0},
            'COVERAGE BY GREENBELT': {0: 0.0,  1: 1.0, 2: 0.0, 3: 1.0},
            })
        ranking.calculate_score(df)
        print(df['score'])
        assert_series_equal(
            df['score'],
            pd.Series([0.67, 1.414214, 0.0, 1.732051], name='score'))

    def test_school_site_size_range_from_terms(self):
        terms = dict(
            pupils=210,
            post16=0,
            build='primary_school'
            )
        self.assertEqual(
            ranking.school_site_size_range_from_terms(terms),
            (1150.45, 1816.5))

    def test_school_site_size_range(self):
        self.assertEqual(
            ranking.school_site_size_range(
                num_pupils=210,
                num_pupils_post16=0,
                school_type='primary_school'),
            (1150.45, 1816.5))


class TestSchoolSiteSize(TestCase):
    def test_primary_0(self):
        self.assertEqual(
            ranking.school_site_size(num_pupils=0,
                                     num_pupils_post16=0,
                                     school_type='primary_school'),
            350.0)

    def test_primary_single_form_entry(self):
        num_pupils = 30 * 7
        size = ranking.school_site_size(num_pupils=num_pupils,
                                        num_pupils_post16=0,
                                        school_type='primary_school')
        self.assertEqual(size, 1211.0)
        space_per_pupil = round(size / num_pupils, 2)
        self.assertEqual(space_per_pupil, 5.77)

    def test_secondary_0(self):
        self.assertEqual(
            ranking.school_site_size(num_pupils=0,
                                     num_pupils_post16=0,
                                     school_type='secondary_school'),
            1050.0)

    def test_secondary_single_form_entry(self):
        num_pupils = 30 * 5
        size = ranking.school_site_size(num_pupils=num_pupils,
                                        num_pupils_post16=0,
                                        school_type='secondary_school')
        self.assertEqual(size, 1995.0)
        space_per_pupil = round(size / num_pupils, 2)
        self.assertEqual(space_per_pupil, 13.3)

    def test_secondary_with_210(self):
        # for direct comparison with the 210 below, where 60 are over 16
        # rather than under 16.
        num_pupils = 30 * 7
        size = ranking.school_site_size(num_pupils=num_pupils,
                                        num_pupils_post16=0,
                                        school_type='secondary_school')
        self.assertEqual(size, 2373.0)
        space_per_pupil = round(size / num_pupils, 2)
        self.assertEqual(space_per_pupil, 11.3)

    def test_secondary_single_form_entry_with_sixth_form(self):
        num_pupils = 30 * 7
        num_pupils_post16 = 30 * 2
        size = ranking.school_site_size(num_pupils=num_pupils,
                                        num_pupils_post16=num_pupils_post16,
                                        school_type='secondary_school')
        self.assertEqual(size, 2765.0)
        space_per_pupil = round(size / num_pupils, 2)
        self.assertEqual(space_per_pupil, 13.17)


# OLA functions #

# These are copied straight from OLA. They marshall the data going into and out
# of the scoring algorithm, so that we can ensure our underlying scoring
# algorithm behaves the same as in OLA.

def convert_elastic_results_to_dicts(resultset):
    e = []
    for r in resultset:
        d = r.to_dict()
        del d['geom']
        if 'titles' in d:
            del d['titles']
        if 'district' in d:
            del d['district']
        e.append(d)
    return e

def convert_df_to_elastic_results(df, terms):
    jsonblob = df.to_json(orient='records')
    normalized_results = json.loads(jsonblob)
    lower_site_req, upper_site_req = \
        ranking.school_site_size_range_from_terms(terms)
    return [denormalize_dict(d, lower_site_req, upper_site_req)
            for d in normalized_results]

def denormalize_dict(source, lower_site_req, upper_site_req, separator="."):
    """ Only denormalizes a single level and only dicts, so "k.k1":v
    will get transformed into "k": {"k1": v} """
    result = {}
    for k, v in source.items():
        if separator in k:
            top, lower = k.split(separator)
            d = result.get(top) or {}
            d[lower] = v
            result[top] = d
        else:
            result[k] = v
    result['lower_site_req'] = lower_site_req
    result['upper_site_req'] = upper_site_req
    return result

class ResultList(list):
    """
    HACK!
    This allows us to assign the 'hits' from the actual search results
    to the list we get back from the optimisation
    HACK!
    """
    hits = 0

# End of OLA functions #