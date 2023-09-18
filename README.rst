===================
Django-po-translate
===================


Quick start
-----------

1. Add "po_translate" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...,
        "po_translate",
    ]
2. If you already have a makemessges command defined somewhere in your application, remove your command or specify the po_translate application on top of it like this::

    INSTALLED_APPS = [
        ...,
        "po_translate",
        "app"
    ]

3. Run the command as usual::

    python manage.py makemessages -l en -d django

If your .po file contains lines without translation, then the translation of the specified locale will be added to them

4.If you do not want translation to be added, run the command with the -no--translate switch::

    python manage.py makemessages -l en -d django --no-translate
