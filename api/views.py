from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import authentication, status
from core.models import Campsite, CampsiteLike


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})


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
