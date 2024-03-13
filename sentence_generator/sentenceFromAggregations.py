from typing import List

from abstractSentenceGenerator import AbstractSentenceGenerator

class SentenceFromAggregation(AbstractSentenceGenerator):
    def __init__(self, aggregations):
        self.aggregations = aggregations
        self.sentences = []
        self.generate_sentences()

    def get_sentences(self) -> List[str]:
        return self.sentences

    def generate_sentences(self):
        pass



