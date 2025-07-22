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

class GroupMessageViewSet(viewsets.ModelViewSet):
    queryset = GroupMessage.objects.all()  
    serializer_class = GroupMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(group__students=self.request.user)

class CallViewSet(viewsets.ModelViewSet):
    queryset = Call.objects.all()  
    serializer_class = CallSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(group__teacher=self.request.user)

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()  
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(group__teacher=self.request.user)

class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    queryset = AssignmentSubmission.objects.all()  
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'teacher':
            return super().get_queryset().filter(assignment__group__teacher=self.request.user)
        return super().get_queryset().filter(student=self.request.user)

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()  
    serializer_class = MaterialSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(group__teacher=self.request.user)

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()  
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(student=self.request.user)

class ChessGameViewSet(viewsets.ModelViewSet):
    queryset = ChessGame.objects.all()
    serializer_class = ChessGameSerializer
    permission_classes = [permissions.IsAuthenticated]

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()  
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)

class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.all()  
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(applicant=self.request.user)

class LessonBookingViewSet(viewsets.ModelViewSet):
    queryset = LessonBooking.objects.all()  
    serializer_class = LessonBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'teacher':
            return super().get_queryset().filter(teacher=self.request.user)
        return super().get_queryset().filter(student=self.request.user)
    
