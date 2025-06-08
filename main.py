import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations
from collections import defaultdict

# === 1. Wczytywanie danych ===
def load_transactions(filepath):
    df = pd.read_csv(filepath)
    transactions = df.groupby('Transaction')['Item'].apply(set).tolist()
    return transactions

# === 2. Obliczanie supportu ===
def get_support(itemset, transactions):
    return sum(1 for transaction in transactions if itemset.issubset(transaction)) / len(transactions)

# === 3. Generowanie częstych zbiorów ===
def get_frequent_itemsets(transactions, min_support=0.02):
    itemsets = defaultdict(int)
    for transaction in transactions:
        for i in range(1, len(transaction)+1):
            for subset in combinations(transaction, i):
                itemsets[frozenset(subset)] += 1

    num_transactions = len(transactions)
    frequent = {k: v/num_transactions for k, v in itemsets.items() if v/num_transactions >= min_support}
    return frequent

# === 4. Zamknięte zbiory ===
def get_closed_itemsets(frequent_itemsets):
    closed = {}
    for itemset in frequent_itemsets:
        is_closed = True
        for other in frequent_itemsets:
            if itemset < other and frequent_itemsets[itemset] == frequent_itemsets[other]:
                is_closed = False
                break
        if is_closed:
            closed[itemset] = frequent_itemsets[itemset]
    return closed

# === 5. Generatory ===
def get_generators(closed_itemsets, frequent_itemsets):
    generators = defaultdict(list)
    for closed in closed_itemsets:
        for itemset in frequent_itemsets:
            if itemset.issubset(closed) and frequent_itemsets[itemset] == closed_itemsets[closed]:
                is_minimal = all(not other.issubset(itemset) or other == itemset for other in frequent_itemsets if frequent_itemsets[other] == closed_itemsets[closed])
                if is_minimal:
                    generators[closed].append(itemset)
    return generators

# === 6. Reguły ===
def generate_non_redundant_rules(closed_itemsets, generators, transactions):
    rules = []
    for closed, gens in generators.items():
        for gen in gens:
            consequent = closed - gen
            if consequent:
                support = get_support(closed, transactions)
                confidence = support / get_support(gen, transactions)
                rules.append({
                    'antecedent': set(gen),
                    'consequent': set(consequent),
                    'support': support,
                    'confidence': confidence
                })
    return rules

# === 7. Wizualizacja ===
def plot_top_items(frequent_itemsets, top_n=10):
    single_items = {list(k)[0]: v for k, v in frequent_itemsets.items() if len(k) == 1}
    top_items = dict(sorted(single_items.items(), key=lambda x: x[1], reverse=True)[:top_n])
    plt.figure(figsize=(8, 5))
    sns.barplot(x=list(top_items.values()), y=list(top_items.keys()), palette="viridis")
    plt.title(f"Top {top_n} najczęstszych produktów")
    plt.xlabel("Support")
    plt.ylabel("Produkt")
    plt.tight_layout()
    plt.show()

def plot_rules(rules):
    plt.figure(figsize=(8, 6))
    supports = [r['support'] for r in rules]
    confidences = [r['confidence'] for r in rules]
    plt.scatter(supports, confidences, alpha=0.6, edgecolor='k')
    plt.title("Reguły asocjacyjne: confidence vs support")
    plt.xlabel("Support")
    plt.ylabel("Confidence")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# === 8. Uruchomienie ===
if __name__ == "__main__":
    filepath = 'example_groceries.csv'

    transactions = load_transactions(filepath)
    frequent_itemsets = get_frequent_itemsets(transactions, min_support=0.05)
    closed_itemsets = get_closed_itemsets(frequent_itemsets)
    generators = get_generators(closed_itemsets, frequent_itemsets)
    rules = generate_non_redundant_rules(closed_itemsets, generators, transactions)

    plot_top_items(frequent_itemsets)
    plot_rules(rules)

    # Wyświetl 5 przykładowych reguł
    for rule in rules[:5]:
        print(f"{rule['antecedent']} => {rule['consequent']}, "
              f"support: {rule['support']:.3f}, confidence: {rule['confidence']:.3f}")
