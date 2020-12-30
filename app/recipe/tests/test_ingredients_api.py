from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL= reverse('recipe:ingredient-list')

class PublicIngedientsApiTests(TestCase):
    """test publicly available ing. api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """test that login is required to access the enpoint"""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatIngredientsApiTests(TestCase):
    """Test ingredients can be retrived ba aut. user"""
    def setUp(self):
        self.client=APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com,'
            'test1234'
        )
        self.client.force_authenticate(self.user)

    def test_ingredient_list(self):
        """test retriving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='kale')
        Ingredient.objects.create(user=self.user, name='salt')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many = True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """test that ingredients for the auth. user ar returned"""

        user2 = get_user_model().objects.create_user(
            'test2@test.com',
            'test12345'
        )
        Ingredient.objects.create(user=user2, name='Vinegar')

        ingredient=Ingredient.objects.create(user=self.user, name='tumeric')
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """test create new ing."""
        payload = {'name': 'cabbage'}
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """test creating invalid ing. fails"""
        payload = {'name':''}

        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrive_ingredient_assigned_to_recipes(self):
        """test filtering ingredients by those assigned to recipes """
        ingredient1 = Ingredient.objects.create(
            user = self.user, name='jabuke'
        )
        ingredient2 = Ingredient.objects.create(
            user = self.user, name='kruske'
        )
        recipe = Recipe.objects.create(
            title='jabukovaca',
            time_minutes=10,
            price = 8.00,
            user = self.user
        )
        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only':1})
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)


    def test_retrive_ingredients_assignet_unique(self):
        """test filtering ingredients by assigned returns uniqu items"""
        ingredient= Ingredient.objects.create(user=self.user, name='jaja')
        Ingredient.objects.create(user=self.user, name = 'sir')
        recipe1 = Recipe.objects.create(
            title = 'jaja sa sirom',
            time_minutes = 30,
            price = 9.00,
            user = self.user
        )
        recipe1.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            title = 'topa',
            time_minutes = 20,
            price = 4.00,
            user = self.user
        )
        recipe2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only':1})

        self.assertEqual(len(res.data),1)