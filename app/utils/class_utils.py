class Injectable:
    """Clase base para todos las clases que pueden ser Inyectables."""
    pass

def inject(*service_classes):
    """
        Decorator para inyección de dependencias.

        Toma multiples tipos de clase como servicio, las cuales deben heredar de la Clase "Injectable"
        Cada clase que se presenta como servicio será inyectada e instanciada en la clase decorada con 'inject'
    """
    def decorator(cls):
        original_init = cls.__init__
        def new_init(self, *init_args, **init_kwargs):
            for service_cls in service_classes:
                if issubclass(service_cls, Injectable):
                    service_name = service_cls.__name__.lower()
                    setattr(self, service_name, service_cls())
                else:
                    raise TypeError(f"{service_cls.__name__} no es inyectable.")
            original_init(self, *init_args, **init_kwargs)
        cls.__init__ = new_init
        return cls
    return decorator