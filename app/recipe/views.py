from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Tag, Ingredient, Recipe
from recipe import serializers

class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """base viewset for user owned recipe attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """return objects for the current authencated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')
    def perform_create(self, serializer):
        """creating a new object """
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """manage tag in the database"""

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

class IngredientViewSet(BaseRecipeAttrViewSet):
    """manage ingredient in the database"""
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecieViewSet(viewsets.ModelViewSet):
    """manage recipe in the data base"""

    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """retrive the recipes for the authen. user"""
        return self.queryset.filter(user = self.request.user)

    def get_serializer_class(self):
        """return apropriate serializer class"""
        if self.action== 'retrieve':
            return serializers.RecipeDetailSerializer

        return self.serializer_class