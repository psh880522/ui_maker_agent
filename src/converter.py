import json
from typing import Dict, Any, List

class UILoaderConfig:
    """UILoader.lua 관련 설정 상수들"""
    
    # 정수로 표현되어야 하는 속성들
    INTEGER_PROPERTIES = {
        'color', 'strokeColor', 'blendFunc', 'fontSize', 'alignment', 
        'glowOpacity', 'glowColor', 'progressType', 'percentage', 
        'basePixel', 'startOpacity', 'endOpacity', 'centerRect'
    }
    
    # 소수점을 유지해야 하는 속성들  
    DECIMAL_PROPERTIES = {
        'x', 'y', 'width', 'height', 'scaleX', 'scaleY', 'skewX', 'skewY', 
        'rotation', 'opacity', 'anchorpoint', 'dockPoint', 'strokeTickness', 
        'glowTickness', 'relSize', 'imageX', 'imageY'
    }
    
    # 노드 타입별 기본 속성 순서
    PROPERTY_ORDER = [
        'type', 'x', 'y', 'isRelativeSize', 'relSize', 'width', 'height',
        'scaleX', 'scaleY', 'skewX', 'skewY', 'rotation', 'visible',
        'anchorpoint', 'dockPoint', 'var'
    ]
    
    # 공통 기본값
    BASE_DEFAULTS = {
        'x': 0.0, 'y': 0.0, 'isRelativeSize': False, 'width': 100.0, 'height': 100.0,
        'scaleX': 1.0, 'scaleY': 1.0, 'skewX': 0.0, 'skewY': 0.0, 'rotation': 0.0,
        'visible': True, 'anchorpoint': [0.0, 0.0], 'dockPoint': [0.0, 0.0], 'var': ''
    }


class UINodeDefaults:
    """노드 타입별 기본값 정의"""
    
    @staticmethod
    def get_sprite_defaults() -> Dict[str, Any]:
        return {
            'color': [255, 255, 255], 'opacity': 255.0, 'blendFunc': [1, 771],
            'flipX': False, 'flipY': False, 'filename': 'default.png'
        }
    
    @staticmethod  
    def get_button_defaults() -> Dict[str, Any]:
        return {
            'enabled': True, 'normalFilename': 'button.png', 'selectedFilename': '',
            'disabledFilename': '', 'imageX': 0.0, 'imageY': 0.0
        }
    
    @staticmethod
    def get_label_defaults() -> Dict[str, Any]:
        return {
            'color': [255, 255, 255], 'opacity': 255.0, 'fontName': 'Custom',
            'fontSize': 12, 'text': '', 'alignment': 1, 'hasStroke': False,
            'strokeTickness': 0.0, 'strokeColor': [0, 0, 0], 'hasBold': False,
            'hasGlow': False, 'glowTickness': 0.0, 'glowColor': [255, 255, 255],
            'glowOpacity': 255
        }
    
    @staticmethod
    def get_scale9_defaults() -> Dict[str, Any]:
        return {
            'color': [255, 255, 255], 'opacity': 255.0, 'blendFunc': [1, 771],
            'filename': 'default.png', 'centerRect': [10, 10, 10, 10], 'stretch': True
        }
    
    @staticmethod
    def get_layer_color_defaults() -> Dict[str, Any]:
        return {
            'color': [0, 0, 0], 'opacity': 160.0, 'blendFunc': [1, 771]
        }


