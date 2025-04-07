from django.db import models
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.fields import StreamField, RichTextField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtail.snippets.blocks import SnippetChooserBlock

from blogs.utils.paginate import paginate_item
from blogs.models import BlogCategory,BlogPage,BlogPageTag

class HomePage(RoutablePageMixin, Page):
    """
    A homepage model displaying various types of content such as videos and images.
    """
    max_count = 1
    intro = RichTextField(blank=True, help_text="Short introduction.")
    description = RichTextField(blank=True, help_text="Description of the content.")


    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("description"),
    ]

    class Meta:
        verbose_name = "Home Page"

    def get_context(self, request):
        # Check if the 'featured' query parameter is present
        is_featured = request.GET.get('featured', 'false').lower() == 'true'

        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        all_posts = self.get_children().live().order_by('-first_published_at')


        # Filter only featured blog posts if 'featured=true' is in the URL
        if is_featured:
            # Get all child pages and filter those that are instances of BlogPage
            b_posts = self.get_children().live().type(BlogPage).order_by('-first_published_at')

            # Filter the posts by the 'featured' field in BlogPage
            all_posts = b_posts.filter(blogpage__featured=True)
            context['is_featured'] = is_featured

        posts = paginate_item(request, all_posts, 10)

        categories = BlogCategory.objects.all()
        context['blogpages'] = posts
        context['categories'] = categories

        return context

    # reference:
    # https://docs.wagtail.io/en/v2.13.2/reference/contrib/routablepage.html#module-wagtail.contrib.routable_page
    @route(r"^category/(?P<cat_slug>[-\w]*)/$", name="category_view")
    def category_view(self, request, cat_slug):
        """Find blog posts based on a category."""

        try:
            # Look for the blog category by its slug.
            category = BlogCategory.objects.get(name=cat_slug)
        except Exception:
            # Blog category doesnt exist (ie /blog/category/missing-category/)
            # Redirect to self.url, return a 404.. that's up to you!
            category = None

        if category is None:
            # This is an additional check.
            # If the category is None, do something. Maybe default to a particular category.
            # Or redirect the user to /blog/ ¯\_(ツ)_/¯
            pass

        posts = BlogPage.objects.live().public().filter(categories__in=[category])
        blog_pages = paginate_item(request, posts, 10)


        # Note: The below template (latest_posts.html) will need to be adjusted
        return self.render(
            request,
            context_overrides={
                'title': cat_slug,
                'posts': blog_pages,
                'categories' : BlogCategory.objects.all()
            },
            template="blog/blog_cat_index_page.html",
        )
class Event(RoutablePageMixin,Page):
    """Event page"""

