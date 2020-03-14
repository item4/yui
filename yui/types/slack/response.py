from typing import Any
from typing import Dict
from typing import Union

import attr


@attr.dataclass(slots=True)
class APIResponse:

    body: Union[Dict[str, Any], str]
    status: int
    headers: Dict[str, Any]
