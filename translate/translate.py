from googletrans import Translator

def translate_to_croatian(text):
    translator = Translator()
    translated = translator.translate(text, dest='hr')
    return translated.text

print(translate_to_croatian("Hello, how are you?"))  # Prints: "Bok, kako si?"