import inspect
from typing import Type, List, Dict
from saria.decorators import memoize
from .manifest import Manifest
from .bundle import Bundle
from .module import Module
from .factory import Factory
from .dependency import Dependency

SELF = "self"
ARGS = "args"
KWARGS = "kwargs"
ignored_dependencies = [
    SELF,
    ARGS,
    KWARGS,
]


@memoize
def get_module_dependencies(prototype: Type) -> Dict[str, Dependency]:
    signature = inspect.signature(prototype.__init__)
    dependencies = {}

    # Collect base class dependencies so we can gather them without having
    # to define them in each inherited class
    if prototype.__bases__:
        for base_class in prototype.__bases__:
            if base_class is Module:
                continue
            dependencies = {
                **get_module_dependencies(base_class),
                **dependencies,
            }

    for parameter in signature.parameters:
        if parameter in ignored_dependencies:
            continue
        parameter = signature.parameters[parameter]
        dependencies[parameter.name] = Dependency(parameter.name, parameter.annotation)

    return dependencies


def _instantiate(
    prototype: Type,
    manifest: Manifest,
    bundle: Bundle,
) -> Module | Factory:
    dependencies = get_module_dependencies(prototype)
    params = {}
    for [dependency_name, dependency] in dependencies.items():
        if manifest[dependency_name]:
            params[dependency_name] = manifest[dependency_name]
            # TODO if not found, and we have a prototype look for by prototpe name, then inject
        elif dependency.prototype and manifest[dependency.prototype]:
            params[dependency_name] = manifest[dependency.prototype]
        else:
            if bundle[dependency_name] is not None:
                if inspect.isclass(bundle[dependency_name]):
                    if issubclass(bundle[dependency_name], Module):
                        manifest[dependency_name] = _inject(
                            bundle[dependency_name],
                            dependency_name,
                            manifest,
                            bundle,
                        )
                        params[dependency_name] = manifest[dependency_name]
                    elif issubclass(bundle[dependency_name], Factory):
                        params[dependency_name] = _instantiate(
                            bundle[dependency_name],
                            manifest,
                            bundle,
                        )
                    else:
                        raise Exception(
                            f"Unable to inject non-module type {str(dependency.prototype)}"
                        )
                else:
                    manifest[dependency_name] = bundle[dependency_name]
                    params[dependency_name] = manifest[dependency_name]
            elif bundle[dependency_name] is None and dependency.prototype is not None:
                if issubclass(dependency.prototype, Module):
                    # TODO when injecting via dependency inference, use the
                    # modules's dependency name
                    manifest[dependency_name] = _inject(
                        dependency.prototype,
                        dependency_name,
                        manifest,
                        bundle,
                    )
                    params[dependency_name] = manifest[dependency_name]
                elif issubclass(dependency.prototype, Factory):
                    params[dependency_name] = _instantiate(
                        dependency.prototype,
                        manifest,
                        bundle,
                    )
                else:
                    raise Exception(
                        f"Unable to inject non-module type {str(dependency.prototype)}"
                    )
            else:
                raise Exception(
                    f"{dependency_name} not found for module: {str(prototype)}"
                )

    instance = prototype(**params)
    return instance


def _create_module(
    prototype: Type,
    module_name: str,
    manifest: Manifest,
    bundle: Bundle,
):
    instance = _instantiate(
        prototype,
        manifest,
        bundle,
    )
    manifest[module_name] = instance
    return instance


def _inject(
    prototype: Type | List[Type],
    dependency_name: str,
    manifest: Manifest,
    bundle: Bundle,
) -> Module | Factory:
    if isinstance(prototype, List):
        manifest[dependency_name] = list(
            map(
                lambda proto: _inject(
                    proto,
                    dependency_name,
                    manifest,
                    bundle,
                ),
                prototype,
            )
        )
    elif inspect.isclass(prototype):
        if issubclass(prototype, Module):
            manifest[dependency_name] = _create_module(
                prototype,
                dependency_name,
                manifest,
                bundle,
            )
        elif issubclass(prototype, Factory):
            return _instantiate(prototype, manifest, bundle)
    else:
        manifest[dependency_name] = bundle[dependency_name]
    return manifest[dependency_name]


def inject_dependencies(bundle: Bundle) -> Manifest:
    manifest = Manifest()
    for [dependency_name, prototype] in bundle.dependencies.items():
        if manifest[dependency_name] is None:
            manifest[dependency_name] = _inject(
                prototype,
                dependency_name,
                manifest,
                bundle,
            )

    return manifest
