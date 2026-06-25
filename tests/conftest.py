import os

# Override Settings for unit/integration tests to default to Gemini (which are mocked).
# This avoids breaking existing tests that expect the Gemini client to be called and mocked.
os.environ["USE_OLLAMA"] = "false"
