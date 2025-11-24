"""
Workaround for Python 3.9.0 typing module bug with Pydantic 2.x
This patches the typing._SpecialForm class to add a replace method
"""

import sys
import typing

def patch_typing_specialform():
    """Patch typing._SpecialForm to fix Pydantic 2.x compatibility with Python 3.9.0"""
    if sys.version_info[:2] == (3, 9) and sys.version_info[2] == 0:
        # Only patch for Python 3.9.0
        if not hasattr(typing._SpecialForm, 'replace'):
            def replace(self, old, new, count=-1):
                """Dummy replace method for _SpecialForm compatibility - returns self as string representation"""
                return str(self).replace(old, new, count) if isinstance(old, str) and isinstance(new, str) else self
            typing._SpecialForm.replace = replace

# Apply patch on import
patch_typing_specialform()

