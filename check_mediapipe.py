import mediapipe as mp
import importlib.util
print('version:', mp.__version__)
print('has mediapipe.tasks.python:', importlib.util.find_spec('mediapipe.tasks.python') is not None)
