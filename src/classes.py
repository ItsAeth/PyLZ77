"""
A buffer class.
"""

from typing import Optional

class Buffer():

    """
    An auto-cropping list with a maximum length set by the user. Can be updated by adding elements or deleting 1 element.
    """

    def __init__(
            self,
            wsize:int,
            elements:list[str] = [],
        ):
        self._wsize = wsize
        self._elements = elements

    @property
    def wsize(self):
        return self._wsize

    @property
    def text(self):
        return self._text

    @property
    def elements(self):
        return self._elements

    def load(self, new: list[str]):
        """
        Initialize the buffer by loading elements into it.
        """
        self._elements = new
    
    def update(self, new : Optional[list[str]] = None):
        """
        Update the elements of the buffer by making a copy and appending new elements or just scrolling by deleting the first one. The buffer crops itself from the left to fit the window size.
        """
        
        # Copy the contents of the buffer
        copy = [elem for elem in self.elements if elem is not None]

        if new:
            copy.extend(new)    # Add new characters into the buffer
        else:
            copy.pop(0)         # If no characters are added, remove the 1st

        if len(copy) > self.wsize:
            # Crop the buffer if window size is exceeded after extending
            copy = copy[-self.wsize:] 

        self._elements = copy