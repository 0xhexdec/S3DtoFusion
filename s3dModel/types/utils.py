from xml.dom.minidom import Element
from typing import Optional

from ...utils.Exceptions import ElementNotFoundException

# TODO: Improve error handling, sometimes it should be better to return "default" value instead of raise Exception
# maybe better to use Optionals for types that are possibly not needed

def getInt(elem: Element, tag: str) -> int:
    try:
        return int(elem.getElementsByTagName(tag)[0].childNodes[0].data)
    except IndexError:
        raise ElementNotFoundException(tag)
    except Exception as e:
        raise e

def getOptionalInt(elem: Element, tag: str) -> Optional[int]:
    try:
        return int(elem.getElementsByTagName(tag)[0].childNodes[0].data)
    except IndexError:
        return None

def getFloat(elem: Element, tag: str) -> float:
    try:
        return float(elem.getElementsByTagName(tag)[0].childNodes[0].data)
    except IndexError:
        raise ElementNotFoundException(tag)
    except Exception as e:
        raise e

def getOptionalFloat(elem: Element, tag: str) -> Optional[float]:
    try:
        return float(elem.getElementsByTagName(tag)[0].childNodes[0].data)
    except Exception:
        return None

def getStr(elem: Element, tag: str) -> str:
    try:
        return elem.getElementsByTagName(tag)[0].childNodes[0].data
    except IndexError as e:
        try:
            if elem.getElementsByTagName(tag)[0].childNodes == []:
                return ""
            else:
                raise ElementNotFoundException(tag)
        except IndexError as e2:
            raise ElementNotFoundException(tag)
        except Exception as e2:
            raise e2
    except Exception as e:
        raise e

def getStr(elem: Element, tag: str) -> str:
    try:
        return elem.getElementsByTagName(tag)[0].childNodes[0].data
    except IndexError as e:
        try:
            if elem.getElementsByTagName(tag)[0].childNodes == []:
                return ""
            else:
                return None
        except Exception:
            return None
    except Exception:
        return None

def getBool(elem: Element, tag: str) -> bool:
    try:
        return bool(getInt(elem, tag))
    except Exception as e:
        raise e

def getOptionalBool(elem: Element, tag: str) -> Optional[bool]:
    try:
        return bool(getInt(elem, tag))
    except Exception:
        return None
