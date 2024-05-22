from typing import List,Optional
from pydantic import BaseModel

class User(BaseModel):
    id: str
    username:str
    
class FormResponse(BaseModel):
    affected_products:str
    severity:str
    suspected_owning_team:List[str]
    start_time:str
    p1_customer_affected:Optional[bool]=False
    suspected_affected_components:str
    description:str
    message_for_sp:Optional[str]=None
    flags_for_statuspage_notification:List[str]
    
class SlackFormSubmission(BaseModel):
    type:str
    user:User
    form_response:FormResponse