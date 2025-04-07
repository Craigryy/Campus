from wagtail.snippets.models import register_snippet
from . import get_model as get_comment_model

# Get the model returned by get_comment_model
Comment = get_comment_model()

# Dynamically register the Comment model as a snippet
register_snippet(Comment)
