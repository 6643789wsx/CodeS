Django-annoying
-----------

[![Code Shelter](https://www.codeshelter.co/static/badges/badge-flat.svg)](https://www.codeshelter.co/)

This django application eliminates certain annoyances in the Django
framework.

### Features

-   render_to decorator - Reduce typing in django views.
-   signals decorator - Allow using signals as decorators.
-   ajax_request decorator - Returns JsonResponse with dict as content.
-   autostrip decorator - Strip form text fields before validation
-   get_object_or_None function - Similar to get_object_or_404, but returns None if the object is not found.
-   AutoOneToOne field - Creates a related object on first call if it doesn't exist yet.
-   JSONField - A field that stores a Python object as JSON and retrieves it as a Python object.
-   get_config function - Get settings from django.conf if exists, return a default value otherwise.
-   StaticServer middleware - Instead of configuring urls.py, just add
    this middleware and it will serve your static files when you are in
    debug mode.
-   get_ object_or_this_function - Similar to get_object_or_404, but returns a default object (`this`) if the object is not found.
-   HttpResponseReload - Reload and stay on same page from where the request
    was made.