from typing import Dict
from saria.app import App, Bundle, Module
from saria.app.factory import Factory


def test_it_should_bootstrap():
    class Foo(Module):
        pass

    class Bar(Module):
        def __init__(self, foo: Foo) -> None:
            super().__init__()
            self.foo = foo

    app = Bundle(
        bar=Bar,
    ).bootstrap()
    assert app.manifest.bar.foo is not None


def test_it_should_reuse_dependency_instances_across_classes():
    class Foo(Module):
        pass

    class Bar(Module):
        def __init__(self, foo: Foo) -> None:
            super().__init__()
            self.foo = foo

    class Baz(Module):
        def __init__(self, foo: Foo) -> None:
            super().__init__()
            self.foo = foo

    app = Bundle(
        bar=Bar,
        baz=Baz,
    ).bootstrap()
    assert app.manifest.bar.foo is app.manifest.baz.foo


def test_it_should_reuse_dependency_instances_across_classes_with_diffrent_names():
    class Foo(Module):
        pass

    class Bar(Module):
        def __init__(self, fooish: Foo) -> None:
            super().__init__()
            self.fooish = fooish

    class Baz(Module):
        def __init__(self, foo: Foo) -> None:
            super().__init__()
            self.foo = foo

    app = Bundle(
        bar=Bar,
        baz=Baz,
    ).bootstrap()
    assert app.manifest.bar.fooish is app.manifest.baz.foo


def test_it_should_inject_base_class_dependencies():
    class Foo(Module):
        pass

    class Bar(Module):
        def __init__(self, foo: Foo) -> None:
            super().__init__()
            self.foo = foo

    class Baz(Bar):
        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)

    app = Bundle(
        bar=Bar,
        baz=Baz,
    ).bootstrap()
    assert isinstance(app.manifest.baz.foo, Foo)


def test_it_should_inject_arrays_of_modules():
    class Foo(Module):
        pass

    class Bar(Module):
        pass

    app = Bundle(
        foos=[
            Foo,
            Bar,
        ],
    ).bootstrap()
    assert all(map(lambda foo: isinstance(foo, Module), app.manifest.foos))


def test_it_injects_separate_instances_of_factories():
    class Foo(Factory):
        pass

    class Bar(Module):
        def __init__(self, foo: Foo) -> None:
            self.foo = foo

    class Baz(Module):
        def __init__(self, foo: Foo) -> None:
            self.foo = foo

    app = Bundle(
        bar=Bar,
        baz=Baz,
    ).bootstrap()
    assert app.manifest.baz.foo is not app.manifest.bar.foo


def test_it_passes_along_non_modules_as_is():
    test_foo = {}

    class Bar(Module):
        def __init__(self, foo: Dict) -> None:
            self.foo = foo

    app = Bundle(
        bar=Bar,
        foo=test_foo,
    ).bootstrap()
    assert app.manifest.bar.foo is test_foo
