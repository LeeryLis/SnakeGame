class SignalBus:
    _signals = {}

    @staticmethod
    def subscribe(signal_name, callback):
        if signal_name not in SignalBus._signals:
            SignalBus._signals[signal_name] = []
        SignalBus._signals[signal_name].append(callback)

    @staticmethod
    def emit(signal_name, *args, **kwargs):
        if signal_name in SignalBus._signals:
            for callback in SignalBus._signals[signal_name]:
                callback(*args, **kwargs)
