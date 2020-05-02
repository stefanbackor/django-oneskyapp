# -*- coding: utf-8 -*-

import hashlib
import os
import time

import polib
import requests
from django.core import management

from ...app_settings import (
    ONESKY_LANGUAGES, ONESKY_LOCALE_PATHS, ONESKY_API_KEY, ONESKY_API_SECRET,
    ONESKY_PROJECTS, ONESKY_MAKEMESSAGES_COMMAND,
    ONESKY_COMPILEMESSAGES_COMMAND
)


def run_makemessages(verbosity=0):
    # TODO: allow passing arguments to makemessages -
    #  obsolete, location, domain atc.
    if isinstance(ONESKY_LANGUAGES, (list, tuple)):
        language_codes = [
            language_item[0] for language_item in ONESKY_LANGUAGES
        ]
        management.call_command(
            ONESKY_MAKEMESSAGES_COMMAND,
            locale=language_codes,
            symlinks=True,
            verbosity=verbosity
        )
    else:
        print("Missing settings.LANGUAGES")


def run_compilemessages(verbosity=0):
    if isinstance(ONESKY_LANGUAGES, (list, tuple)):
        language_codes = [
            language_item[0] for language_item in ONESKY_LANGUAGES
        ]
        management.call_command(
            ONESKY_COMPILEMESSAGES_COMMAND,
            locale=language_codes,
            verbosity=verbosity
        )
    else:
        management.call_command(
            ONESKY_COMPILEMESSAGES_COMMAND, verbosity=verbosity
        )


"""

    OneSky's simple python wrapper

    Known WTF?:
    - If you manualy create project file (e.g. django.po) inside SkyOne app, API will return 400 error "This file is not downloadable through API"
    - Always upload at least your default django.po language file for each project. 

"""


class OneSkyApiClient(object):
    def __init__(self, api_key, api_secret, locale_path='.'):
        self.api_key = api_key
        self.api_secret = api_secret
        self.locale_path = locale_path
        pass

    def json_request(
        self, method="get", api_path=None, api_params=None, file_stream=None
    ):
        url = 'https://platform.api.onesky.io/1/' + api_path
        url_params = {}
        if isinstance(api_params, dict):
            url_params = dict(
                [(k, v) for k, v in api_params.items() if v is not None]
            )

        timestamp = str(int(time.time()))
        auth_hash = hashlib.md5()
        auth_hash.update(timestamp.encode('utf-8'))
        auth_hash.update(self.api_secret.encode('utf-8'))
        url_params["dev_hash"] = auth_hash.hexdigest()
        url_params["timestamp"] = timestamp
        url_params["api_key"] = self.api_key

        if method.lower() == "get":
            response = requests.get(url, params=url_params)
        elif method.lower() == "post":
            file_name = url_params["file_name"]
            del url_params["file_name"]
            response = requests.post(
                url,
                params=url_params,
                files={"file": (file_name, file_stream)}
                if file_stream else None
            )

        if response.headers.get('content-disposition', '') \
            .startswith('attachment;'):
            filename = response.headers['content-disposition'].split('=')[1]
            dest_filename = os.path.join(self.locale_path, filename)
            try:
                os.makedirs(os.path.dirname(dest_filename))
            except OSError as e:
                # Ok if path exists
                pass
            with open(dest_filename, 'wb') as f:
                for chunk in response.iter_content():
                    f.write(chunk)
            response_output = {'filename': dest_filename}
        else:
            try:
                response_output = response.json()
            except ValueError:
                response_output = {}

        return response.status_code, response_output

    def json_get_request(self, *args, **kwargs):
        return self.json_request(method="get", *args, **kwargs)

    def json_post_request(self, *args, **kwargs):
        return self.json_request(method="post", *args, **kwargs)

    def project_languages(self, project_id):
        return self.json_get_request(
            api_path="projects/%s/languages" % project_id
        )

    def file_list(self, project_id, page=1):
        return self.json_get_request(
            api_path="projects/%s/files" % project_id,
            api_params={"page": page}
        )

    def file_upload(
        self, project_id, file_name, file_format="GNU_PO", locale=None,
        is_keeping_all_strings=None
    ):
        with open(file_name, 'rb') as file_stream:
            return self.json_post_request(
                api_path="projects/%s/files" % project_id,
                file_stream=file_stream,
                api_params={
                    "file_name": os.path.basename(file_name),
                    "file_format": file_format,
                    "locale": locale,
                    "is_keeping_all_strings": is_keeping_all_strings
                }
            )

    def translation_export(
        self, project_id, locale, source_file_name, export_file_name
    ):
        return self.json_get_request(
            api_path="projects/%s/translations" % project_id,
            api_params={
                "locale": locale,
                "source_file_name": source_file_name,
                "export_file_name": export_file_name
            }
        )


class OneSkyApiClientException(Exception):
    pass


