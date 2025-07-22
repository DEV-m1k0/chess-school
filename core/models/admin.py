from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

admin.site.register(User)
admin.site.register(Group)
admin.site.register(GroupMessage)
admin.site.register(Call)
admin.site.register(Assignment)
admin.site.register(AssignmentSubmission)
admin.site.register(Material)
admin.site.register(Subscription)
admin.site.register(ChessGame)
admin.site.register(Review)
admin.site.register(JobApplication)
admin.site.register(LessonBooking)
