from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class UINode(BaseModel):
    # UILoader.lua에 기반한 모든 속성 정의
    type: str = Field(..., description="CCTouchNode, CCSprite, CCButton, CCLayerColor 등 노드 타입")
    x: float = Field(..., description="x 좌표")
    y: float = Field(..., description="y 좌표")
    
    # 크기 관련
    width: Optional[float] = Field(default=None, description="너비")
    height: Optional[float] = Field(default=None, description="높이")
    isRelativeSize: Optional[bool] = Field(default=False, description="상대 크기 사용 여부")
    relSize: Optional[List[float]] = Field(default=None, description="상대 크기 [x, y, width, height]")
    
    # 변형 관련
    scaleX: Optional[float] = Field(default=1.0, description="X축 스케일")
    scaleY: Optional[float] = Field(default=1.0, description="Y축 스케일")
    skewX: Optional[float] = Field(default=0.0, description="X축 기울기")
    skewY: Optional[float] = Field(default=0.0, description="Y축 기울기")
    rotation: Optional[float] = Field(default=0.0, description="회전")
    visible: Optional[bool] = Field(default=True, description="표시 여부")
    
    # 앵커 및 도킹
    anchorpoint: Optional[List[float]] = Field(default=None, description="앵커 포인트 [x, y]")
    dockPoint: Optional[List[float]] = Field(default=None, description="도킹 포인트 [x, y]")
    
    # 색상 및 투명도
    color: Optional[List[int]] = Field(default=None, description="색상 [r, g, b]")
    opacity: Optional[float] = Field(default=255.0, description="불투명도")
    blendFunc: Optional[List[int]] = Field(default=None, description="블렌드 함수 [src, dst]")
    
    # 노드 변수명
    var: str = Field(default="", description="노드에 할당할 변수명")
    
    # 파일명 (스프라이트, 버튼 등)
    filename: Optional[str] = Field(default=None, description="이미지 파일 경로")
    normalFilename: Optional[str] = Field(default=None, description="버튼 기본 상태 파일명")
    selectedFilename: Optional[str] = Field(default="", description="버튼 선택 상태 파일명")
    disabledFilename: Optional[str] = Field(default="", description="버튼 비활성 상태 파일명")
    
    # 버튼 관련
    enabled: Optional[bool] = Field(default=True, description="활성화 여부")
    
    # 텍스트 관련
    text: Optional[str] = Field(default="", description="텍스트 내용")
    fontName: Optional[str] = Field(default="Custom", description="폰트명")
    fontSize: Optional[int] = Field(default=12, description="폰트 크기")
    alignment: Optional[int] = Field(default=1, description="정렬 (0=왼쪽, 1=중앙, 2=오른쪽)")
    hasStroke: Optional[bool] = Field(default=False, description="외곽선 사용 여부")
    strokeTickness: Optional[float] = Field(default=0.0, description="외곽선 두께")
    strokeColor: Optional[List[int]] = Field(default=None, description="외곽선 색상 [r, g, b]")
    
    # Scale9Sprite 관련
    centerRect: Optional[List[int]] = Field(default=None, description="중앙 영역 [x, y, w, h]")
    stretch: Optional[bool] = Field(default=True, description="늘리기 여부")
    
    # 하위 노드
    children: List[Dict[str, Any]] = Field(default_factory=list, description="하위 노드 리스트")