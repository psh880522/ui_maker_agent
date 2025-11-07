import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from src.schema import UINode  # 2.1에서 정의한 스키마 임포트

def create_ui_file_from_image(image_path: str) -> str:
    """
    이미지 시안을 분석하여 .ui 파일 내용을 생성합니다.
    """
    # .env 파일 로드
    load_dotenv()
    
    # 1. 클라이언트 초기화 (환경 변수에서 API 키 읽기)
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_AI_API_KEY가 .env 파일 또는 환경 변수에 설정되지 않았습니다.")
    
    client = genai.Client(api_key=api_key)

    # 2. 이미지 로드
    img = Image.open(image_path)
    
    # 3. 모델 프롬프트 및 구성 설정
    system_instruction = (
        "당신은 게임 UI/UX 전문가이자 Lua UI 파일 생성 에이전트입니다. "
        "UI 구성 데이터를 JSON 형태로 생성하는 전문가입니다. "
        "이미지의 UI 요소들(배경, 버튼, 텍스트, 아이콘 등)을 정확히 식별하고 좌표와 크기를 측정하여 "
        "UILoader.lua가 이해할 수 있는 형식으로 변환해야 합니다."
    )

    # JSON 스키마 예시를 텍스트로 제공 (UILoader 샘플 기반)
    json_example = '''
    {
        "type": "CCTouchNode",
        "x": 0.0,
        "y": 0.0,
        "isRelativeSize": false,
        "width": 950.0,
        "height": 440.0,
        "scaleX": 1.0,
        "scaleY": 1.0,
        "skewX": 0.0,
        "skewY": 0.0,
        "rotation": 0.0,
        "visible": true,
        "anchorpoint": [0.5, 0.5],
        "dockPoint": [0.5, 0.5],
        "var": "",
        "children": [
            {
                "type": "CCScale9Sprite",
                "x": 0.0,
                "y": 0.0,
                "width": 948.0,
                "height": 440.0,
                "anchorpoint": [0.0, 0.0],
                "dockPoint": [0.0, 0.0],
                "filename": "frame_popup_bg.png",
                "centerRect": [10, 10, 10, 10],
                "stretch": true,
                "color": [255, 255, 255],
                "opacity": 255.0,
                "var": "background"
            },
            {
                "type": "CCButton",
                "x": 400.0,
                "y": 380.0,
                "width": 60.0,
                "height": 60.0,
                "anchorpoint": [0.5, 0.5],
                "dockPoint": [1.0, 1.0],
                "normalFilename": "btn_close.png",
                "selectedFilename": "",
                "disabledFilename": "",
                "enabled": true,
                "var": "btnClose"
            },
            {
                "type": "CCStylishLabelTTF",
                "x": 200.0,
                "y": 350.0,
                "width": 400.0,
                "height": 40.0,
                "anchorpoint": [0.0, 0.0],
                "dockPoint": [0.5, 1.0],
                "text": "제목",
                "fontName": "Custom",
                "fontSize": 24,
                "alignment": 1,
                "color": [255, 255, 255],
                "hasStroke": true,
                "strokeTickness": 2.0,
                "strokeColor": [0, 0, 0],
                "var": "titleLabel"
            }
        ]
    }
    '''
    
    # Gemini 요청 (Vision)
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp', # Vision을 지원하는 모델
        contents=[
            system_instruction,
            f"""이 UI 시안 이미지를 분석하여 다음 규칙에 따라 JSON 형식으로 변환해주세요:

1. **노드 타입 식별**:
   - 배경 이미지: CCSprite 또는 CCScale9Sprite (늘어나야 하는 경우)
   - 버튼: CCButton (normalFilename, selectedFilename, disabledFilename 필요)
   - 텍스트: CCStylishLabelTTF
   - 컨테이너: CCTouchNode

2. **좌표 시스템**: 
   - 좌하단이 (0,0) 기준
   - 모든 좌표는 픽셀 단위로 정확히 측정
   - 중심점 기준으로 배치

3. **필수 속성** (모든 노드에 반드시 포함):
   - 기본: type, x, y, width, height, scaleX, scaleY, skewX, skewY, rotation, visible
   - 배치: anchorpoint, dockPoint (모든 노드 필수!)
   - 식별: var
   - 이미지 관련: filename (확장자 .png 포함)
   - 텍스트: text, fontName, fontSize, alignment, color
   - 버튼: enabled, normalFilename

4. **예시 JSON 형식**:
{json_example}

**중요**: 
- 응답은 반드시 유효한 JSON 형식이어야 하며, 마크다운 코드 블록으로 감싸주세요
- **모든 노드에 dockPoint 속성을 반드시 포함하세요** (UILoader.lua 필수!)
- 다른 설명 텍스트는 포함하지 마세요""",
            img  # 이미지를 contents 배열에 직접 포함
        ]
    )
    
    # 4. JSON 응답을 Lua 파일 형식으로 변환
    # 이 단계에서는 JSON 문자열을 파싱하고, Lua 테이블 문자열로 변환하는 로직이 필요합니다.
    # (주의: Gemini는 JSON을 생성하며, 이 JSON을 Lua로 변환하는 로직은 Python에서 구현해야 합니다.)

    json_data = response.text
    # json_to_lua_converter(json_data) 함수가 필요함
    # 예시를 위해 단순 반환
    return json_data