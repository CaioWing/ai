import re
from typing import Tuple

def parse_response(response: str) -> Tuple[str, str, str]:
    patterns = {
        "bash": r"```bash\n(.*?)```",
        "modify": r"```modify\n(.*?)\n---\n(.*?)```",
        "analyze": r"```analyze\n(.*?)```"
    }

    for action, pattern in patterns.items():
        match = re.search(pattern, response, re.DOTALL)
        if match:
            if action == "modify":
                return action, match.group(1), match.group(2)
            else:
                return action, match.group(1), ""
    return "none", "", ""
