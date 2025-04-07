from django.db import models
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField

from taggit.models import TaggedItemBase

# Add these:
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField, StreamField
from wagtail import blocks
from wagtail.snippets.models import register_snippet
from wagtail.search import index
from wagtail import hooks
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
)

from blogs.utils.paginate import paginate_item
from blogs.blocks import InlineImageBlock, InlineVideoBlock

from custom_comments import get_model, get_form


User = get_user_model()  # Gets the currently active User model


class BlogIndexPage(RoutablePageMixin, Page):
    intro = RichTextField(blank=True)

    # Specifies that only ArticlePage objects can live under this index page
    # https://www.pythoneatstail.com/en/overview-all-articles/adding-streamfield-wagtail-page/
    subpages_types = ['BlogPage']

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]

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


class BlogTagIndexPage(RoutablePageMixin, Page):

    def get_context(self, request):

        # Filter by tag
        tag = request.GET.get('tag')
        blogpages = BlogPage.objects.filter(tags__name=tag)

        posts = paginate_item(request, blogpages, 9)

        # Update template context
        context = super().get_context(request)
        context['blogpages'] = posts
        context['tag'] = tag
        return context


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )

# Individual blog
class BlogPage(RoutablePageMixin, Page):
    def get_absolute_url(self):
        return self.get_url()

    def main_image(self):
        blog_index_image = self.image
        if blog_index_image:
            return blog_index_image
        else:
            return None

    def get_streamfield_text(self):
        for block in self.body:
            if block.block_type == "paragraph":
                return block

    def get_categories(self):
        categories = BlogCategory.objects.all()
        return categories


    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Get the dynamic comment form using the `get_form` function from custom_comments
        CommentForm = get_form()
        context['comment_form'] = CommentForm(self)

        # Fetch any existing comments using the `get_model` function
        Comment = get_model()
        # Filter comments that are public and order them by submission date
        context['comment_list'] = Comment.objects.filter(
            object_pk=self.pk,
            is_public=True,
            is_removed=False
        ).order_by('submit_date')

        return context

    date = models.DateField("Post date")
    image = models.ForeignKey(
        'wagtailimages.Image', blank=True, null=True, on_delete=models.SET_NULL, related_name='+', verbose_name=_("Image")
    )

    featured = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=False)
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT, # Prevent deletion if the user is still referenced
        null=True,
        blank=True,
        related_name='blog_posts'
    )
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    categories = ParentalManyToManyField('blog.BlogCategory', blank=True)
    body = StreamField([
        ('heading', blocks.CharBlock(form_classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', InlineImageBlock()),
        ('video', InlineVideoBlock()),
    ], use_json_field=True)

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    # https://docs.wagtail.io/en/stable/topics/streamfield.html
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('tags'),
            FieldPanel('featured'),
            FieldPanel('allow_comments'),
            FieldPanel(
                'categories',
                widget=forms.CheckboxSelectMultiple
            ),
        ],
        heading="Blog information"),
        FieldPanel('author'),
        FieldPanel('body'),
        FieldPanel('image'),
        InlinePanel('gallery_images', label="Gallery images"),
    ]

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


@hooks.register('before_create_page')
def set_default_author(request, parent_page, page):
    if isinstance(page, BlogPage):
        page.author = request.user


class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
    ]


@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('icon'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'blog categories'


class AuthorPage(Page):
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name='author_page'
    )
    bio = StreamField([
        ('heading', blocks.CharBlock(form_classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', InlineImageBlock()),
        ('video', InlineVideoBlock()),
    ], use_json_field=True)
    profile_picture = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    location = models.CharField(max_length=255, null=True, blank=True, help_text="Author's location (e.g., Colorado, USA)")
    languages = models.CharField(max_length=255, null=True, blank=True, help_text="Comma-separated list of languages (e.g., English, Spanish)")

    content_panels = Page.content_panels + [
        FieldPanel('user'),
        FieldPanel('bio'),
        FieldPanel('profile_picture'),
        MultiFieldPanel([
            FieldPanel('location'),
            FieldPanel('languages'),
        ], heading="Author Details")
    ]

    def split_languages(self):
        """Return the languages as a list"""
        if self.languages:
            return [lang.strip() for lang in self.languages.split(',')]
        return []

    def get_context(self, request):
        context = super().get_context(request)

        # Filter for only fully published (live and with a published date) blog posts
        recent_blogs = (
            self.user.blog_posts.specific()
            .live()
            .public()  # Ensures only publicly accessible pages are included
            .type(BlogPage)
            .filter(first_published_at__isnull=False)  # Exclude pages without a publish date
            .order_by('-first_published_at')[:7]  # Order by published date and limit results
        )

        context['recent_blogs'] = recent_blogs
        context['author'] = self.user
        return context