class LuaFormatter:
    """Lua 형식 변환 유틸리티"""
    
    @staticmethod
    def format_value(value: Any, preserve_decimal: bool = False) -> str:
        """값을 Lua 형식으로 포맷"""
        if isinstance(value, str):
            return f"'{value}'"
        elif isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, (int, float)):
            return LuaFormatter._format_number(value, preserve_decimal)
        elif isinstance(value, list):
            items = [LuaFormatter.format_value(item, preserve_decimal) for item in value]
            return f"{{ {'; '.join(items)}; }}"
        elif isinstance(value, dict):
            items = [f"{k} = {LuaFormatter.format_value(v, preserve_decimal)}" for k, v in value.items()]
            return f"{{\n{'; '.join(items)}\n}}"
        return str(value)
    
    @staticmethod
    def _format_number(value: float, preserve_decimal: bool) -> str:
        """숫자를 Lua 형식으로 포맷"""
        if preserve_decimal:
            return f"{value:.6f}"
        elif isinstance(value, int) or (isinstance(value, float) and value.is_integer()):
            return str(int(value))
        else:
            return f"{value:.6f}"
    
    @staticmethod
    def should_be_integer(key: str) -> bool:
        """속성이 정수로 표현되어야 하는지 판단"""
        return key in UILoaderConfig.INTEGER_PROPERTIES
    
    @staticmethod
    def should_preserve_decimal(key: str) -> bool:
        """속성이 소수점을 유지해야 하는지 판단"""
        return key in UILoaderConfig.DECIMAL_PROPERTIES


class UINodeProcessor:
    """UI 노드 처리기"""
    
    @staticmethod
    def set_defaults(node_dict: Dict[str, Any]) -> Dict[str, Any]:
        """노드 타입에 따른 기본값 설정"""
        node_type = node_dict.get('type', '')
        defaults = UILoaderConfig.BASE_DEFAULTS.copy()
        
        # 타입별 기본값 추가
        type_defaults = UINodeProcessor._get_type_defaults(node_type)
        defaults.update(type_defaults)
        
        # 기본값 적용 (기존 값이 없는 경우만)
        for key, default_value in defaults.items():
            if key not in node_dict:
                node_dict[key] = default_value
        
        # 특수 처리
        UINodeProcessor._handle_special_cases(node_dict, node_type)
        
        return node_dict
    
    @staticmethod
    def _get_type_defaults(node_type: str) -> Dict[str, Any]:
        """노드 타입별 기본값 반환"""
        defaults_map = {
            'CCSprite': UINodeDefaults.get_sprite_defaults(),
            'CCButton': UINodeDefaults.get_button_defaults(),
            'CCStylishLabelTTF': UINodeDefaults.get_label_defaults(),
            'CCTextFieldTTF': UINodeDefaults.get_label_defaults(),
            'CCScale9Sprite': UINodeDefaults.get_scale9_defaults(),
            'CCLayerColor': UINodeDefaults.get_layer_color_defaults(),
        }
        return defaults_map.get(node_type, {})
    
    @staticmethod
    def _handle_special_cases(node_dict: Dict[str, Any], node_type: str) -> None:
        """특수한 경우 처리"""
        # CCButton: filename을 normalFilename으로 변환
        if node_type == 'CCButton' and 'filename' in node_dict:
            node_dict['normalFilename'] = node_dict['filename']
            del node_dict['filename']
    
    @staticmethod
    def get_property_order(node_type: str) -> List[str]:
        """노드 타입별 속성 출력 순서 반환"""
        order = UILoaderConfig.PROPERTY_ORDER.copy()
        
        # 타입별 추가 속성
        if node_type == 'CCButton':
            order.extend(['enabled', 'color', 'opacity', 'blendFunc', 
                         'normalFilename', 'selectedFilename', 'disabledFilename', 'imageX', 'imageY'])
        elif node_type == 'CCSprite':
            order.extend(['color', 'opacity', 'blendFunc', 'filename', 'flipX', 'flipY'])
        elif node_type == 'CCStylishLabelTTF':
            order.extend(['color', 'opacity', 'fontName', 'fontSize', 'text', 'alignment',
                         'hasStroke', 'strokeTickness', 'strokeColor', 'hasBold', 'hasGlow',
                         'glowTickness', 'glowColor', 'glowOpacity'])
        elif node_type == 'CCScale9Sprite':
            order.extend(['color', 'opacity', 'blendFunc', 'filename', 'centerRect', 'stretch'])
        elif node_type == 'CCLayerColor':
            order.extend(['color', 'opacity', 'blendFunc'])
        
        return order


