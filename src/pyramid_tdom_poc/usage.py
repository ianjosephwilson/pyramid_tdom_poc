import inspect
from dataclasses import dataclass
from string.templatelib import Template
from collections.abc import Callable

from tdom.processor import ProcessorService

from .pretty import format_template


class LiteralHTML:
    def __init__(self, text):
        self.text = text

    def __html__(self):
        return self.text


@dataclass
class Example:
    """
    Try to generalize the major interpolation forms that TDOM accepts into a
    single component for display.
    """

    title: str
    children: Template
    tdom_processor_api: ProcessorService
    description: str = ""
    section_classes: tuple[str, ...] = ("ex-section",)
    pretty_classes: tuple[str, ...] = ("ex-pretty",)
    children_classes: tuple[str, ...] = ("ex-children",)
    rules_classes: tuple[str, ...] = ("ex-rules",)
    description_classes: tuple[str, ...] = ("ex-description",)
    show_children: bool = False
    component_callables: tuple[
        Callable[..., Template] | Callable[..., Callable[[], Template]], ...
    ] = ()
    rules: tuple[tuple[str, str], ...] = ()
    # Out of fields... we need more fields...

    def __call__(self):
        children_tnode = self.tdom_processor_api.parser_api.to_tnode(self.children)
        pretty_t = format_template(children_tnode, self.children)
        if self.component_callables:
            pretty_t = t"""{pretty_t}{[t"<div><pre>{inspect.getsource(cc)}</pre></div>" for cc in self.component_callables]}"""
        return sum(
            [
                t"<section class={self.section_classes}>",
                t"<h4>{self.title}</h4>",
                t"<p class={self.description_classes}>{self.description}</p>"
                if self.description
                else t"",
                t"<div class={self.rules_classes}>{[t'<div><code>{name}</code><code>{definition}</code></div>' for name, definition in self.rules]}</div>"
                if self.rules
                else t"",
                t"<div class={self.pretty_classes}>{pretty_t}</div>",
                t"<div class={self.children_classes}>{self.children if self.show_children else 'Children Not Shown'}</div>",
                t"</section>",
            ],
            t"",
        )


def get_styles_t():
    return Template("""
<style>
  .root {
      width: 50%
  }
  .telement_tag {
        color: blue
  }
  .tcomponent_tag {
        color: green;
  }
  .tattr_name { color: black; }
  .tattr_value { color: red; }
  .tcomment_literal, .ttext_literal {color: black; }
  .tcomment_ip, .ttext_ip { color: green; }
  .tcomment_tag { color: orange; }

  .ex-section {
    max-width: 800px;
    margin-bottom: 30px;
  }
  .ex-section > h4 {
      font-family: monospace;
      font-size: 20px;
      color: #333;
  }
  .ex-description, .ex-pretty, .ex-children, .ex-rules {
      padding-left: 20px;
      margin-bottom: 10px;
  }
</style>
""")


def get_component_example_t():
    def FactoryComponent(
        children: Template, wrap_in_style: dict | None = None
    ) -> Callable[[], Template]:
        def func() -> Template:
            return FunctionComponent(children, wrap_in_style=wrap_in_style)

        return func

    def FunctionComponent(
        children: Template, wrap_in_style: dict | None = None
    ) -> Template:
        return t'<div style="{wrap_in_style}">{children}</div>'

    rules = tuple(
        [
            ("type FunctionComponentSig=", "Callable[..., Template]"),
            ("type FactoryComponentSig=", "Callable[..., Callable[[], Template]]"),
        ]
    )
    component_callables = tuple([FactoryComponent, FunctionComponent])
    return t"""<{Example}
        title="Component Forms"
        description="Components can be a simple functions or a factory that returns a function."
        rules={rules}
        component_callables={component_callables}
        show_children>
        <{FunctionComponent} wrap-in-style={ {"color": "purple"} }><em>Function!</em></{FunctionComponent}>
        <{FactoryComponent} wrap-in-style={ {"color": "orange"} }><em>Factory!</em></{FactoryComponent}>
    </{Example}>"""


def get_normal_text_example_t():
    rules = tuple(
        [
            ("type VALUE=", "None|str|Template|Iterable[VALUE]|HasHTMLDunder|object"),
        ]
    )
    return t"""<{Example}
        title="Normal Text Forms"
        description="HTML elements with normal text content."
        rules={rules}
        show_children>
    <div>
      <div>{None}</div>
      <div>{"str"}</div>
      <div>{t"<span>{'nested'}</span>"}</div>
      <div>{["iter", "able"]}</div>
      <div>{LiteralHTML("&")}</div>
      <div>{1}</div>
    </div>
    </{Example}>"""


def get_raw_text_example_t():
    rules = tuple(
        [
            ("type EXACT=", "None|str|HasHTMLDunder|object"),
            ("type INEXACT=", "None|str|object"),
        ]
    )
    return t"""<{Example}
        title="Raw Text Forms"
        description="HTML elements with raw text content: script or style."
        rules={rules}
        show_children>
    <div>
      <script>{None}</script>
      <script>{"window.ExampleApp = {};"}</script>
      <script>{LiteralHTML('window.ExampleApp.message = "escape-hatch";')}</script>
      <script>{100}</script>
      <script>var x = 1; {None};</script>
      <script>var x = 1; {"var y = 2;"}</script>
      <script>var x = 1; var y = {2};</script>
    </div>
    </{Example}>"""


