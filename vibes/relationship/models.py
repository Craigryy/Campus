from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, StreamField
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from blogs.utils.paginate import paginate_item


class Relationship(Page):
    intro = RichTextField(blank=True)
    description = RichTextField(blank=True)
    featured = models.BooleanField(default=False)

    profile = StreamField([
        ("document", blocks.StructBlock([
            ("name", blocks.CharBlock(required=True, help_text="Title of the document")),
            ("bio", blocks.TextBlock(required=False, help_text="Short description of the document")),
            ("icon", ImageChooserBlock(required=False, help_text="Optional custom icon for the document"))
        ], icon="doc-full", label="Document")),
    ], use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('description'),  
        FieldPanel('profile'),
    ]

    class Meta:
        verbose_name = "Profile"

    def get_context(self, request):
        """Add pagination to the profiles using the existing paginate_item utility."""
        is_featured = request.GET.get('featured', 'false').lower() == 'true'
        context = super().get_context(request)
        all_profiles = self.get_children().live().order_by("-first_published_at")

        if is_featured:
            all_profiles = self.get_children().live().type(Relationship).filter(relationship__featured=True).order_by("-first_published_at")
            context["is_featured"] = True

        context["paginated_resources"] = paginate_item(request, all_profiles, 10)
        return context
