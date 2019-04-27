"""Module for dependency injection.

This allows a component to declare dependencies on a feature that other
components can implement::

  class MyService(Component):
      repository = Dependency()

      def print_count(self):
          print(self.repository.count())

  class Repository(Component):
      def count(self):
          return 42

To configure the dependency injection, a container is created with a provider
for each feature::

  class Container():
      repository = SingletonProvider(Repository)
      myService = SingletonProvider(MyService)

  c = Container()

When a feature is requested from the container, the provider will supply an
instance of the component it is configured with. The same mechanism is used for
when a component accesses a dependency. The dependency injection is lazy::

  myService = c.myService
  assert 42 == myService.print_count()

"""
import abc
from typing import Any, Type, TypeVar, Union

from crib.exceptions import InjectionError


class Container:
    pass


class Component:
    """A basic object that can either depend on or implement a feature."""

    def __init__(self, name, container, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self._container = container


CT = TypeVar("CT", bound=Component)


class AbstractProvider(metaclass=abc.ABCMeta):
    """Provide a component for a feature."""

    def __init__(self):
        super().__init__()
        self.feature: str = None

    def __set_name__(self, owner, name: str):
        self.feature = name

    @abc.abstractmethod
    def __get__(self, container: Container, T) -> Any:  # pragma: no cover
        """Return a component for the requested feature."""
        raise NotImplementedError()


class FactoryProvider(AbstractProvider):
    def __init__(self, component_class: Type[CT], *args, **kwargs):
        super().__init__()
        self._component_class = component_class
        self._args = args
        self._kwargs = kwargs

    def __get__(self, container: Container, T) -> Component:
        return self._component_class(
            self.feature, container, *self._args, **self._kwargs
        )


class SingletonProvider(FactoryProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._instance = None

    def __get__(self, container: Container, T) -> Component:
        self._instance = self._instance or super().__get__(container, T)
        return self._instance


class ObjectProvider(AbstractProvider):
    def __init__(self, obj: Any):
        super().__init__()
        self.obj = obj

    def __get__(self, container, T) -> Any:
        return self.obj


class Dependency:
    def __init__(self, feature: Union[None, str] = None):
        super().__init__()
        self.feature = feature

    def __set_name__(self, owner, name: str):
        self.feature = self.feature or name

    def __get__(self, component, T):
        if component is None:
            return self

        try:
            return getattr(component._container, self.feature)
        except AttributeError:
            raise InjectionError(f"Feature {self.feature} not configured.")


class Infrastructure(Dependency):
    def __get__(self, component, T):
        if component is None:
            return self

        return super().__get__(component, T)[component.name]
