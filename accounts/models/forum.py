from django.db import models

from accounts.models import User


class ForumSpace(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_forum_spaces')
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ForumPost(models.Model):
    KIND_DISCUSSION = 'discussion'
    KIND_QUESTION = 'question'
    KIND_RESOURCE = 'resource'

    KIND_CHOICES = (
        (KIND_QUESTION, 'Question'),
        (KIND_DISCUSSION, 'Discussion'),
        (KIND_RESOURCE, 'Resource'),
    )

    forum = models.ForeignKey(ForumSpace, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default=KIND_QUESTION)
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title


class ForumComment(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_comments')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author} -> {self.post}'


class ForumPostLike(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_post_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['post', 'user'], name='unique_forum_post_like'),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} likes {self.post}'