from pydantic import BaseModel, Field


class Email(BaseModel):
    title: str = Field(..., description="邮件标题")
    recipient: str = Field(..., description="收件人")
    text: str = Field(..., description="邮件内容，如果用户没有提供，则根据用户意图自动生成，**不要使用结束语和署名**")
# 地理位置类
class Location(BaseModel):
    latitude: float = Field(..., description="纬度")
    longitude: float = Field(..., description="经度")