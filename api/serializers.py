from rest_framework import serializers
from core.models import Campsite


class CampsiteSerializer(serializers.ModelSerializer):
    like_count = serializers.IntegerField(read_only=True)
    user_has_liked = serializers.SerializerMethodField()

    class Meta:
        model = Campsite
        fields = ['id', 'name', 'country', 'description', 'like_count', 'user_has_liked']

    def get_user_has_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        liked_ids = self.context.get('liked_ids')
        if liked_ids is not None:
            return obj.id in liked_ids
        # Fallback (avoid N+1 where possible; views will pass liked_ids)
        return obj.likes.filter(user=request.user).exists()