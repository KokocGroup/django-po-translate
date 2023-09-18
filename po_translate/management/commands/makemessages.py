import os
import re

import pkg_resources
import polib
from django.conf import settings
from django.core.management.commands import makemessages

# from googletrans import Translator


class Command(makemessages.Command):
    """
        python manage.py make_messages -l en -d djangojs --ignore=*.build.js
    """

    msgmerge_options = ["-q", "--backup=none", "--previous", "--update", "--no-fuzzy-matching", "--no-location"]

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--no-clear-fuzzy',
            dest='no_clear_fuzzy',
            help='Leaves the translation flagged as fuzzy',
            action='store_true'
        )

        parser.add_argument(
            "--no-translate",
            dest="no_translate",
            help="Don't add automatic translation",
            action="store_true"
        )

    def valid_translator_version(self):
        error_message = 'Need googletrans 3.1.0a0 version.' \
                        ' Please, install googletrans command "pip install googletrans==3.1.0a0"'
        valid_versions = ['3.1.0a0', '4.0.0rc1']
        try:
            package = pkg_resources.get_distribution("googletrans")
        except pkg_resources.DistributionNotFound:
            raise ValueError(error_message)

        if package and package.version not in valid_versions:
            raise ValueError(error_message)
        return True

    def handle(self, *args, **options):
        no_clear_fuzzy = options.pop('no_clear_fuzzy')
        no_translate = options.pop('no_translate')
        selected_locale = options.get('locale')
        res = super().handle(*args, **options)

        for locale in selected_locale:
            paths = []
            for path in settings.LOCALE_PATHS:
                paths.append(os.path.join(path, f'{locale}/LC_MESSAGES/django.po'))

        for path in paths:
            po = polib.pofile(path)

            # убираем fuzzy
            if not no_clear_fuzzy:
                for entry in po.fuzzy_entries():
                    entry.flags.remove('fuzzy')
                po.save()

            # добавляем перевод
            if not no_translate:
                if self.valid_translator_version():
                    from googletrans import Translator

                translator = Translator()
                untranslated_list = [entry.msgid for entry in po.untranslated_entries()]
                translated_list = translator.translate(untranslated_list, dest=locale)

                for entry, translated in zip(po.untranslated_entries(), translated_list):
                    variables_msgid = re.findall(r'\{\{?[%\s\S]*?\}\}?|\%\([^\)]*\)[ds]?', entry.msgid)

                    if not variables_msgid:
                        entry.msgstr = translated.text
                    else:
                        variables_msgstr = re.findall(r'\{\{?[%\s\S]*?\}\}?|\%\([^\)]*\)[ds]?', translated.text)

                        for var_msgstr, var_msgid in zip(variables_msgstr, variables_msgid):
                            translated.text = translated.text.replace(var_msgstr, var_msgid)
                            entry.msgstr = translated.text

                po.save()

        return res
