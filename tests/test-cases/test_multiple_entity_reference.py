import spacy


def test_multiple_entity_reference():
    library = """The system to build is an automated library book borrowing system that is to be used in the departmental libraries of a university. The goal is to relieve the librarians from processing book loans.
The system does not require users to identify themselves to search for books according to certain criteria and to check the availability of a particular book. However, to check-out books, to check their respective book loan status, and to place holds on books that are already on loan, users must first identify themselves to the system.
A single receipt is printed for each user check-out session; it details for each book: the title of the book, the unique identifier of the book, the date the book was borrowed, and the date the book is to be returned by. At the start of each week, the system sends warning emails to all borrowers that have overdue books. All information about what category of member a user belongs to (see borrowing rules below), his/her email address, etc. is available from the central university server. Books have physically attached barcodes, which are used for the identification of books that are checked out (a barcode scanner is to be used). If the book does not scan, it should be also possible to enter the barcode manually. Book renewals (i.e., extending the due date) are not supported in the current version of the system, but this feature is planned for a later release. It is perceived as an important feature to be supported via the web.
These are the borrowing rules:
• Each user has a maximum number of books that are allowed to be on loan at any one time. The limit is dependent on the category of the member, e.g. Department Heads can take out as many as 100 books, where Research Assistants are limited to 15 books.
• Often, a certain category of book has a different loan period for each category of member, e.g. Professors are allowed to borrow a standard book for 6 months, whereas Graduate Students are allowed only 3 months.
• Different categories of books have different loan periods (e.g., Lecturers may borrow a standard book for 3 months, but can only loan a periodical for 1 month). It might even not be possible, for a certain category of member, to borrow certain books (e.g. Undergraduate Students cannot borrow reference books).
• Books that are on reserve are not available for loan.
"""

    language_model = spacy.load("en_core_web_trf")

    # Process the text
    doc = language_model(library)

    # Extract noun pairs that might refer to the same entity
    potential_pairs = []

    for token1 in doc:
        if token1.pos_ == "NOUN" or token1.pos_ == "PROPN":
            for token2 in doc:
                if token2.pos_ == "NOUN" or token2.pos_ == "PROPN":
                    if token1.text != token2.text and token1.similarity(token2) > 0.7:
                        potential_pairs.append((token1.text, token2.text))

    # Filter for unique pairs
    unique_pairs = list(set(potential_pairs))

    # Output the unique pairs
    for pair in unique_pairs:
        print(pair)

    res = language_model(library)

    for token in res:
        print(token)

    print(res)


import spacy
import coreferee

# Load the SpaCy model with coreferee
nlp = spacy.load("en_core_web_trf")
nlp.add_pipe("coreferee")

# The provided text
text = """
The system to build is an automated library book borrowing system that is to be used in the departmental libraries of a university. The goal is to relieve the librarians from processing book loans.
The system does not require users to identify themselves to search for books according to certain criteria and to check the availability of a particular book. However, to check-out books, to check their respective book loan status, and to place holds on books that are already on loan, users must first identify themselves to the system.
A single receipt is printed for each user check-out session; it details for each book: the title of the book, the unique identifier of the book, the date the book was borrowed, and the date the book is to be returned by. At the start of each week, the system sends warning emails to all borrowers that have overdue books. All information about what category of member a user belongs to (see borrowing rules below), his/her email address, etc. is available from the central university server. Books have physically attached barcodes, which are used for the identification of books that are checked out (a barcode scanner is to be used). If the book does not scan, it should be also possible to enter the barcode manually. Book renewals (i.e., extending the due date) are not supported in the current version of the system, but this feature is planned for a later release. It is perceived as an important feature to be supported via the web.
These are the borrowing rules:
• Each user has a maximum number of books that are allowed to be on loan at any one time. The limit is dependent on the category of the member, e.g. Department Heads can take out as many as 100 books, where Research Assistants are limited to 15 books.
• Often, a certain category of book has a different loan period for each category of member, e.g. Professors are allowed to borrow a standard book for 6 months, whereas Graduate Students are allowed only 3 months.
• Different categories of books have different loan periods (e.g., Lecturers may borrow a standard book for 3 months, but can only loan a periodical for 1 month). It might even not be possible, for a certain category of member, to borrow certain books (e.g. Undergraduate Students cannot borrow reference books).
• Books that are on reserve are not available for loan.
"""

# Process the text
doc = nlp(text)


def testtt():
    # Perform coreference resolution and print the clusters

    for chain in doc._.coref_chains:
        print(f"Cluster: {chain}")
        for mention in chain:
            print(f" - {mention.pretty_representation}")

        print()
