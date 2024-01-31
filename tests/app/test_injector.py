from saria.app.injector import get_module_dependencies


def test_it_returns_the_modules_dependencies():
    class Bar:
        pass

    class Foo:
        def __init__(self, bar: Bar):
            self.bar = bar

    dependencies = get_module_dependencies(Foo)
    assert len(dependencies) is 1


def test_it_gets_base_class_dependencies():
    class Baz:
        pass

    class Bar:
        def __init__(self, baz: Baz):
            self.baz = baz
            pass

    class Foo(Bar):
        def __init__(self, bar: Bar, **kwargs):
            super().__init__(**kwargs)
            self.bar = bar

    dependencies = get_module_dependencies(Foo)
    assert len(dependencies) is 2
