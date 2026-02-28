import typing as t
from string.templatelib import Template


type TDOM = t.Annotated[Template, "html", "tdom"]
