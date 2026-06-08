from pydantic import BaseModel


class PoemPayload(BaseModel):
    id: str
    title: str
    author: str
    dynasty: str
    content: list[str]   # 每行诗句

    def full_text(self) -> str:
        return f"{self.title} {self.author} {''.join(self.content)}"


class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    dynasties: list[str] = []  # 空列表 = 不过滤


class PoemResult(BaseModel):
    id: str
    title: str
    author: str
    dynasty: str
    content: list[str]
    score: float


class SearchResponse(BaseModel):
    results: list[PoemResult]
    query: str
