verb_tags = ['VB', 'VBZ', 'VBP', 'VBN', 'VBG', 'VBD']

singular_cardinality_to_article_map = {
    '1': 'exactly one',
    '*': 'Many+pl'
}

# ToDo Enhance to include all the rules from the paper
# multiple_cardinality_to_article_map = {
#     '0..*': 'Zero or many+pl',
#     '1..*': 'One or many+pl',
# }
multiple_cardinality_to_article_map = {
    '0..*': 'zero or multiple+pl',
    '1..*': 'at least one or more',
    '2,3,...,n': 'Two,three,....,many+pl',
}

noun_tags = ['NN', 'NNS', 'NNP', 'NNPS']