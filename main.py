# -*- coding: utf-8 -*-
import argparse
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from src.agent import create_ui_file_from_image
from src.converter import json_to_lua_string

def setup_environment():
    """환경 변수 및 설정 검증"""
    # .env 파일 로드
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key:
        print("❌ 오류: GOOGLE_AI_API_KEY가 설정되지 않았습니다.")
        print("💡 설정 방법:")
        print("   1. .env 파일에 'GOOGLE_AI_API_KEY=your-api-key' 추가")
        print("   2. 또는 환경 변수로 설정: export GOOGLE_AI_API_KEY='your-api-key'")
        print("   3. .env.example 파일을 참고하세요")
        return False
    return True

def validate_image_file(image_path: str) -> bool:
    """이미지 파일 유효성 검증"""
    if not os.path.exists(image_path):
        print(f"❌ 오류: 이미지 파일을 찾을 수 없습니다: {image_path}")
        return False
    
    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')
    if not image_path.lower().endswith(valid_extensions):
        print(f"❌ 오류: 지원되지 않는 이미지 형식입니다. 지원 형식: {', '.join(valid_extensions)}")
        return False
    
    return True

def generate_ui_file(image_path: str, output_path: str = None, verbose: bool = False):
    """UI 파일 생성 메인 로직"""
    
    # 1. 환경 검증
    if not setup_environment():
        return False
    
    # 2. 이미지 파일 검증
    if not validate_image_file(image_path):
        return False
    
    # 3. 출력 파일 경로 설정
    if not output_path:
        image_name = Path(image_path).stem
        output_path = f"{image_name}_generated.ui"
    
    try:
        if verbose:
            print(f"🔍 이미지 분석 중: {image_path}")
        
        # 4. AI로 이미지 분석 및 JSON 생성
        json_result = create_ui_file_from_image(image_path)
        
        if verbose:
            print("📋 JSON 데이터 생성 완료")
            print(f"📄 전체 응답:\n{json_result}")
        
        # JSON 응답에서 실제 JSON 부분만 추출 (마크다운 코드 블록 제거)
        json_content = json_result.strip()
        if json_content.startswith('```json'):
            json_content = json_content[7:]  # ```json 제거
        if json_content.endswith('```'):
            json_content = json_content[:-3]  # ``` 제거
        json_content = json_content.strip()
        
        if verbose:
            print(f"📄 정제된 JSON:\n{json_content[:200]}...")
        
        # 5. JSON을 Lua 형식으로 변환
        
        lua_content = json_to_lua_string(json_content)
        
        # 6. 최종 .ui 파일 형태로 래핑 (UILoader.lua 호환)
        final_ui_content = f"""{lua_content};"""
        
        # 7. 파일 저장 (마지막에 개행 추가)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_ui_content + "\n")
        
        print(f"✅ UI 파일 생성 완료: {output_path}")
        
        # 8. 파일 정보 출력
        file_size = os.path.getsize(output_path)
        print(f"📊 파일 크기: {file_size} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False

def main():
    """메인 함수 - CLI 인터페이스"""
    parser = argparse.ArgumentParser(
        description="🎨 UI Maker Agent - 이미지 시안을 Lua UI 파일로 변환",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python main.py image.png                    # 기본 출력 파일명으로 생성
  python main.py image.png -o custom.ui       # 커스텀 출력 파일명 지정
  python main.py image.png -v                 # 자세한 출력으로 실행

환경 설정:
  1. .env 파일에 API 키 설정 (권장):
     GOOGLE_AI_API_KEY=your-google-ai-api-key
  
  2. 또는 환경 변수로 설정:
     Windows: set GOOGLE_AI_API_KEY=your-api-key
     Linux/Mac: export GOOGLE_AI_API_KEY=your-api-key
  
  3. .env.example 파일을 참고하여 .env 파일을 생성하세요.
        """
    )
    
    parser.add_argument(
        "image_path",
        help="분석할 UI 시안 이미지 파일 경로"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="출력할 .ui 파일 경로 (기본: {이미지명}_generated.ui)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="자세한 출력 모드"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="UI Maker Agent v0.1.0"
    )
    
    # 인수가 없을 때 도움말 표시
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    print("🚀 UI Maker Agent 시작")
    print(f"📁 입력 파일: {args.image_path}")
    
    # UI 파일 생성 실행
    success = generate_ui_file(
        image_path=args.image_path,
        output_path=args.output,
        verbose=args.verbose
    )
    
    if success:
        print("🎉 작업 완료!")
    else:
        print("💥 작업 실패!")
        sys.exit(1)

if __name__ == "__main__":
    main()
