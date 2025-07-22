from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'messages', views.GroupMessageViewSet)
router.register(r'calls', views.CallViewSet)
router.register(r'assignments', views.AssignmentViewSet)
router.register(r'submissions', views.AssignmentSubmissionViewSet)
router.register(r'materials', views.MaterialViewSet)
router.register(r'subscriptions', views.SubscriptionViewSet)
router.register(r'games', views.ChessGameViewSet)
router.register(r'reviews', views.ReviewViewSet)
router.register(r'applications', views.JobApplicationViewSet)
router.register(r'bookings', views.LessonBookingViewSet)

