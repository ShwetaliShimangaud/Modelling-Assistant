from src.assistant import Assistant
import time


def test_assistant():
    domains = ['bank', 'car-maintenance', 'factory', 'library', 'production-cell-inheritance',
               'production-cell-enum', 'smart-city', 'sustainable-transportation']

    domains = ['flight-reservation']

    for domain_name in domains:
        start = time.time()
        assistant = Assistant(domain_name)
        assistant.run()

        end = time.time()
        print((end - start))
