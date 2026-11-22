
from movies.models import MoviePost
from movies.agents.post_classifier import PostClassifier


def categorize_post(post_id):

    try:
        # Fetch post from database
        post = MoviePost.objects.get(id=post_id)

        # Combine title and content
        post_text = f"""
        Title: {post.title}

        Content: {post.content}
        """

        # Initialize classifier
        classifier = PostClassifier()

        # Get category from LLM
        category = classifier.classify(post_text)

        # Update category in database
        post.category = category
        post.save(update_fields=["category"])

        return {
            "success": True,
            "post_id": post.id,
            "category": category
        }

    except MoviePost.DoesNotExist:
        return {
            "success": False,
            "error": "Post not found"
        }

    except Exception as e:
        print("Categorization error:", str(e))

        raise
