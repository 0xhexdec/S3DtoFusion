from xml.dom.minidom import Element

from ...utils.Exceptions import ElementNotFoundException


def getInt(elem: Element, tag: str) -> int:
    try:
        return int(elem.getElementsByTagName(tag)[0].childNodes[0].data)
    except IndexError:
        raise ElementNotFoundException(tag)
    except Exception as e:
        raise e

def getFloat(elem: Element, tag: str) -> float:
    try:
        return float(elem.getElementsByTagName(tag)[0].childNodes[0].data)
    except IndexError:
        raise ElementNotFoundException(tag)
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
                raise ElementNotFoundException(tag)
        except IndexError as e2:
            raise ElementNotFoundException(tag)
        except Exception as e2:
            raise e2
    except Exception as e:
        raise e

def getBool(elem: Element, tag: str) -> bool:
    try:
        return bool(getInt(elem, tag))
    except Exception as e:
        raise e
