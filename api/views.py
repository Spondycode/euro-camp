from django.db import transaction
from django.db.models import Count, Exists, OuterRef, Q, Value, BooleanField
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import authentication, status, generics
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from core.models import Campsite, CampsiteLike, Product
from .serializers import CampsiteSerializer, ProductSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})


class CampsitePagination(PageNumberPagination):
    """Custom pagination for campsites list."""
    page_size = 30
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'current_page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })


@extend_schema(
    summary="List campsites (paginated)",
    parameters=[
        OpenApiParameter(name='country', description='2-letter country code', required=False, type=OpenApiTypes.STR),
        OpenApiParameter(name='search', description='Search in name or town', required=False, type=OpenApiTypes.STR),
        OpenApiParameter(name='page', description='Page number (1-based)', required=False, type=OpenApiTypes.INT),
    ],
)
class CampsiteListAPIView(generics.ListAPIView):
    """API view for paginated campsites list with filters."""
    serializer_class = CampsiteSerializer
    pagination_class = CampsitePagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        request = self.request
        user = request.user

        qs = Campsite.objects.all()

        # Approval visibility: staff can see all, others only approved
        if not user.is_staff:
            qs = qs.filter(is_approved=True)

        # Filter by country
        country = request.query_params.get('country')
        if country:
            qs = qs.filter(country__iexact=country.strip())

        # Search in name or town
        search = request.query_params.get('search')
        if search:
            s = search.strip()
            qs = qs.filter(Q(name__icontains=s) | Q(town__icontains=s))

        # Annotate with like count
        qs = qs.annotate(
            like_count=Count('likes', distinct=True)
        )

        # Annotate with has_liked for authenticated users
        if user.is_authenticated:
            qs = qs.annotate(
                has_liked=Exists(
                    CampsiteLike.objects.filter(user=user, campsite_id=OuterRef('pk'))
                )
            )
        else:
            qs = qs.annotate(has_liked=Value(False, output_field=BooleanField()))

        # Ordering: premium first, then by like count desc, then by name
        qs = qs.order_by('-is_premium', '-like_count', 'name')

        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class CampsiteLikeToggleView(APIView):
    """Toggle like/unlike for a campsite."""
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, campsite_id):
        campsite = get_object_or_404(Campsite, id=campsite_id)
        user = request.user

        with transaction.atomic():
            like, created = CampsiteLike.objects.get_or_create(user=user, campsite=campsite)
            if created:
                is_liked = True
            else:
                like.delete()
                is_liked = False

        like_count = CampsiteLike.objects.filter(campsite=campsite).count()
        return Response(
            {'is_liked': is_liked, 'like_count': like_count},
            status=status.HTTP_200_OK
        )


class CampsiteLikeStatusView(APIView):
    """Get like status and count for a campsite."""
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, campsite_id):
        campsite = get_object_or_404(Campsite, id=campsite_id)
        is_liked = CampsiteLike.objects.filter(user=request.user, campsite=campsite).exists()
        like_count = CampsiteLike.objects.filter(campsite=campsite).count()
        return Response(
            {'is_liked': is_liked, 'like_count': like_count},
            status=status.HTTP_200_OK
        )


# Custom Permission

class IsSuperAdmin(BasePermission):
    """Custom permission to only allow super admins."""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_super_admin or request.user.is_superuser)
        )


# Product API Views

class ProductListAPIView(generics.ListAPIView):
    """List all featured products."""
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Product.objects.filter(is_featured=True).order_by('name')


class ProductDetailAPIView(generics.RetrieveAPIView):
    """Retrieve a single product."""
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    queryset = Product.objects.all()


class ProductCreateAPIView(generics.CreateAPIView):
    """Create a new product (super admin only)."""
    serializer_class = ProductSerializer
    permission_classes = [IsSuperAdmin]
    queryset = Product.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProductUpdateAPIView(generics.UpdateAPIView):
    """Update a product (super admin only)."""
    serializer_class = ProductSerializer
    permission_classes = [IsSuperAdmin]
    queryset = Product.objects.all()


class ProductDestroyAPIView(generics.DestroyAPIView):
    """Delete a product (super admin only)."""
    serializer_class = ProductSerializer
    permission_classes = [IsSuperAdmin]
    queryset = Product.objects.all()
