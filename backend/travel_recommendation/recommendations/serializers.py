from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Recommendation, Traveler, Trip, Guide, AIInteraction


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = '__all__'


class GuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guide
        fields = '__all__'


class TravelerSerializer(serializers.ModelSerializer):
    # user is read-only and assigned automatically via signals/app logic
    user = serializers.ReadOnlyField(source='user.id')
    profile_pic_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Traveler
        fields = ('id', 'user', 'bio', 'featured', 'profile_pic', 'profile_pic_url')
        read_only_fields = ('id', 'profile_pic_url', 'user')

    def get_profile_pic_url(self, obj):
        if obj.profile_pic:
            request = self.context.get('request', None)
            if request is not None:
                return request.build_absolute_uri(obj.profile_pic.url)
            return obj.profile_pic.url
        return None


class TripSerializer(serializers.ModelSerializer):
    traveler = serializers.PrimaryKeyRelatedField(queryset=Traveler.objects.all())
    recommendations = serializers.PrimaryKeyRelatedField(queryset=Recommendation.objects.all(), many=True, required=False)

    class Meta:
        model = Trip
        fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def validate_password(self, value):
        # Use Django's password validators
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


# -----------------
# AI Interaction serializer
# -----------------
class AIInteractionSerializer(serializers.ModelSerializer):
    # user is read-only and set automatically by the view
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = AIInteraction
        fields = ('id', 'user', 'prompt', 'ai_response', 'created_at')
        read_only_fields = ('id', 'user', 'prompt', 'ai_response', 'created_at')


# -----------------
# Profile serializer for user's own profile
# -----------------
class TravelerProfileSerializer(serializers.ModelSerializer):
    """Serializer for authenticated user's own profile (GET/PUT)."""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    joined_on = serializers.DateTimeField(source='user.date_joined', read_only=True)
    profile_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Traveler
        fields = ('username', 'email', 'joined_on', 'bio', 'profile_image', 'interests', 'travel_style')
        read_only_fields = ('username', 'email', 'joined_on', 'profile_image')

    def get_profile_image(self, obj):
        """Return absolute URL for profile image if it exists."""
        if obj.profile_pic:
            request = self.context.get('request', None)
            if request is not None:
                return request.build_absolute_uri(obj.profile_pic.url)
            return obj.profile_pic.url
        return None
