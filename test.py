from nlprule import Tokenizer, Rules

tokenizer = Tokenizer.load("en")
rules = Rules.load("en", tokenizer)

# Example ESL writing errors
esl_errors = [
    "I want her to go to the school from the home.",
    "He don't like to study.",
    "She is my best of friend.",
    "I am going to shopping.",
    "The weather is very nice, isn't it?",
]

for sentence in esl_errors:
    suggestions = rules.correct(sentence)

    print(f"Original Sentence: {sentence}")
    print("Suggestions:")
    print(rules.correct(sentence))
    print("\n" + "-"*40 + "\n")
