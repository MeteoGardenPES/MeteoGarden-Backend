from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import User


class IdentifyAndSavePlantTests(APITestCase):
    def test_requires_image(self):
        url = reverse("images/yulan-magnolia.jpg")
        resp = self.client.post(
            url,
            data={"username": "testuser", "organs": "flower"},
            format="multipart",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("image", resp.data)

    def test_invalid_organ(self):
        url = reverse("images/yulan-magnolia.jpg")
        img = SimpleUploadedFile(
            "yulan-magnolia.jpg", b"fakebytes", content_type="image/jpeg"
        )

        resp = self.client.post(
            url,
            data={"username": "testuser", "organs": "xxx", "image": img},
            format="multipart",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("organs", resp.data)
