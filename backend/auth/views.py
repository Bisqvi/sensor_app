from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import RegisterSerializer, UserSummarySerializer
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(["POST"])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    refresh = RefreshToken.for_user(user)
    return Response({
        "user": UserSummarySerializer(user).data,
        "token": {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }
    }, status=status.HTTP_201_CREATED)