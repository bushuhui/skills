from __future__ import annotations

from copy import deepcopy

from docx.oxml import OxmlElement


def _m(tag: str):
    return OxmlElement(f"m:{tag}")


def math_text(text: str):
    run = _m("r")
    text_element = _m("t")
    text_element.text = text
    run.append(text_element)
    return run


def math_superscript(base_text: str, superscript_text: str):
    sup = _m("sSup")
    e = _m("e")
    e.append(math_text(base_text))
    sup_value = _m("sup")
    sup_value.append(math_text(superscript_text))
    sup.append(e)
    sup.append(sup_value)
    return sup


def math_fraction(numerator: str, denominator: str):
    fraction = _m("f")
    num = _m("num")
    num.append(math_text(numerator))
    den = _m("den")
    den.append(math_text(denominator))
    fraction.append(num)
    fraction.append(den)
    return fraction


def append_equation(paragraph, items: list[object]) -> None:
    o_math_para = _m("oMathPara")
    o_math = _m("oMath")
    for item in items:
        if isinstance(item, str):
            o_math.append(math_text(item))
        else:
            o_math.append(deepcopy(item))
    o_math_para.append(o_math)
    paragraph._p.append(o_math_para)