def get_escapable_raw_text_example_t():
    rules = tuple(
        [
            ("type EXACT=", "None|str|HasHTMLDunder|object"),
            ("type INEXACT=", "None|str|object"),
        ]
    )
    return t"""<{Example}
        title="Escapable Raw Text Forms"
        description="HTML elements with escapable raw text content: textarea or title."
        rules={rules}
        show_children>
    <div>
      <textarea name="ex">{None}</textarea>
      <textarea name="ex">{"<div></div>"}</textarea>
      <textarea name="ex">{LiteralHTML("<div></div>")}</textarea>
      <textarea name="ex">{100}</textarea>
      <textarea name="ex"><div></div>{None};</textarea>
      <textarea name="ex"><div></div>{"<script></script></textarea>"}</textarea>
      <textarea name="ex"><div></div>{2};</textarea>
    </div>
    </{Example}>"""


def get_comment_example_t():
    rules = tuple(
        [
            ("type EXACT=", "None|str|HasHTMLDunder|object"),
            ("type INEXACT=", "None|str|object"),
        ]
    )
    return t"""<{Example}
        title="Comment Forms"
        description="HTML comments with simple interpolations are supported."
        rules={rules}
        show_children>
    <!--{LiteralHTML("escape-hatch")}-->
    <!--{None}-->
    <!--{"str"}-->
    <!--{1}-->
    <!--{None}{"str"}{1}-->
    </{Example}>"""


def get_interpolated_attribute_example_t():
    rules = ((t"type InterpolatedValue=", t"None|str|bool"),)
    return t"""<{Example}
        title="General Interpolated Attribute"
        description="HTML attribute's entire value is an interpolation."
        rules={rules}
        show_children>
    <div>
    <img width={None} height=20 src="/assets/red.png">
    <img width={10} height=20 src="/assets/red.png">
    <img width={"10"} height=20 src="/assets/red.png">
    <img width={False} height=20 src="/assets/red.png">
    <img width={True} height=20 src="/assets/red.png">

    <img width="" height=20 src="/assets/red.png">
    <img title="The color is {"Red"}." height=20 src="/assets/red.png">
    <img { {"title": "The color is red", "height": 20, "src": "/assets/red.png"} }>
    </div>
    </{Example}>"""


def get_templated_attribute_example_t():
    rules = ((t"type TemplatedValue=", t"str|object"),)
    return t"""<{Example}
        title="General Templated Attribute"
        description="HTML attribute's value is a mix of literal text and interpolations."
        rules={rules}
        show_children>
    <div>
    <img title="The image color is {"Red"}." height=20 src="/assets/red.png">
    <img title="The image color is {True}, {False} or {None}." height=20 src="/assets/red.png">
    </div>
    </{Example}>"""


def get_spread_attribute_example_t():
    rules = ((t"type SpreadValue=", t"None|dict[str, None|str|bool|object]"),)
    return t"""<{Example}
        title="General Spread Attribute"
        description="HTML attribute has no value and the name is entirely an interpolation."
        rules={rules}
        show_children>
    <div>
    <img { {"title": "The color is red", "height": 20, "src": "/assets/red.png"} }>
    </div>
    </{Example}>"""


def get_class_attribute_example_t():
    rules = ((t"type ClassValue=", t"None|str|dict[str, bool|None]|Sequence[str]"),)
    return t"""<{Example}
        title="Class Attribute"
        description="HTML class attributes have special handling."
        rules={rules}
        show_children>
    <div>
    <img class="mw100" class={"theme-default"} class={("b--blue", "db")} class={ {"m2": False} }>
    </div>
    </{Example}>"""


def get_style_attribute_example_t():
    rules = ((t"type StyleValue=", t"None|str|dict[str, str|None]"),)
    return t"""<{Example}
        title="Style Attribute"
        description="HTML style attributes have special handling."
        rules={rules}
        show_children>
    <div>
    <div style="background-color: white; text-decoration: line-through" style={"color: red"} style={ {"font-size": "20px", "background-color": None} }>TEXT</div>
    </div>
    </{Example}>"""


def get_aria_attribute_example_t():
    rules = ((t"type AriaValue=", t"None|str|dict[str, None|object"),)
    return t"""<{Example}
        title="Aria Attribute"
        description="HTML aria attribute has special handling."
        rules={rules}
        show_children>
    <div>
    <div aria={ {"role": "button"} }>TEXT</div>
    </div>
    </{Example}>"""


def get_data_attribute_example_t():
    rules = ((t"type DataValue=", t""),)
    return t"""<{Example}
        title="Data Attribute"
        description="HTML data attribute has special handling."
        rules={rules}
        show_children>
    <div>
    <div data={ {"property-context": "entrance"} }>TEXT</div>
    </div>
    </{Example}>"""


def usage_view(request):
    examples = [
        get_normal_text_example_t(),
        get_component_example_t(),
        get_escapable_raw_text_example_t(),
        get_raw_text_example_t(),
        get_comment_example_t(),
        get_interpolated_attribute_example_t(),
        get_templated_attribute_example_t(),
        get_spread_attribute_example_t(),
        get_class_attribute_example_t(),
        get_style_attribute_example_t(),
        get_aria_attribute_example_t(),
        get_data_attribute_example_t(),
    ]
    return t"<!doctype html><html><head>{get_styles_t()}</head><body><div>{examples}</div></body></html>"
