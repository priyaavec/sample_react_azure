import os
import uuid

from azure.storage.blob import (
    BlobServiceClient,
    ContentSettings
)


CONTAINER_NAME = os.getenv(
    "AZURE_STORAGE_CONTAINER",
    "crud-files"
)


def get_blob_service():

    connection_string = os.getenv(
        "AZURE_STORAGE_CONNECTION_STRING"
    )

    if not connection_string:

        raise RuntimeError(
            "AZURE_STORAGE_CONNECTION_STRING is missing"
        )

    return BlobServiceClient.from_connection_string(
        connection_string
    )


def get_container():

    service = get_blob_service()

    container = service.get_container_client(
        CONTAINER_NAME
    )

    try:
        container.create_container()

    except Exception:
        pass

    return container


def upload_file(
    data: bytes,
    filename: str,
    content_type: str | None
):

    extension = os.path.splitext(filename)[1]

    blob_name = (
        f"{uuid.uuid4()}{extension}"
    )

    blob = get_container().get_blob_client(
        blob_name
    )

    blob.upload_blob(
        data,
        overwrite=True,
        content_settings=ContentSettings(
            content_type=content_type
        )
    )

    return blob_name


def download_file(blob_name: str):

    blob = get_container().get_blob_client(
        blob_name
    )

    return blob.download_blob().readall()


def delete_file(blob_name: str):

    blob = get_container().get_blob_client(
        blob_name
    )

    blob.delete_blob(
        delete_snapshots="include"
    )
