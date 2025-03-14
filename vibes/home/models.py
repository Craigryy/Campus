from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from django.http import HttpResponse


class HomePage(RoutablePageMixin, Page):
    """A homepage displaying various content like videos and images."""

    intro = RichTextField(blank=True, help_text="Short introduction.")
    description = RichTextField(blank=True, help_text="Description of the content.")

    content = StreamField([
        ("video", blocks.StructBlock([
            ("title", blocks.CharBlock(required=True, help_text="Title of the video")),
            ("description", blocks.TextBlock(required=False, help_text="Short description of the video")),
            ("file", DocumentChooserBlock(help_text="Upload a video file")),
            ("icon", ImageChooserBlock(required=False, help_text="Optional custom icon for the video"))
        ], icon="media", label="Video")),

        ("image", blocks.StructBlock([
            ("title", blocks.CharBlock(required=True, help_text="Title of the image")),
            ("description", blocks.TextBlock(required=False, help_text="Short description of the image")),
            ("image", ImageChooserBlock(icon="image", label="Image"))
        ], icon="image", label="Image")),
    ], use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("description"),
        FieldPanel("content"),
    ]

    class Meta:
        verbose_name = "Home Page"

    @route(r'^events/$')
    def upcoming_events(self, request):
        return HttpResponse("Upcoming events page")

    @route(r'^videos/$')
    def video_content(self, request):
        return HttpResponse("Video content page")

class UpcomingEvent(models.Model):
    """Model for upcoming events."""
    title = models.CharField(max_length=255, help_text="Title of the event")
    description = models.TextField(help_text="Description of the event")
    read_more_url = models.URLField(blank=True, null=True, help_text="Optional URL for more details")

    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("read_more_url"),
    ]

    class Meta:
        verbose_name = "Upcoming Event"
        verbose_name_plural = "Upcoming Events"

    def __str__(self):
        return self.title
