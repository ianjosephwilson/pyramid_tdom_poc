from dataclasses import dataclass
from string.templatelib import Template, Interpolation

from tdom.tnodes import (
    TFragment,
    TElement,
    TText,
    TDocumentType,
    TComment,
    TComponent,
    TLiteralAttribute,
    TInterpolatedAttribute,
    TTemplatedAttribute,
    TSpreadAttribute,
    TAttribute,
)
from tdom.htmlspec import (
    VOID_ELEMENTS,
)


def format_el_start(
    el: TElement,
    template: Template,
    prefix_classes: tuple[str] = ("telement_tag",),
    suffix_classes: tuple[str] = ("telement_tag",),
    use_startend=False,
    close_void=False,
):
    start_prefix = t"<span class={prefix_classes}>{'<'}{el.tag}</span>"
    if el.tag in VOID_ELEMENTS:
        if close_void:
            suffix_text = " />"
        else:
            suffix_text = ">"
    elif not el.children and use_startend:
        suffix_text = " />"
    else:
        suffix_text = ">"
    start_suffix = t"<span class={suffix_classes}>{suffix_text}</span>"
    attrs_t = sum([format_attr(attr, template) for attr in el.attrs], t"")
    return t"{start_prefix}{attrs_t}{start_suffix}"


def format_el_end(
    el: TElement,
    template: Template,
    classes: tuple[str] = ("telement_tag",),
    use_startend=False,
) -> Template:
    if (not el.children and use_startend) or el.tag in VOID_ELEMENTS:
        return t""
    else:
        return t"<span class={classes}>{'</'}{el.tag}{'>'}</span>"


def format_interpolation(
    ip: Interpolation, ip_index: int, classes: tuple[str, ...] = ("interpolation",)
) -> Template:
    exp = t"{ip.expression}" if ip.expression else t"{ip_index}"
    if ip.conversion is not None:
        exp += t"!{ip.conversion}"
    if ip.format_spec != "":
        exp += t":{ip.format_spec}"
    return t"<span class={classes}>{{" + exp + t"}}</span>"


def format_attr(
    attr: TAttribute,
    template: Template,
    name_classes: tuple[str, ...] = ("tattr_name",),
    value_classes: tuple[str, ...] = ("tattr_value",),
) -> Template:
    match attr:
        case TLiteralAttribute():
            # Leading space
            name_t = t"<span class={name_classes}>{attr.name}</span>"
            value_t = t'<span class={value_classes}>"{attr.value}"</span>'
            return t" {name_t}={value_t}"
        case TInterpolatedAttribute():
            name_t = t"<span class={name_classes}>{attr.name}</span>"
            value_t = (
                t"<span class={value_classes}>"
                + format_interpolation(
                    template.interpolations[attr.value_i_index], attr.value_i_index
                )
                + t"</span>"
            )
            return t" {name_t}={value_t}"
        case TTemplatedAttribute():
            name_t = t"<span class={name_classes}>{attr.name}</span>"
            value_parts = []
            for part in attr.value_ref:
                if isinstance(part, str):
                    value_parts.append(t"{part}")
                else:
                    value_parts.append(
                        format_interpolation(template.interpolations[part], part)
                    )
            value_t = (
                t"<span class={value_classes}>" + sum(value_parts, t"") + t"</span>"
            )
            return t" {name_t}={value_t}"
        case TSpreadAttribute():
            name_t = (
                t"<span class={name_classes}>"
                + format_interpolation(
                    template.interpolations[attr.i_index], attr.i_index
                )
                + t"</span>"
            )
            return t" {name_t}"
        case _:
            raise NotImplementedError("Unhandled attribute type.")


def format_comp_start(
    comp: TComponent,
    template: Template,
    prefix_classes: tuple[str] = ("tcomponent_tag",),
    suffix_classes: tuple[str] = ("tcomponent_tag",),
    use_startend=False,
):
    exp_t = format_interpolation(
        template.interpolations[comp.start_i_index], comp.start_i_index
    )
    attrs_t = sum([format_attr(attr, template) for attr in comp.attrs], t"")
    if comp.children or not use_startend:
        suffix_text = ">"
    else:
        suffix_text = " />"
    return t"<span class={prefix_classes}>{'<'}{exp_t}</span>{attrs_t}<span class={suffix_classes}>{suffix_text}</span>"


def format_comp_end(
    comp: TComponent,
    template: Template,
    classes: tuple[str] = ("tcomponent_tag",),
    use_startend=False,
):
    if (not use_startend or comp.children) and comp.end_i_index is not None:
        exp_t = format_interpolation(
            template.interpolations[comp.end_i_index], comp.end_i_index
        )
        return t"<span class={classes}>{'</'}{exp_t}{'>'}</span>"
    else:
        return t""


@dataclass
class CloseElement:
    node: TElement


@dataclass
class CloseComponent:
    node: TComponent


def format_text(
    text: TText,
    template: Template,
    literal_classes: tuple[str, ...] = ("ttext_literal",),
    ip_classes: tuple[str, ...] = ("ttext_ip",),
):
    parts = []
    for part in text.ref:
        if isinstance(part, str):
            parts.append(t"<span class={literal_classes}>{part}</span>")
        else:
            ip_t = format_interpolation(template.interpolations[part], part)
            parts.append(t"<span class={ip_classes}>{ip_t}</span>")
    return sum(parts, t"") if parts else None


def format_document_type(
    dt: TDocumentType, template: Template, classes: tuple[str, ...] = ("tdoctype",)
) -> Template:
    return t"<span class={classes}>{'<!DOCTYPE '}{dt.text}{'>'}</span>"


def format_comment(
    comment: TComment,
    template: Template,
    tag_classes: tuple[str, ...] = ("tcomment_tag",),
    literal_classes: tuple[str, ...] = ("tcomment_literal",),
    ip_classes: tuple[str, ...] = ("tcomment_ip",),
) -> Template:
    parts = []
    for part in comment.ref:
        if isinstance(part, str):
            parts.append(t"<span class={literal_classes}>{part}</span>")
        else:
            ip_t = format_interpolation(template.interpolations[part], part)
            parts.append(t"<span class={ip_classes}>{ip_t}</span>")
    inner_t = sum(parts, t"") if parts else t""
    return t"<span class={tag_classes}>{'<!--'}</span>{inner_t}<span class={tag_classes}>{'-->'}</span>"


def format_template(root, root_template, root_classes: tuple[str, ...] = ("troot",)):
    q = [(root, root_template)]
    out = []
    while q:
        (node, template) = q.pop()
        match node:
            case TDocumentType():
                out.append(format_document_type(node, template))
            case TComment():
                out.append(format_comment(node, template))
            case CloseElement():
                out.append(format_el_end(node.node, template))
            case CloseComponent():
                out.append(format_comp_end(node.node, template))
            case TFragment():
                q.extend([(n, template) for n in reversed(node.children)])
            case TElement():
                out.append(format_el_start(node, template))
                q.append((CloseElement(node), template))
                q.extend([(n, template) for n in reversed(node.children)])
            case TComponent():
                out.append(format_comp_start(node, template))
                q.append((CloseComponent(node), template))
                # @TODO: Do we want this?
                q.extend([(n, template) for n in reversed(node.children)])
            case TText():
                out.append(format_text(node, template))
            case _:
                raise ValueError(f"Unknown tnode {node}")
    return t"<div class={root_classes}>{[chunk for chunk in out]}</div>"
