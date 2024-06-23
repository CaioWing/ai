import re
from typing import List, Tuple, Dict

def parse_response(response: str) -> List[Tuple[str, Dict[str, str]]]:
    pattern = r'\[(\w+)\](.*?)\[/\1\]'
    matches = re.findall(pattern, response, re.DOTALL)
    
    parsed_actions = []

    for action_type, content in matches:
        action_type = action_type.lower()
        
        if action_type == 'modify':
            file_pattern = r'FILE: (.*?)\n---\n(.*)'
            file_match = re.search(file_pattern, content, re.DOTALL)
            if file_match:
                file_path, file_content = file_match.groups()
                parsed_actions.append((action_type, {
                    'file_path': file_path.strip(),
                    'content': file_content.strip()
                }))
        else:
            parsed_actions.append((action_type, {'content': content.strip()}))

    return parsed_actions if parsed_actions else [("none", {})]