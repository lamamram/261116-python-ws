# %%
print("bonjour")

# %%

print("les gens")

# %% ------------------ introspection --------------------

import inspect

def func(param: int = 10) -> str:
    return str(param)

print(func.__annotations__)

sign = inspect.signature(func)
# accéder aux valeurs par défaut
print(sign.parameters["param"].default)

# %%
