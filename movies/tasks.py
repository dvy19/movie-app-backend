
from celery import shared_task
from movies.services.categorization_service import categorize_post


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30
)
def categorize_post_task(self, post_id):

    try:
        return categorize_post(post_id)

    except Exception as exc:
        raise self.retry(exc=exc)


# docker exec -it movie-redis redis-cli ping
# docker start movie-redis
# docker stop movie-redis
# docker ps -a