class Command(management.base.BaseCommand):
    help = "Updates your .po translation files using makemessages and " \
           "uploads them to OneSky translation service. " \
           "Pushes new translation strings from OneSky to your django app " \
           "and compiles messages."

    def handle(self, *args, **options):
        try:
            # Locale path and necessary settings
            if (ONESKY_LOCALE_PATHS and
                isinstance(ONESKY_LOCALE_PATHS, (list, tuple))):
                locale_path = ONESKY_LOCALE_PATHS[0]
            elif ONESKY_LOCALE_PATHS:
                locale_path = ONESKY_LOCALE_PATHS
            else:
                locale_path = None

            if not locale_path:
                raise OneSkyApiClientException(
                    "LOCALE_PATHS not configured properly. "
                    "Set your path to locale dir in settings.py as string"
                )
            if not ONESKY_API_KEY or not ONESKY_API_SECRET:
                raise OneSkyApiClientException(
                    "ONESKY_API_KEY or ONESKY_API_SECRET "
                    "not configured properly. Please include your OneSky key "
                    "and secret in settings.py as string"
                )
            if not ONESKY_PROJECTS or not isinstance(ONESKY_PROJECTS, list):
                raise OneSkyApiClientException(
                    "ONESKY_PROJECTS not configured properly. "
                    "Use list of OneSky project ids.")

            print("Using locale path: %s" % locale_path)

            # Init API client
            client = OneSkyApiClient(
                api_key=ONESKY_API_KEY,
                api_secret=ONESKY_API_SECRET,
                locale_path=locale_path
            )

            """
                PULL
            """
            # For each OneSky project..
            for project_id in ONESKY_PROJECTS:

                # Get languages
                status, json_response = client.project_languages(project_id)
                if status != 200:
                    print(OneSkyApiClientException(
                        "Unable to retrieve project languages for #%s. "
                        "OneSky API status: %s, OneSky API message: %s" % (
                            project_id,
                            status,
                            json_response.get("meta", {}).get("message", "")
                        )
                    ))
                project_languages = json_response.get("data", [])

                # Get files
                file_names = []
                page = 1
                while page:
                    status, json_response = client.file_list(
                        project_id, page=page
                    )
                    if status != 200:
                        print(OneSkyApiClientException(
                            "Unable to retrieve file list for #%s. "
                            "OneSky API status: %s, OneSky API message: %s" % (
                                project_id,
                                status,
                                json_response.get("meta", {})
                                    .get("message", "")
                            )
                        ))
                    page = json_response.get("meta", {}).get("next_page", None)
                    file_names.extend([
                        file.get("file_name")
                        for file in json_response.get("data", [])
                        if file.get("file_name").endswith(".po")
                    ])

                # Pull each translated file
                for file_name in file_names:
                    for language in project_languages:
                        export_file_name = os.path.join(
                            language.get("code", "unknown"),
                            "LC_MESSAGES",
                            file_name
                        )
                        if language.get("is_ready_to_publish", None):
                            status, json_response = client.translation_export(
                                project_id,
                                locale=language.get("code"),
                                source_file_name=file_name,
                                export_file_name=export_file_name
                            )
                            if status == 200:
                                print("Saving translation file %s for #%s." % (
                                    json_response.get(
                                        "filename",
                                        "-No filename in OneSky response-"
                                    ),
                                    project_id
                                ))
                            elif status == 204:
                                print(OneSkyApiClientException(
                                    "Unable to download translation "
                                    "file %s for #%s. File has no content. "
                                    "OneSky API status: %s, "
                                    "OneSky API message: %s" % (
                                        export_file_name,
                                        project_id,
                                        status,
                                        json_response.get("meta", {})
                                            .get("message", "")
                                    )
                                ))
                            else:
                                print(OneSkyApiClientException(
                                    "Something went wrong with downloading "
                                    "translation file %s for #%s. "
                                    "OneSky API status: %s, "
                                    "OneSky API message: %s" % (
                                        export_file_name,
                                        project_id,
                                        status,
                                        json_response.get("meta", {})
                                            .get("message", "")
                                    )
                                ))
                        else:
                            print(OneSkyApiClientException(
                                "Unable to save translation file %s for #%s. "
                                "Mark it as ready to publish." % (
                                    export_file_name, project_id
                                )
                            ))
            """
                MAKE
            """
            run_makemessages(verbosity=1)

            """
                PUSH
            """
            for project_id in ONESKY_PROJECTS:
                for file_name in file_names:
                    if isinstance(ONESKY_LANGUAGES, (list, tuple)):
                        language_codes = [
                            language_item[0]
                            for language_item in ONESKY_LANGUAGES
                        ]
                        for language_code in language_codes:
                            # Push each local file
                            upload_file_name = os.path.join(
                                locale_path,
                                language_code,
                                "LC_MESSAGES",
                                file_name
                            )
                            if os.path.isfile(upload_file_name):
                                po_file = polib.pofile(upload_file_name)
                                fuzzy_entries = po_file.fuzzy_entries()
                                if fuzzy_entries:
                                    print(
                                        'Fuzzy translations: %s items' % len(
                                            fuzzy_entries
                                        )
                                    )

                                # Upload to OneSky
                                if upload_file_name.endswith(".po"):
                                    print(
                                        "Uploading file: %s" % upload_file_name
                                    )
                                    # TODO: pass is_keeping_all_strings in command cli call
                                    client.file_upload(
                                        project_id,
                                        upload_file_name,
                                        file_format="GNU_PO",
                                        locale=language_code,
                                        is_keeping_all_strings=False
                                    )
            """
                COMPILE
            """
            run_compilemessages(verbosity=1)

        except OneSkyApiClientException as e:
            print(e)
