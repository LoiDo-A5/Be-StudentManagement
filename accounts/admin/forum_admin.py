from django.contrib import admin


class ForumSpaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_by', 'is_public', 'created_at')
    search_fields = ('title', 'description', 'created_by__username')
    list_filter = ('is_public', 'created_at')


class ForumPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'forum', 'title', 'author', 'kind', 'is_pinned', 'created_at')
    search_fields = ('title', 'content', 'forum__title', 'author__username')
    list_filter = ('forum', 'kind', 'is_pinned', 'created_at')


class ForumCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'author', 'parent', 'created_at')
    search_fields = ('content', 'post__title', 'author__username')
    list_filter = ('post', 'created_at')


class ForumPostLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'created_at')
    search_fields = ('post__title', 'user__username')
    list_filter = ('created_at',)