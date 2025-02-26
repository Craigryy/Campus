"""Added due to using wagtail """
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


@hooks.register("register_admin_menu_item")
def register_core_menu():
    return MenuItem(
        _("Core"),
        reverse("admin:core_user_changelist"),
        icon_name="user",
        order=600)
