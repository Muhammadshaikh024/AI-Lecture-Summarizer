def generate_quiz_questions(keywords: list[str]) -> list[str]:
    questions = []
    templates = [
        "What is {k}?",
        "Explain {k} in the context of AI lecture content.",
        "Why is {k} important?",
        "Give an example related to {k}.",
    ]

    for kw in keywords:
        for t in templates:
            q = t.format(k=kw)
            if q not in questions:
                questions.append(q)
            if len(questions) >= 10:
                return questions

    return questions[:10]