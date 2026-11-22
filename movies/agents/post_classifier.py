
import os
import json
from groq import Groq

from .prompts import POST_CATEGORIES, CLASSIFICATION_PROMPT


class PostClassifier:

    def __init__(self):
        self.client = Groq(
            api_key=os.environ.get("GROQ_API_KEY")
        )

    def classify(self, post_content):

        if not post_content or not post_content.strip():
            raise ValueError("Post content cannot be empty")

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": CLASSIFICATION_PROMPT
                },
                {
                    "role": "user",
                    "content": f"Classify this post:\n\n{post_content}"
                }
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        result = response.choices[0].message.content

        try:
            data = json.loads(result)
        except json.JSONDecodeError:
            raise ValueError("LLM returned invalid JSON")

        category = data.get("category")

        if category not in POST_CATEGORIES:
            raise ValueError(f"Invalid category returned: {category}")

        return category


''' sample test

python manage.py shell

from posts.agents.post_classifier import PostClassifier

classifier = PostClassifier()

category = classifier.classify(
    "I think Interstellar is one of the greatest science fiction movies ever made."
)

print(category)
'''