class LuaConverter:
    """JSON을 Lua 형식으로 변환하는 메인 클래스"""
    
    @staticmethod
    def json_to_lua_string(json_string: str) -> str:
        """JSON 문자열을 Lua 테이블 문자열로 변환"""
        try:
            data = json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파싱 오류: {e}")
        
        return LuaConverter._convert_node(data, "")
    
    @staticmethod
    def _convert_node(node_dict: Dict[str, Any], indent: str = "\t") -> str:
        """단일 노드를 Lua 형식으로 변환"""
        # 기본 속성 설정
        node_dict = UINodeProcessor.set_defaults(node_dict.copy())
        
        lua_lines = []
        children = node_dict.pop('children', [])
        node_type = node_dict.get('type', '')
        
        # 자식 노드들 처리
        LuaConverter._process_children(children, lua_lines, indent)
        
        # 속성들 처리
        LuaConverter._process_properties(node_dict, node_type, lua_lines, indent)
        
        return f"{{\n{chr(10).join(lua_lines)}\n{indent[:-1] if indent else ''}}}"
    
    @staticmethod
    def _process_children(children: List[Dict], lua_lines: List[str], indent: str) -> None:
        """자식 노드들을 처리하여 lua_lines에 추가"""
        for i, child in enumerate(children, 1):
            child_lua = LuaConverter._convert_node(child, indent + "\t")
            lua_lines.extend([
                f"{indent}[{i}] =",
                f"{indent}{child_lua};"
            ])
    
    @staticmethod
    def _process_properties(node_dict: Dict[str, Any], node_type: str, lua_lines: List[str], indent: str) -> None:
        """노드의 속성들을 처리하여 lua_lines에 추가"""
        property_order = UINodeProcessor.get_property_order(node_type)
        processed_keys = set()
        
        # 정렬된 순서로 속성 출력
        for key in property_order:
            if LuaConverter._should_output_property(key, node_dict):
                LuaConverter._add_property_line(key, node_dict[key], lua_lines, indent)
                processed_keys.add(key)
        
        # 순서에 없는 추가 속성들 처리
        for key, value in node_dict.items():
            if key not in processed_keys and LuaConverter._should_output_property(key, node_dict):
                LuaConverter._add_property_line(key, value, lua_lines, indent)
    
    @staticmethod
    def _should_output_property(key: str, node_dict: Dict[str, Any]) -> bool:
        """속성을 출력해야 하는지 판단"""
        if key not in node_dict or node_dict[key] is None:
            return False
        
        value = node_dict[key]
        # 빈 배열은 출력하지 않음
        if isinstance(value, (list, tuple)) and len(value) == 0:
            return False
        
        return True
    
    @staticmethod
    def _add_property_line(key: str, value: Any, lua_lines: List[str], indent: str) -> None:
        """속성 라인을 lua_lines에 추가"""
        # 정수형 속성 처리
        if LuaFormatter.should_be_integer(key) and isinstance(value, (int, float)):
            value = int(value)
        
        # 소수점 유지 여부 결정
        preserve_decimal = LuaFormatter.should_preserve_decimal(key)
        formatted_value = LuaFormatter.format_value(value, preserve_decimal)
        lua_lines.append(f"{indent}{key} = {formatted_value};")


# 기존 함수들을 새로운 클래스 기반 구현으로 대체
def format_lua_value(value, preserve_decimal=False):
    """하위 호환성을 위한 래퍼 함수"""
    return LuaFormatter.format_value(value, preserve_decimal)

def should_be_integer(key):
    """하위 호환성을 위한 래퍼 함수"""
    return LuaFormatter.should_be_integer(key)

def should_preserve_decimal(key):
    """하위 호환성을 위한 래퍼 함수"""
    return LuaFormatter.should_preserve_decimal(key)

def set_default_ui_properties(node_dict: Dict[str, Any]) -> Dict[str, Any]:
    """하위 호환성을 위한 래퍼 함수"""
    return UINodeProcessor.set_defaults(node_dict)

def json_to_lua_string(json_string: str) -> str:
    """하위 호환성을 위한 래퍼 함수"""
    return LuaConverter.json_to_lua_string(json_string)