from django.db.models import Count, Q
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import ForumComment, ForumPost, ForumPostLike, ForumSpace, User


class ForumUserSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'display_name', 'avatar', 'role']

    def get_display_name(self, obj):
        return obj.full_name or obj.username


class ForumSpaceSerializer(serializers.ModelSerializer):
    created_by = ForumUserSerializer(read_only=True)
    post_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ForumSpace
        fields = ['id', 'title', 'description', 'created_by', 'is_public', 'created_at', 'updated_at', 'post_count']


class ForumCommentSerializer(serializers.ModelSerializer):
    author = ForumUserSerializer(read_only=True)
    post_id = serializers.PrimaryKeyRelatedField(source='post', queryset=ForumPost.objects.all(), write_only=True)
    parent_id = serializers.PrimaryKeyRelatedField(
        source='parent',
        queryset=ForumComment.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    replies = serializers.SerializerMethodField()

    class Meta:
        model = ForumComment
        fields = ['id', 'post', 'post_id', 'parent', 'parent_id', 'author', 'content', 'created_at', 'updated_at', 'replies']

    def get_replies(self, obj):
        replies = obj.replies.select_related('author', 'post').all()
        return ForumCommentSerializer(replies, many=True, context=self.context).data

    def validate_post(self, value):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if value.forum.is_public or value.forum.created_by_id == request.user.id:
                return value
        raise serializers.ValidationError('Bạn không có quyền bình luận trong diễn đàn này.')

    def validate(self, attrs):
        post = attrs.get('post')
        parent = attrs.get('parent')

        if parent and parent.post_id != post.id:
            raise serializers.ValidationError({'parent': 'Bình luận trả lời phải thuộc cùng một bài viết.'})

        return attrs


class ForumPostSerializer(serializers.ModelSerializer):
    forum = ForumSpaceSerializer(read_only=True)
    forum_id = serializers.PrimaryKeyRelatedField(source='forum', queryset=ForumSpace.objects.all(), write_only=True)
    author = ForumUserSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    liked_by_me = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = ForumPost
        fields = [
            'id', 'forum', 'forum_id', 'author', 'title', 'content', 'kind', 'is_pinned',
            'created_at', 'updated_at', 'like_count', 'comment_count', 'liked_by_me', 'comments',
        ]

    def get_liked_by_me(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return ForumPostLike.objects.filter(post=obj, user=request.user).exists()

    def get_comments(self, obj):
        top_level_comments = obj.comments.filter(parent__isnull=True).select_related('author', 'post').prefetch_related('replies__author')
        return ForumCommentSerializer(top_level_comments, many=True, context=self.context).data

    def validate_forum(self, value):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if value.is_public or value.created_by_id == request.user.id:
                return value
        raise serializers.ValidationError('Bạn không có quyền đăng bài trong diễn đàn này.')


class ForumSpaceViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ForumSpaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (
            ForumSpace.objects.filter(Q(is_public=True) | Q(created_by=user))
            .select_related('created_by')
            .annotate(post_count=Count('posts', distinct=True))
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ForumPostViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ForumPostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = (
            ForumPost.objects.filter(Q(forum__is_public=True) | Q(forum__created_by=user))
            .select_related('forum', 'forum__created_by', 'author')
            .prefetch_related('comments__author', 'comments__replies__author')
            .annotate(
                like_count=Count('likes', distinct=True),
                comment_count=Count('comments', distinct=True),
            )
        )

        forum_id = self.request.query_params.get('forum_id')
        if forum_id:
            queryset = queryset.filter(forum_id=forum_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = ForumPostLike.objects.get_or_create(post=post, user=request.user)

        if not created:
            like.delete()

        like_count = ForumPostLike.objects.filter(post=post).count()
        return Response(
            {
                'liked': created,
                'like_count': like_count,
            },
            status=status.HTTP_200_OK,
        )


class ForumCommentViewSet(CreateModelMixin, ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ForumCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        post_id = self.request.query_params.get('post_id')
        queryset = (
            ForumComment.objects.filter(Q(post__forum__is_public=True) | Q(post__forum__created_by=user))
            .select_related('author', 'post', 'parent', 'post__forum')
            .prefetch_related('replies__author')
        )

        if post_id:
            queryset = queryset.filter(post_id=post_id)
        else:
            queryset = queryset.none()

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)