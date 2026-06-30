from pydantic import BaseModel, Field

class VisitorSession(BaseModel):
    # --- Variables Numériques Comportementales ---
    Administrative: int = Field(..., description="Number of administrative pages visited", ge=0)
    Administrative_Duration: float = Field(..., description="Total time spent on administrative pages", ge=0.0)
    Informational: int = Field(..., description="Number of informational pages visited", ge=0)
    Informational_Duration: float = Field(..., description="Total time spent on informational pages", ge=0.0)
    ProductRelated: int = Field(..., description="Number of product-related pages visited", ge=0)
    ProductRelated_Duration: float = Field(..., description="Total time spent on product pages", ge=0.0)
    BounceRates: float = Field(..., description="Average bounce rate of pages visited", ge=0.0, le=1.0)
    ExitRates: float = Field(..., description="Average exit rate of pages visited", ge=0.0, le=1.0)
    PageValues: float = Field(..., description="Average page value metric for this session", ge=0.0)
    SpecialDay: float = Field(..., description="Closeness of site date to a special day/holiday", ge=0.0, le=1.0)
    
    # --- Variables Catégorielles / Variables à Encoder ---
    Month: str = Field(..., description="Month name as string (e.g., 'May', 'Nov', 'Mar')")  # Corrigé en str
    OperatingSystems: int = Field(..., description="Identifier for visitor operating system")
    Browser: int = Field(..., description="Identifier for visitor web browser")
    Region: int = Field(..., description="Geographical region index")
    TrafficType: int = Field(..., description="Web traffic source type code")
    VisitorType: str = Field(..., description="Visitor status text ('Returning_Visitor', 'New_Visitor', 'Other')")  # Corrigé en str
    Weekend: bool = Field(..., description="Is the session on a weekend? (True/False)")  # Aligné avec le type natif du dataset

class PredictionResponse(BaseModel):
    purchase_probability: float = Field(..., description="The probability percentage of completing a purchase")
    will_buy: bool = Field(..., description="Binary classification prediction outcome")
    confidence_level: str = Field(..., description="Qualitative evaluation of prediction strength")
    recommended_action: str = Field(..., description="Automated business recommendation for the merchant")
    trigger_code: str = Field(..., description="Code representing the specific action to be taken by the client site")