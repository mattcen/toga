from toga.handlers import wrapped_handler

from .base import Widget


class MultilineTextInput(Widget):
    def __init__(
        self,
        id=None,
        style=None,
        value=None,
        readonly=False,
        placeholder=None,
        on_change=None,
    ):
        """Create a new multi-line text input widget.

        Inherits from :class:`~toga.widgets.base.Widget`.

        :param id: The ID for the widget.
        :param style: A style object. If no style is provided, a default style
            will be applied to the widget.
        :param value: The initial content to display in the widget.
        :param readonly: Can the value of the widget be modified by the user?
        :param placeholder: The content to display as a placeholder when
            there is no user content to display.
        :param on_change: A handler that will be invoked when the the value of
            the widget changes as a result of user input.
        """

        super().__init__(id=id, style=style)

        # Create a platform specific implementation of a MultilineTextInput
        self._impl = self.factory.MultilineTextInput(interface=self)

        # Set all the properties
        self.value = value
        self.readonly = readonly
        self.placeholder = placeholder
        self.on_change = on_change

    @property
    def placeholder(self):
        """The placeholder text for the widget.

        A value of ``None`` will be interpreted and returned as an empty string.
        Any other object will be converted to a string using ``str()``.
        """
        return self._impl.get_placeholder()

    @placeholder.setter
    def placeholder(self, value):
        self._impl.set_placeholder("" if value is None else str(value))
        self.refresh()

    @property
    def enabled(self):
        """Is the widget currently enabled? i.e., can the user interact with the
        widget?

        Disabling a MultilineTextInput is equivalent to making the input
        read-only.
        """
        return not self._impl.get_readonly()

    @enabled.setter
    def enabled(self, value):
        self._impl.set_readonly(not bool(value))

    @property
    def readonly(self):
        """Can the value of the widget be modified by the user?

        This only controls manual changes by the user (i.e., typing at the
        keyboard). Programmatic changes are permitted while the widget has
        ``readonly`` enabled.
        """
        return self._impl.get_readonly()

    @readonly.setter
    def readonly(self, value):
        self._impl.set_readonly(bool(value))

    @property
    def value(self):
        """The text to display in the widget.

        A value of ``None`` will be interpreted and returned as an empty string.
        Any other object will be converted to a string using ``str()``.
        """
        return self._impl.get_value()

    @value.setter
    def value(self, value):
        self._impl.set_value("" if value is None else str(value))
        self.refresh()

    def clear(self):
        """Clear any text from the widget.

        This will restore any placeholder text, if a placeholder has been
        provided.
        """
        self.value = ""

    def scroll_to_bottom(self):
        """Scroll the view to make the bottom of the text field visible."""
        self._impl.scroll_to_bottom()

    def scroll_to_top(self):
        """Scroll the view to make the top of the text field visible."""
        self._impl.scroll_to_top()

    @property
    def on_change(self):
        """The handler to invoke when the value of the widget changes.

        This is only invoked in response to user-generated changes.
        """
        return self._on_change

    @on_change.setter
    def on_change(self, handler):
        self._on_change = wrapped_handler(self, handler)
