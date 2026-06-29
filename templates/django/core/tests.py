from django.test import SimpleTestCase
from django.urls import reverse

class CoreTests(SimpleTestCase):
    def test_health_check(self):
        url = reverse('health_check')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "UP")
        self.assertIn("uptime", data)
        self.assertIn("timestamp", data)

    def test_api_info(self):
        url = reverse('get_info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertEqual(data["status"], "operational")
