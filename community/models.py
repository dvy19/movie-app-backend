import uuid
import secrets
from django.db import models
from django.utils.text import slugify
from django.utils import timezone


class Group(models.Model):
    owner = models.ForeignKey(
        "users.CustomUser", 
        related_name='owned_groups',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True, null=True)
    icon = models.ImageField(
        upload_to='group_icons/',
        blank=True,
        null=True
    )
    
    # A permanent slug can still be useful for the group's main URL profile (e.g., /groups/movie-buffs-xyz/)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_suffix = uuid.uuid4().hex[:6]
            self.slug = f"{base_slug}-{unique_suffix}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class GroupInvitation(models.Model):
    group = models.ForeignKey(
        Group, 
        related_name='invitations', 
        on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
        "users.CustomUser", 
        related_name='created_invites', 
        on_delete=models.CASCADE
    )
    code = models.CharField(max_length=12, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    # Optional enhancements for later:
    # expires_at = models.DateTimeField(null=True, blank=True)
    # max_uses = models.PositiveIntegerField(default=0) # 0 for unlimited
    # times_used = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.code:
            # Generate a secure random code when the owner requests an invite
            self.code = secrets.token_urlsafe(6).upper() # e.g., 'X7K9P2M4'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invite for {self.group.name} ({self.code})"


class GroupMember(models.Model):
    user = models.ForeignKey(
        "users.CustomUser", 
        related_name='group_memberships', 
        on_delete=models.CASCADE
    )
    group = models.ForeignKey(
        Group, 
        related_name='memberships', 
        on_delete=models.CASCADE
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'group')

    def __str__(self):
        return f"{self.user} in {self.group}"