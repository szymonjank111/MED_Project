import pandas as pd
from itertools import combinations
from collections import defaultdict


def load_data_txt(path):
    with open(path, 'r') as file:
        transactions = [line.strip().split(',') for line in file]
    return transactions


def load_data_csv(path):
    df = pd.read_csv(path, sep=',')
    grouped = df.groupby(['Member_number', 'Date'])['itemDescription'].apply(list)
    transactions = grouped.tolist()
    return transactions


def count_itemsets(transactions):
    itemset_counts = defaultdict(int)
    for transaction in transactions:
        transaction = set(transaction)
        for r in range(1, len(transaction) + 1):
            for combo in combinations(transaction, r):
                itemset_counts[frozenset(combo)] += 1
    return itemset_counts


def find_closed_frequent_itemsets(itemset_counts, min_support):
    frequent_itemsets = {
        itemset: count for itemset, count in itemset_counts.items()
        if count >= min_support
    }

    closed_itemsets = []
    for itemset, support in frequent_itemsets.items():
        is_closed = True
        for other_itemset, other_support in frequent_itemsets.items():
            if itemset < other_itemset and support == other_support:
                is_closed = False
                break
        if is_closed:
            closed_itemsets.append((set(itemset), support))
    return closed_itemsets


def find_generators(closed_itemsets, itemset_counts, num_transactions, epsilon = 0):
    generators = dict()

    for closed_set, closed_support in closed_itemsets:
        closed_fset = frozenset(closed_set)
        candidate_generators = [
            frozenset(subset)
            for r in range(1, len(closed_set))
            for subset in combinations(closed_set, r)
            if (itemset_counts.get(frozenset(subset), 0) - closed_support) / num_transactions <= epsilon
        ]

        minimal_generators = []
        for g in candidate_generators:
            if not any(other < g for other in candidate_generators if other != g):
                minimal_generators.append(g)

        generators[closed_fset] = minimal_generators

    return generators


def generate_rules_from_generators(generators, closed_itemsets, itemset_counts, num_transactions):
    rules = []
    support_lookup = {
        frozenset(itemset): support for itemset, support in closed_itemsets
    }

    for closed_fset, gens in generators.items():
        closed_support = support_lookup[closed_fset]

        for gen in gens:
            consequent = closed_fset - gen
            if consequent:
                gen_support = itemset_counts.get(gen, 0)
                confidence = closed_support / gen_support if gen_support > 0 else 0

                rules.append({
                    'generator': set(gen),
                    'consequent': set(consequent),
                    'support': closed_support / num_transactions,
                    'confidence': confidence
                })
    return rules


def filter_rules(rules, min_support=1.0, min_confidence=0.0):
    filtered = [
        r for r in rules
        if r['support'] >= min_support and r['confidence'] >= min_confidence
    ]

    non_redundant = []
    for r1 in filtered:
        redundant = False
        for r2 in filtered:
            if r1 == r2:
                continue

            if (r2['generator'].issubset(r1['generator']) and
                r1['consequent'] == r2['consequent'] and
                r1['confidence'] <= r2['confidence']):
                redundant = True
                break

            if (r1['generator'] == r2['consequent'] and
                r1['consequent'] == r2['generator']):
                if r1['confidence'] <= r2['confidence']:
                    redundant = True
                    break

        if not redundant:
            non_redundant.append(r1)

    return non_redundant


def calculate_coverage(rules, transactions):
    covered_transactions = set()

    for i, transaction in enumerate(transactions):
        transaction_set = set(transaction)
        for rule in rules:
            rule_items = rule['generator'] | rule['consequent']
            if rule_items.issubset(transaction_set):
                covered_transactions.add(i)
                break

    coverage = len(covered_transactions) / len(transactions) if transactions else 0
    return coverage