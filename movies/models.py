from django.db import models

# Create your models here.

class MoviePost(models.Model):

    user=models.ForeignKey("users.CustomUser" , on_delete=models.CASCADE , related_name="post")

    image=models.ImageField( upload_to='post/' , blank=True , null=True)

    title=models.CharField(max_length=30)

    content=models.CharField(max_length=200)

    category=models.CharField(max_length=30)

    def __str__(self):
        return {self.title}


class Comment(models.Model):
    post = models.ForeignKey(MoviePost, on_delete=models.CASCADE, related_name="comments")

    # The user who wrote the comment (NOT the post owner)
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.post.title}"


class Like(models.Model):
    post = models.ForeignKey(MoviePost, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensures a user can only like a specific post once
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user} liked {self.post.title}"

'''
related_name="comments" lets you easily access all comments for a post using post.comments.all().

related_name="likes" lets you fetch all likes for a post using post.likes.all() or count them using post.likes.count().
'''

'''

to find the person who liked or commented
commenter = comment.user 
liker = like.user

to find the post owner
comment.post.user
like.post.user

To see all comments/likes made by a specific user:

user_comments = customer_user.user_comments.all()
user_likes = customer_user.user_likes.all()
'''

'''
handle likes and comments count dynamically

total_likes = post.likes.count()
total_comments = post.comments.count()
'''