"""
Send deflate logs returns "Request accepted for processing (always 202 empty JSON)." response
"""
from dotenv import load_dotenv
load_dotenv()

from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.logs_api import LogsApi
from datadog_api_client.v2.model.content_encoding import ContentEncoding
from datadog_api_client.v2.model.http_log import HTTPLog
from datadog_api_client.v2.model.http_log_item import HTTPLogItem


def send_log(message, status):
    body = HTTPLog(
        [
            HTTPLogItem(
                ddsource="jarvis",
                ddtags="env:jarvis,version:1.0",
                hostname="jarvis",
                message=message,
                service="jarvis",
                status=status,
            ),
        ]
    )

    configuration = Configuration()
    with ApiClient(configuration) as api_client:
        api_instance = LogsApi(api_client)
        response = api_instance.submit_log(content_encoding=ContentEncoding.DEFLATE, body=body)

        print(response)
