from rest_framework import viewsets, permissions, status
from .models import *
from .serializers import *
from .permissions import *


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrSelf]  
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(id=self.request.user.id)

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()  
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

