import sys
import types

# --- QUICK FIX FOR RAGAS BREAKING IMPORT ---
dummy_chat = types.ModuleType("langchain_community.chat_models.vertexai")
dummy_chat.ChatVertexAI = type("ChatVertexAI", (object,), {})
sys.modules["langchain_community.chat_models.vertexai"] = dummy_chat

import langchain_community.llms
langchain_community.llms.VertexAI = type("VertexAI", (object,), {})
# --------------------------------------------

# Now your standard imports will work without crashing
import ragas
print(ragas.__version__)
