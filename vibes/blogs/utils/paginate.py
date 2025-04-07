from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger


class BlogPagination(object):
    def __call__(self, request, item, num):
        """Custom paginate"""

        # Paginate all posts by "num" per page
        # put this in settings
        paginator = Paginator(item, num)
        # Try to get the ?page=x value
        page = request.GET.get("page")
        try:
            # If the page exists and the ?page=x is an int
            page_items = paginator.page(page)
        except PageNotAnInteger:
            # If the ?page=x is not an int; show the first page
            page_items = paginator.page(1)
        except (EmptyPage, InvalidPage):
            # If the ?page=x is out of range (too high most likely)
            # Then return the last page
            page_items = paginator.page(paginator.num_pages)


        return page_items

paginate_item = BlogPagination()
