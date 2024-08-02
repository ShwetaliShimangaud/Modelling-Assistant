from src.assistant import Assistant
import time


def test_assistant():
    start = time.time()
    domain_name = "production-cell-inheritance"
    assistant = Assistant(domain_name)
    assistant.run()

    end = time.time()
    print((end - start))
