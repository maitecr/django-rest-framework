from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import HTTP_418_IM_A_TEAPOT
from rest_framework.viewsets import ModelViewSet
from tag.models import Tag

from ..models import Recipe
from ..permissions import IsOwner
from ..serializers import RecipeSerializer, TagSerializer


class RecipeAPIv2Pagination(PageNumberPagination):
    page_size = 1


class RecipeAPIv2ViewSet(ModelViewSet):
    queryset = Recipe.objects.get_published()
    serializer_class = RecipeSerializer
    pagination_class = RecipeAPIv2Pagination
    permission_classes = [IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        qs = super().get_queryset()

        print(self.request.query_params)  # parâmetros capturados na url
        category_id = self.request.query_params.get('category_id', '')

        if category_id != '' and category_id.isnumeric():
            qs = qs.filter(category_id=category_id)

        return qs

    def get_object(self):
        pk = self.kwargs.get('pk', '')
        obj = get_object_or_404(
            self.get_queryset(),
            pk=pk
        )

        self.check_object_permissions(self.request, obj)

        return obj

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsOwner(), ]

        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        print('REQUEST', request.user, self.request.user)
        print(request.user.is_authenticated)
        return super().list(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        pk = kwargs.get('pk')

        recipe = self.get_object()
        serializer = RecipeSerializer(
            instance=recipe,
            data=request.data,
            many=False,
            context={'request': request},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
        )

# class RecipeAPIv2List(ListCreateAPIView):
#     queryset = Recipe.objects.get_published()
#     serializer_class = RecipeSerializer
#     pagination_class = RecipeAPIv2Pagination

    # def get(self, request):
    #     recipes = Recipe.objects.get_published()[:10]
    #     serializer = RecipeSerializer(
    #         instance=recipes,
    #         many=True,
    #         context={'request': request}
    #     )

    #     return Response(serializer.data)

    # def post(self, request):
    #     serializer = RecipeSerializer(
    #         data=request.data,
    #         context={'request': request},
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(
    #         author_id=1, category_id=1, tags=[1, 2]
    #     )

    #     return Response(
    #         serializer.data,
    #         status=status.HTTP_201_CREATED,
    #     )


# class RecipeAPIv2Detail(RetrieveUpdateDestroyAPIView):
#     queryset = Recipe.objects.get_published()
#     serializer_class = RecipeSerializer
#     pagination_class = RecipeAPIv2Pagination

    # def get_recipe(self, pk):
    #     recipe = get_object_or_404(
    #         Recipe.objects.get_published(),
    #         pk=pk
    #     )
    #     return recipe

    # def get(self, request, pk):
    #     recipe = self.get_recipe(pk)

    #     serializer = RecipeSerializer(
    #         instance=recipe,
    #         many=False,
    #         context={'request': request}
    #     )
    #     return Response(serializer.data)

    # def patch(self, request, pk):
    #     recipe = self.get_recipe(pk)

    #     serializer = RecipeSerializer(
    #         instance=recipe,
    #         data=request.data,
    #         many=False,
    #         context={'request': request},
    #         partial=True
    #     )

    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(
    #         serializer.data,
    #     )

    # def delete(self, request, pk):
    #     recipe = self.get_recipe(pk)
    #     recipe.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


@api_view()
def tag_api_detail(request, pk):
    tag = get_object_or_404(
        Tag.objects.all(),
        pk=pk
    )
    serializer = TagSerializer(
        instance=tag,
        many=False,
        context={'request': request}
    )

    return Response(serializer.data)
