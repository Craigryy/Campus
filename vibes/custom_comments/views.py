from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from blog.models import BlogPage
from custom_comments import get_model, get_form

def post_comment(request, page_id):
    # Fetch the BlogPage instance
    page = get_object_or_404(BlogPage, id=page_id)

    # Get the custom form (without passing target_object directly)
    CommentForm = get_form()

    if request.method == 'POST':
        # Initialize the form with request.POST data
        # form = CommentForm(request.POST, target_object=page)

        form = CommentForm(page, data=request.POST)

        # Handle AJAX requests
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if form.is_valid():
                # Get the comment model dynamically
                Comment = get_model()

                # Save the comment
                comment = Comment(
                    user_name=form.cleaned_data['name'],
                    comment=form.cleaned_data['comment'],
                    email=form.cleaned_data['email'],
                    # Get the content type of the BlogPage model
                    content_type=ContentType.objects.get_for_model(page),
                    object_pk=page.pk,  # Relating the comment to the blog post
                    site_id=getattr(settings, 'SITE_ID', 1),
                    submit_date=timezone.now(),
                )
                comment.save()

                # Return a success response
                return JsonResponse({
                    'success': True,
                    'message': 'Comment submitted successfully!',
                    'comment': {
                        'user_name': comment.user_name,
                        'comment': comment.comment,
                        'submit_date': comment.submit_date.strftime('%Y-%m-%d %H:%M:%S')
                    }
                })
            else:
                # Return form errors as JSON response
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)

    # Fallback in case it's not an AJAX request
    return JsonResponse({'error': 'Invalid request'}, status=400)
