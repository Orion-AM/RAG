import pkg_resources
import sys

print("Python version:", sys.version)
print("Installed packages:")
for d in pkg_resources.working_set:
    if "langch" in d.key:
        print(f"{d.key}=={d.version}")

try:
    import langchain
    print(f"langchain path: {langchain.__file__}")
    print(f"langchain dir: {dir(langchain)}")
except ImportError as e:
    print(f"ImportError: {e}")

try:
    import langchain.chains
    print("langchain.chains imported successfully")
except ImportError as e:
    print(f"langchain.chains ImportError: {e}")
