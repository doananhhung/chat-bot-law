from langchain_groq import ChatGroq
import inspect

print("Các tham số của ChatGroq.__init__:")
sig = inspect.signature(ChatGroq.__init__)
for name, param in sig.parameters.items():
    print(f"- {name}: {param.annotation}")
