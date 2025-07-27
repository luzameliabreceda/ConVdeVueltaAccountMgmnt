from injector import Injector, singleton


class GlobalDIContainer:
    
    def __init__(self):
        self.injector = Injector()
        self._configure_global_bindings()
    
    def _configure_global_bindings(self):
        pass
    
    def register_module_dependencies(self, module_name: str, bindings: list):
        for interface, implementation, scope in bindings:
            self.injector.binder.bind(interface, to=implementation, scope=scope)
    
    def get_injector(self):
        return self.injector


global_di_container = GlobalDIContainer() 