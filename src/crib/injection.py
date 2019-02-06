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

  class Container(object):
      repository = SingletonProvider(Repository)
      myService = SingletonProvider(MyService)

  c = Container()

When a feature is requested from the container, the provider will supply an
instance of the component it is configured with. The same mechanism is used for
when a component accesses a dependency. The dependency injection is lazy::

  myService = c.myService
  assert 42 == myService.print_count()

"""
import itertools

from crib import config as _cfg
from crib import exceptions, plugin_loader


class AbstractProvider(object):
    def __init__(self):
        super(AbstractProvider, self).__init__()
        self.feature = None

    def __set_name__(self, owner, name):
        self.feature = name

    def __get__(self, container, T):
        raise NotImplementedError()


class FactoryProvider(AbstractProvider):
    def __init__(self, component_class, *args, **kwargs):
        super(FactoryProvider, self).__init__()
        self._component_class = component_class
        self._args = args
        self._kwargs = kwargs

    def __get__(self, container, T):
        return self._component_class(
            self.feature, container, *self._args, **self._kwargs
        )


class SingletonProvider(FactoryProvider):
    def __init__(self, *args, **kwargs):
        super(SingletonProvider, self).__init__(*args, **kwargs)
        self._instance = None

    def __get__(self, container, T):
        self._instance = self._instance or super(SingletonProvider, self).__get__(
            container, T
        )
        return self._instance


class ObjectProvider(AbstractProvider):
    def __init__(self, obj):
        super(ObjectProvider, self).__init__()
        self.obj = obj

    def __get__(self, container, T):
        return self.obj


class PluginsProvider(AbstractProvider):
    def __init__(self, hook):
        super(PluginsProvider, self).__init__()
        self._hook = hook
        self._plugins = None

    def __get__(self, container, T):
        if self._plugins is None:
            self._plugins = self._load_plugins(container)
        return self._plugins

    def _load_plugins(self, container):
        plugins = [plugin for plugins in self._hook() for plugin in plugins]
        return plugins


class ConfiguredPluginProvider(PluginsProvider):
    def __init__(self, hook):
        super(ConfiguredPluginProvider, self).__init__(hook)
        self._component = None

    def __get__(self, container, T):
        if self._component is None:
            plugins = super(ConfiguredPluginProvider, self).__get__(container, T)
            self._component = self._load_component(container, plugins)
        return self._component

    def _load_component(self, container, plugins):
        plugin_config = container.config[self.feature].copy()
        plugin_type = plugin_config.pop("type")
        for plugin in plugins:
            if plugin.name() == plugin_type:
                return plugin(self.feature, container)
        raise exceptions.PluginNotFound(f"{plugin_type} plugin not found")


class Component(object):
    def __init__(self, name, container):
        super(Component, self).__init__()
        self.name = name
        print("asdf", self)
        self._container = container


class Dependency(object):
    def __init__(self, feature=None):
        super(Dependency, self).__init__()
        self.feature = feature

    def __set_name__(self, owner, name):
        self.feature = self.feature or name

    def __get__(self, component, T):
        if component is None:
            return self

        return getattr(component._container, self.feature)


class Infrastructure(Dependency):
    def __get__(self, component, T):
        return super(Infrastructure, self).__get__(component, T)[component.name]


class Ui(Component):
    config = Infrastructure()
    app = Dependency("app")

    def main(self):
        print(self.config.get("cool"))
        print(self.app())
        print(self.app())
        print(self.app())


class App(Component):
    propertyService = Dependency("propertyService")

    def __call__(self):
        return self.propertyService.get_shit()


class PropertyService(Component):
    propertyRepo = Dependency("propertyRepo")

    def get_shit(self):
        return self.propertyRepo.shit()


class PropertyRepo(Component):
    def shit(self):
        return "shit"


class Configuration(Component):
    configLoaders = Dependency()

    def __init__(self, name, container, configfile):
        super(Configuration, self).__init__(name, container)
        self._cfg = None
        self._configfile = configfile

    def __getitem__(self, key):
        if self._cfg is None:
            self._cfg = self.load()
        return self._cfg[key]

    def load(self):
        default = _cfg.load_default(self.configLoaders)
        user_cfg = _cfg.load(self.configLoaders, self._configfile)
        cfg = _cfg.merge_config(default, user_cfg)
        return cfg


class C(object):
    propertyService = SingletonProvider(PropertyService)
    propertyRepo = SingletonProvider(PropertyRepo)
    app = SingletonProvider(App)
    ui = SingletonProvider(Ui)
    config = SingletonProvider(Configuration, open("config.yaml", "r"))
    configLoaders = PluginsProvider(plugin_loader.hook.crib_add_config_loaders)

    property_repository = ConfiguredPluginProvider(
        plugin_loader.hook.crib_add_property_repos
    )
    user_repository = ConfiguredPluginProvider(plugin_loader.hook.crib_add_user_repos)
    directions_repository = ConfiguredPluginProvider(
        plugin_loader.hook.crib_add_directions_repos
    )
    directions_service = ConfiguredPluginProvider(
        plugin_loader.hook.crib_add_directions_services
    )


c = C()
ui = c.ui
ui.main()
print(c.directions_repository)
