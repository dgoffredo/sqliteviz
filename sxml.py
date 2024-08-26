"""Simplify use of `xml.etree.ElementTree.TreeBuilder` using s-expressions.

Example:

>>> import datetime
>>> import uuid
>>> from xml.etree import ElementTree
>>> import sxml
>>> feed = ['feed', {'xmlns': 'http://www.w3.org/2005/Atom'},
...     ['title', 'A Programming Blog'],
...     ['link', {'href': 'https://www.davidgoffredo.com'}],
...     ['updated', datetime.date(2038, 1, 19)],
...     ['author',
...         ['name', 'David Goffredo']],
...     ['id', uuid.uuid3(uuid.NAMESPACE_DNS, 'www.davidgoffredo.com')]]
>>> element = sxml.element_from_sexpr(feed)
>>> print(ElementTree.tostring(element, encoding='unicode'))
<feed xmlns="http://www.w3.org/2005/Atom"><title>A Programming Blog</title><link href="https://www.davidgoffredo.com" /><updated>2038-01-19</updated><author><name>David Goffredo</name></author><id>05c8119e-2310-3c40-918d-a824ddffa17e</id></feed>
"""


from typing import Optional
from xml.etree import ElementTree as ET


def element_from_sexpr(sexpr) -> Optional[ET.Element]:
    """Return an XML `Element` parsed from the specified symbolic expression
    `sexpr`, or return `None` if `sexpr` does not represent an XML element.
    """
    builder = ET.TreeBuilder()
    element = _element_from_sexpr(sexpr, builder)
    root = builder.close()
    return element or root # in case `builder` wasn't used


def _element_from_sexpr(sexpr, builder: ET.TreeBuilder) -> Optional[ET.Element]:
    if isinstance(sexpr, list):
        _element_from_list(sexpr, builder)
    elif isinstance(sexpr, ET.Element):
        return sexpr
    elif isinstance(sexpr, str):
        builder.data(sexpr)
    else:
        builder.data(str(sexpr))


def _element_from_list(sexpr, builder: ET.TreeBuilder):
    assert len(sexpr)
    tag, *rest = sexpr
    attributes = {}
    if len(rest) and isinstance(rest[0], dict):
        attributes, *rest = rest

    element = builder.start(tag, attributes)
    for child in rest:
        child_element = _element_from_sexpr(child, builder)
        if child_element is not None:
            element.append(child_element)
    builder.end(tag)

