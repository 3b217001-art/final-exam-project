from pydantic import BaseModel, ConfigDict


class PostCreate(BaseModel):
    """用於 POST 新增與 PUT 完整更新"""

    text: str
    author: str
    tags: str

class PostResponse(PostCreate):
    """API 回傳的名言格式，包含 id"""

    id: int

    model_config = ConfigDict(from_attributes=True)