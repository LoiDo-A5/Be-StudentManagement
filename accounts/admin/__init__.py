from django.contrib import admin
from rest_framework.authtoken.models import TokenProxy

from accounts.admin.chatroom_admin import ChatRoomAdmin
from accounts.admin.class_level_admin import ClassLevelAdmin
from accounts.admin.class_name_admin import ClassNameAdmin
from accounts.admin.class_student_admin import ClassStudentAdmin
from accounts.admin.direct_message_admin import DirectMessageAdmin
from accounts.admin.friendship_admin import FriendShipAdmin
from accounts.admin.forum_admin import ForumSpaceAdmin, ForumPostAdmin, ForumCommentAdmin, ForumPostLikeAdmin
from accounts.admin.message_admin import MessageAdmin
from accounts.admin.student_score_admin import StudentScoreAdmin
from accounts.admin.subject_admin import SubjectAdmin
from accounts.admin.subject_score_admin import SubjectScoreAdmin
from accounts.admin.system_setting_age_admin import SystemSettingAdmin
from accounts.admin.token_admin import FilterTokenAdmin
from accounts.admin.user_admin import UserAdmin
from accounts.models import User, ChatRoom, Message, DirectMessage, Friendship, ClassLevel, ClassName, ClassStudent, \
    StudentScore, Subject, SubjectScore, SystemSetting, ForumSpace, ForumPost, ForumComment, ForumPostLike

admin.site.register(User, UserAdmin)
admin.site.register(ChatRoom, ChatRoomAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(DirectMessage, DirectMessageAdmin)
admin.site.register(Friendship, FriendShipAdmin)

admin.site.unregister(TokenProxy)
admin.site.register(TokenProxy, FilterTokenAdmin)
admin.site.register(ClassLevel, ClassLevelAdmin)
admin.site.register(ClassName, ClassNameAdmin)
admin.site.register(ClassStudent, ClassStudentAdmin)
admin.site.register(StudentScore, StudentScoreAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(SubjectScore, SubjectScoreAdmin)
admin.site.register(SystemSetting, SystemSettingAdmin)
admin.site.register(ForumSpace, ForumSpaceAdmin)
admin.site.register(ForumPost, ForumPostAdmin)
admin.site.register(ForumComment, ForumCommentAdmin)
admin.site.register(ForumPostLike, ForumPostLikeAdmin)
