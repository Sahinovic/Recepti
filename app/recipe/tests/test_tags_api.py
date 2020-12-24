from django.contrib.auth import  get_user_model
from django.urls import  reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import  APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL= reverse('recipe:tag-list')

class PublicTagsApiTests(TestCase):
    """tast the publicly available tags API"""
    def setUp(self):
        self.client= APIClient()

    def test_login_required(self):
        """test that login is required for retriving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsAPiTests(TestCase):
    """test the authorized user tags API"""

    def setUp(self):
        self.user=get_user_model().objects.create_user(
            'test@test.com',
            "password1234"
        )
        self.client=APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_tags(self):
        """Test retriving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res=self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """test that tags returned are for the authe. user"""
        user2=get_user_model().objects.create_user(
            'test1@test.com',
            'testpass'
        )
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name = 'comfort food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
