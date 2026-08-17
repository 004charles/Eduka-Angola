import json

from django.test import RequestFactory, TestCase

from core.views import coordenadas_publicas, public_nearby_courses


class NearbyCoursesEndpointTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_rejects_coordinates_outside_valid_ranges(self):
        response = public_nearby_courses(self.factory.get('/api/public/cursos/proximos/?lat=120&lng=13'))

        self.assertEqual(response.status_code, 400)
        self.assertIn('intervalo permitido', json.loads(response.content)['detail'])

    def test_reads_confirmed_coordinates_from_the_non_gis_fallback(self):
        centre = type('Centro', (), {'localizacao': '-8.8390, 13.2894'})()

        self.assertEqual(coordenadas_publicas(centre), (-8.839, 13.2894))

    def test_accepts_valid_coordinates_without_persisting_visitor_location(self):
        response = public_nearby_courses(self.factory.get('/api/public/cursos/proximos/?lat=-8.8390&lng=13.2894'))
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload['ok'])
        self.assertIn('cursos', payload)
