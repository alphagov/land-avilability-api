from unittest import TestCase
import pytest
import json
from django.contrib.gis.geos import Point
from api.models import BusStop, TrainStop, Address, CodePoint, Broadband
from api.serializers import (
    BusStopSerializer, TrainStopSerializer, AddressSerializer,
    CodePointSerializer, BroadbandSerializer)


class TestBusStopSerializer(TestCase):
    @pytest.mark.django_db
    def test_busstop_serializer_create_object(self):
        json_payload = """
            {
                "amic_code": "1800AMIC001",
                "point": {
                    "type": "Point",
                    "coordinates": [-2.347743000012108,53.38737090322739]
                },
                "name": "Altrincham Interchange",
                "direction": "Nr Train Station",
                "area": "NA",
                "road": "STAMFORD NEW RD",
                "nptg_code": "E0028261",
                "srid": 4326
            }
        """

        data = json.loads(json_payload)
        serializer = BusStopSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        serializer.save()
        self.assertEqual(BusStop.objects.count(), 1)


class TestTrainStopSerializer(TestCase):
    @pytest.mark.django_db
    def test_trainstop_serializer_create_object(self):
        json_payload = """
            {
                "atcode_code": "9100ALTRNHM",
                "naptan_code": "",
                "point": {
                    "type": "Point",
                    "coordinates": [377008, 387924]
                },
                "name": "DATALAND INTERCHANGE",
                "main_road": "DATALAND NEW RD",
                "side_road": "DATA LANE",
                "type": "R",
                "nptg_code": "E0028261",
                "local_reference": "AA123ZZ",
                "srid": 27700
            }
        """

        data = json.loads(json_payload)
        serializer = TrainStopSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        serializer.save()
        self.assertEqual(TrainStop.objects.count(), 1)


class TestAddressSerializer(TestCase):
    @pytest.mark.django_db
    def test_address_serializer_create_object(self):
        json_payload = """
            {
                "uprn": "12345678",
                "address_line_1": "Dataland",
                "address_line_2": "Dataland Village Main Street",
                "city": "Dataland City",
                "county": "Cucumberland",
                "postcode": "AA11 1ZZ",
                "country_code": "GB",
                "point": {
                    "type": "Point",
                    "coordinates": [55.4168769443259, -1.83356713993623]
                },
                "srid": 4326
            }
        """

        data = json.loads(json_payload)
        serializer = AddressSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        serializer.save()
        self.assertEqual(Address.objects.count(), 1)


class TestCodePointSerializer(TestCase):
    @pytest.mark.django_db
    def test_codepoint_serializer_create_object(self):
        json_payload = """
            {
                "postcode": "BL0 0AA",
                "quality": "10",
                "country": "E92000001",
                "nhs_region": "E19000001",
                "nhs_health_authority": "E18000002",
                "county": "",
                "district": "E08000002",
                "ward": "E05000681",
                "point": {
                    "type": "Point",
                    "coordinates": [379448, 416851]
                },
                "srid": 27700
            }
        """

        data = json.loads(json_payload)
        serializer = CodePointSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        serializer.save()
        self.assertEqual(CodePoint.objects.count(), 1)


class TestBroadbandSerializer(TestCase):
    @pytest.mark.django_db
    def test_broadband_serializer_create_object(self):
        # Prepare a CodePoint
        codepoint = CodePoint()
        codepoint.postcode = 'ME58TL'
        codepoint.point = Point(
            float("-1.83356713993623"), float("55.4168769443259"))
        codepoint.quality = 10
        codepoint.save()

        json_payload = """
            {
                "postcode": "ME5 8TL",
                "speed_30_mb_percentage": 50,
                "avg_download_speed": 10.5,
                "min_download_speed": 2.8,
                "max_download_speed": 12.3,
                "avg_upload_speed": 0.5,
                "min_upload_speed": 0.3,
                "max_upload_speed": 1.1
            }
        """

        data = json.loads(json_payload)
        serializer = BroadbandSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        serializer.save()
        self.assertEqual(Broadband.objects.count(), 1)

    @pytest.mark.django_db
    def test_broadband_invalid_serializer_no_codepoint(self):
        json_payload = """
            {
                "postcode": "ME5 8TL",
                "speed_30_mb_percentage": 50,
                "avg_download_speed": 10.5,
                "min_download_speed": 2.8,
                "max_download_speed": 12.3,
                "avg_upload_speed": 0.5,
                "min_upload_speed": 0.3,
                "max_upload_speed": 1.1
            }
        """

        data = json.loads(json_payload)
        serializer = BroadbandSerializer(data=data)
        self.assertFalse(serializer.is_valid())
