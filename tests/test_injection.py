"""Tests for the injection module.
"""
import pytest  # type: ignore

from crib import exceptions, injection


class Product(injection.Component):
    def __init__(self, name, container, foo, *, bar=None):
        super(Product, self).__init__(name, container)
        self.foo = foo
        self.bar = bar


def test_factory_provider():
    """Test a factory provider."""

    class Container(injection.Container):
        product = injection.FactoryProvider(Product, 1, bar=3)

    ctx = Container()
    product1 = ctx.product
    product2 = ctx.product

    assert isinstance(product1, Product)
    assert product1.foo == 1
    assert product1.bar == 3
    assert product1 is not product2


def test_singleton_provider():
    """Test a singleton provider."""

    class Container(injection.Container):
        product = injection.SingletonProvider(Product, 1, bar=3)

    ctx = Container()
    product1 = ctx.product
    product2 = ctx.product

    assert isinstance(product1, Product)
    assert product1.foo == 1
    assert product1.bar == 3
    assert product1 is product2


def test_object_provider():
    """Test an object provider."""
    expected = "teststring"

    class Container(injection.Container):
        product = injection.ObjectProvider(expected)

    ctx = Container()
    product1 = ctx.product
    product2 = ctx.product

    assert product1 is expected
    assert product2 is expected


def test_simple_dependency():
    """Test simple dependency declaration."""

    class A(injection.Component):
        b = injection.Dependency(feature="b")

    class Container:
        a = injection.SingletonProvider(A)
        b = injection.ObjectProvider(123)

    ctx = Container()
    result = ctx.a.b

    assert result == 123


def test_magic_dependency():
    """Test dependency feature name is automatically detected."""

    class A(injection.Component):
        b = injection.Dependency()

    class Container:
        a = injection.SingletonProvider(A)
        b = injection.ObjectProvider(123)

    ctx = Container()
    result = ctx.a.b

    assert result == 123


def test_override_dependency_name():
    """Test a dependency feature name can be overriden."""

    class A(injection.Component):
        b = 42
        c = injection.Dependency(feature="b")

    class Container:
        a = injection.SingletonProvider(A)
        b = injection.ObjectProvider(123)

    ctx = Container()
    result = ctx.a.c

    assert result == 123


def test_dependency_class_var():
    """Test getting a dependency on an uninitialized component."""

    class A(injection.Component):
        b = injection.Dependency()

    dep = A.b
    assert dep.feature == "b"


def test_dependency_not_configured():
    """Test getting a dependency that is not in the container."""

    class A(injection.Component):
        b = injection.Dependency()

    class Container:
        a = injection.SingletonProvider(A)

    container = Container()
    with pytest.raises(exceptions.InjectionError) as ctx:
        container.a.b

    assert ctx.value.args == ("Feature b not configured.",)


def test_infrastructure():
    """Test an infrastructure."""

    class A(injection.Component):
        config = injection.Infrastructure()

    class Container:
        a = injection.SingletonProvider(A)
        config = injection.ObjectProvider({"a": 1, "config": 2})

    ctx = Container()
    result = ctx.a.config
    assert result == 1


def test_infrastructure_class_var():
    """Test accessing an infrastructure on an uninitialized component."""

    class A(injection.Component):
        b = injection.Infrastructure()

    result = A.b
    assert result.feature == "b"
