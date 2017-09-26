from typing import Mapping, Optional


def features() -> Mapping[str, Optional[str]]:
    if not hasattr(features, 'features'):
        setattr(features, 'features', {
            'autopurge': 'Auto Purge',
            })
    return getattr(features, 'features')
