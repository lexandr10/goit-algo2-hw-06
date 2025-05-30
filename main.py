import requests
import matplotlib, matplotlib.pyplot as plt
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import re

matplotlib.use('Agg')


def download_text(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def preprocess_text(text: str) -> str:

    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text

def map_function(chunk: str) :
    words = chunk.split()
    return [(word, 1) for word in words if word]

def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()

def reduce_function(shuffled_values):
    reduced = {}
    for key, values in shuffled_values:
        reduced[key] = sum(values)
    return reduced

def chunk_text(text:str, n_chunks:int) :
    words = text.split()
    chunk_size = len(words) // n_chunks
    return [" ".join(words[i * chunk_size:(i + 1) * chunk_size]) for i in range(n_chunks)]

def map_reduce(text: str, n_threads: int = 4):
    chunks = chunk_text(text, n_threads)

    with ThreadPoolExecutor(max_workers=n_threads) as executor:
        mapped_lists = list(executor.map(map_function, chunks))

        all_mapped = [item for sublist in mapped_lists for item in sublist]

        shuffled = shuffle_function(all_mapped)

        reduced = reduce_function(shuffled)

    return reduced

def visualize_top_words(word_counts: dict, top_n: int = 10):
    top_items = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    words, counts = zip(*top_items)

    plt.figure(figsize=(10, 6))
    plt.bar(words, counts, color='skyblue')
    plt.title(f"Топ-{top_n} найчастіших слів")
    plt.xlabel("Слова")
    plt.ylabel("Кількість")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("top_words.png")
    print("Графік збережено у файл 'top_words.png'")
if __name__ == '__main__':
    # URL з текстом (можеш замінити на інший за потреби)
    url = 'https://www.gutenberg.org/files/1342/1342-0.txt'  # "Pride and Prejudice" by Jane Austen

    print("Завантаження тексту...")
    raw_text = download_text(url)

    print("Попередня обробка тексту...")
    clean_text = preprocess_text(raw_text)

    print("Виконання MapReduce...")
    word_counts = map_reduce(clean_text, n_threads=6)

    print("Візуалізація результатів...")
    visualize_top_words(word_counts, top_n=15)