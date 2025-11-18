from rest_framework import serializers
from core.models import Campsite, Product


class CampsiteSerializer(serializers.ModelSerializer):
    """Serializer for Campsite model with pagination support."""
    country_name = serializers.CharField(source='get_country_display', read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    has_liked = serializers.SerializerMethodField()

    class Meta:
        model = Campsite
        fields = [
            'id',
            'name',
            'town',
            'description',
            'country',
            'country_name',
            'image_url',
            'website',
            'phone_number',
            'is_premium',
            'is_approved',
            'like_count',
            'has_liked',
            'type',
            'province',
        ]

    def get_has_liked(self, obj):
        """Get whether the current user has liked this campsite."""
        # Expect queryset annotated with 'has_liked'
        return getattr(obj, 'has_liked', False)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'image_url', 'amazon_link', 'is_featured', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'created_by']
