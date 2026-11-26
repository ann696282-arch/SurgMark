import base64
import io
import unittest
from PIL import Image
from server import app, image_from_payload

class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.url = 'http://127.0.0.1:8765'

    def test_local_ui_and_status(self):
        with self.client.get('/', base_url=self.url) as response:
            self.assertEqual(response.status_code, 200)
        self.assertIn('models', self.client.get('/api/status', base_url=self.url).json)

    def test_esd_assets_are_served(self):
        for path in ['app.js','esd-core.js','style.css']:
            with self.client.get('/'+path, base_url=self.url) as response:
                self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get('/server.py', base_url=self.url).status_code, 404)

    def test_cross_origin_blocked(self):
        r = self.client.post('/api/classify', base_url=self.url, headers={'Origin': 'https://external.example'}, json={})
        self.assertEqual(r.status_code, 403)

    def test_untrusted_host_blocked(self):
        self.assertEqual(self.client.get('/api/status', base_url='http://external.example').status_code, 403)

    def test_input_validation(self):
        self.assertEqual(self.client.post('/api/classify', base_url=self.url, json={'labels': []}).status_code, 400)
        self.assertEqual(self.client.post('/api/segment', base_url=self.url, json={'image':'bad'}).status_code, 400)

    def test_frame_decode(self):
        b = io.BytesIO()
        Image.new('RGB', (32, 24)).save(b, 'JPEG')
        image = image_from_payload({'image': 'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()})
        self.assertEqual(image.size, (32, 24))

if __name__ == '__main__':
    unittest.main()
