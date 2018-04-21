import pkgutil
import importlib
import inspect

from stdlib_list import stdlib_list


def import_module(_mod_name):
    return importlib.import_module(_mod_name)


def import_class(_mod, _class_name):
    try:
        return getattr(_mod, _class_name)
    except AttributeError:
        return None


def get_functions_of_class(_mod, _class_name):
    """
    得到类的函数/变量名列表.
    """
    cls = import_class(_mod, _class_name)

    functions = inspect.getmembers(cls)
    return [func[0] for func in functions]


def get_members(_mod_name):
    """
    得到：
        模块.类.函数名/变量名列表
        模块.函数名/变量名列表
    """
    try:
        mod = import_module(_mod_name)

        def is_member(_member):
            try:
                return _member.__module__ == _mod_name
            except AttributeError:
                return False

        members = inspect.getmembers(mod, is_member)

        results = []
        for member in members:
            if inspect.isclass(member[1]):
                results += ["%s.%s.%s" % (_mod_name, member[0], func)
                            for func in get_functions_of_class(mod, member[0])]
            else:
                results.append("%s.%s" % (_mod_name, member[0]))

        return results
    except Exception:
        return []


def get_package_members(package):
    """
    得到
        包.包.包.模块.类.函数名/变量名
        包.包.包.模块.函数名/变量名
    """
    results = []
    try:
        for _, modname, ispkg in pkgutil.iter_modules(import_module(package).__path__):
            if not ispkg:
                absolute_modname = "%s.%s" % (package, modname)
                functions = get_members(absolute_modname)
                results += functions
            else:
                results += get_package_members("%s.%s" % (package, modname))
        return results
    except Exception:
        return []


def get_members_and_package_members(mod_name):
    """
    得到
        包.包.包.模块.类.函数名/变量名
        包.包.包.模块.函数名/变量名
        模块.类.函数名/变量名列表
        模块.函数名/变量名列表
    """
    try:
        members = get_members(mod_name)
        package_members = get_package_members(mod_name)
        return members + package_members
    except:
        return []


def print_array(items):
    for item in items[0:1000]:
        print(item)


def get_standard_lib():
    libraries = stdlib_list("3.5")
    libraries_with_functions = [(library, get_members_and_package_members(library)) for library in libraries]
    return libraries_with_functions


def get_django_lib():
    return get_members_and_package_members('django')


if __name__ == '__main__':
    print_array(get_django_lib())
