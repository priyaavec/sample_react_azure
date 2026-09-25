from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ItemOut(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    title: str

    description: str | None = None

    blob_name: str | None = None

    original_filename: str | None = None

    content_type: str | None = None

    created_at: datetime
