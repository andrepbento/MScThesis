class Dictionary(dict):

    @staticmethod
    def update_dict(dictionary, key, func=None):
        if not isinstance(dictionary, dict) and func is None:
            return

        for k, v in dictionary.items():
            if k == key:
                dictionary[k] = func(v)
            elif isinstance(v, list):
                for item in v:
                    Dictionary.update_dict(item, key, func)
