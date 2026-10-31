from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    if created:
        post_owner = instance.post.user
        
        # Optional: Don't create a notification if users like their own post
        if post_owner != instance.user:
            Notification.objects.create(
                recipient=post_owner,
                sender=instance.user,
                post=instance.post,
                message=f"{instance.user.username} liked your post: '{instance.post.title}'"
            )