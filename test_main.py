import pytest
from main import (
    count_itemsets,
    find_closed_frequent_itemsets,
    find_generators,
    generate_rules_from_generators,
    filter_rules
)

transactions = [
    ['bread', 'milk'],
    ['milk', 'butter'],
    ['bread', 'butter'],
    ['bread', 'milk', 'butter']
]

num_transactions = len(transactions)

transactions_doubled = [
    ['bread', 'milk'],
    ['milk', 'butter'],
    ['bread', 'butter'],
    ['butter', 'bread'],
    ['bread', 'milk', 'butter', 'butter']
]

num_transactions_double = len(transactions_doubled)

transactions_generators = [
    ['a', 'b'],
    ['a', 'b'],
    ['a', 'b', 'c'],
    ['a', 'b', 'c'],
    ['a', 'c'],
    ['c']
]

num_transactions_gens = len(transactions_generators)

min_support = 2

min_rule_support = 0.2


def test_count_itemsets():
    itemset_counts = count_itemsets(transactions)
    expected = {
        frozenset(['bread']): 3,
        frozenset(['milk']): 3,
        frozenset(['butter']): 3,
        frozenset(['bread', 'milk']): 2,
        frozenset(['bread', 'butter']): 2,
        frozenset(['milk', 'butter']): 2,
        frozenset(['bread', 'milk', 'butter']): 1,
    }
    for itemset, count in expected.items():
        assert itemset_counts[itemset] == count


def test_find_closed_frequent_itemsets():
    itemset_counts = count_itemsets(transactions)
    closed_itemsets = find_closed_frequent_itemsets(itemset_counts, min_support=1)
    closed_sets = [set(itemset) for itemset, _ in closed_itemsets]

    assert {'bread'} in closed_sets
    assert {'milk'} in closed_sets
    assert {'butter'} in closed_sets
    assert {'bread', 'milk'} in closed_sets
    assert {'bread', 'butter'} in closed_sets
    assert {'milk', 'butter'} in closed_sets
    assert {'bread', 'milk', 'butter'} in closed_sets
    assert len(closed_sets) == 7


def test_find_closed_frequent_itemsets_bigger_support():
    itemset_counts = count_itemsets(transactions)
    closed_itemsets = find_closed_frequent_itemsets(itemset_counts, min_support=2)
    closed_sets = [set(itemset) for itemset, _ in closed_itemsets]

    assert {'bread'} in closed_sets
    assert {'milk'} in closed_sets
    assert {'butter'} in closed_sets
    assert {'bread', 'milk'} in closed_sets
    assert {'bread', 'butter'} in closed_sets
    assert {'milk', 'butter'} in closed_sets
    assert {'bread', 'milk', 'butter'} not in closed_sets
    assert len(closed_sets) == 6


def test_find_closed_frequent_itemsets_double_set():
    itemset_counts = count_itemsets(transactions_doubled)
    closed_itemsets = find_closed_frequent_itemsets(itemset_counts, min_support=2)
    closed_sets = [set(itemset) for itemset, _ in closed_itemsets]

    assert {'bread'} in closed_sets
    assert {'milk'} in closed_sets
    assert {'butter'} in closed_sets
    assert {'bread', 'milk'} in closed_sets
    assert {'bread', 'butter'} in closed_sets
    assert {'milk', 'butter'} in closed_sets
    assert {'bread', 'milk', 'butter'} not in closed_sets
    assert len(closed_sets) == 6


def test_find_closed_frequent_itemsets_biggest_support():
    itemset_counts = count_itemsets(transactions)
    closed_itemsets = find_closed_frequent_itemsets(itemset_counts, min_support=3)
    closed_sets = [set(itemset) for itemset, _ in closed_itemsets]

    assert {'bread'} in closed_sets
    assert {'milk'} in closed_sets
    assert {'butter'} in closed_sets
    assert {'bread', 'milk'} not in closed_sets
    assert {'bread', 'butter'} not in closed_sets
    assert {'milk', 'butter'} not in closed_sets
    assert {'bread', 'milk', 'butter'} not in closed_sets
    assert len(closed_sets) == 3


def test_find_closed_frequent_itemsets_too_big_support():
    itemset_counts = count_itemsets(transactions)
    closed_itemsets = find_closed_frequent_itemsets(itemset_counts, min_support=4)
    closed_sets = [set(itemset) for itemset, _ in closed_itemsets]

    assert {'bread'} not in closed_sets
    assert {'milk'} not in closed_sets
    assert {'butter'} not in closed_sets
    assert {'bread', 'milk'} not in closed_sets
    assert {'bread', 'butter'} not in closed_sets
    assert {'milk', 'butter'} not in closed_sets
    assert {'bread', 'milk', 'butter'} not in closed_sets
    assert len(closed_sets) == 0


def test_find_closed_frequent_itemsets_transactions_with_generators():
    itemset_counts = count_itemsets(transactions_generators)
    closed_itemsets = find_closed_frequent_itemsets(itemset_counts, min_support=3)
    closed_sets = [set(itemset) for itemset, _ in closed_itemsets]

    assert {'a'} in closed_sets
    assert {'b'} not in closed_sets
    assert {'c'} in closed_sets
    assert {'a', 'b'} in closed_sets
    assert {'a', 'c'} in closed_sets
    assert {'b', 'c'} not in closed_sets
    assert {'a', 'b', 'c'} not in closed_sets
    assert len(closed_sets) == 4


def test_find_generators_empty():
    itemset_counts = count_itemsets(transactions)
    closed_itemsets = find_closed_frequent_itemsets(itemset_counts, min_support)
    generators = find_generators(closed_itemsets, itemset_counts, num_transactions)

    for closed_set in generators:
        assert len(generators[closed_set]) == 0


def test_find_generators():
    itemset_counts = count_itemsets(transactions_generators)
    closed_itemsets = find_closed_frequent_itemsets(itemset_counts, min_support=3)
    generators = find_generators(closed_itemsets, itemset_counts, num_transactions_gens)

    key = frozenset(['a', 'b'])
    assert key in generators
    gen_sets = generators[key]

    for closed_set in generators:
        if closed_set != frozenset(['a', 'b']):
            assert len(generators[closed_set]) == 0
        else:
            assert frozenset(['b']) in generators[closed_set]
            assert len(generators[closed_set]) == 1


def test_generate_rules_from_generators_empty():
    itemset_counts = count_itemsets(transactions)
    closed_itemsets = find_closed_frequent_itemsets(itemset_counts, min_support=2)
    generators = find_generators(closed_itemsets, itemset_counts, num_transactions)
    rules = generate_rules_from_generators(generators, closed_itemsets, itemset_counts, num_transactions)

    assert len(rules) == 0


def test_generate_rules_from_generators():
    itemset_counts = count_itemsets(transactions_generators)
    closed_itemsets = find_closed_frequent_itemsets(itemset_counts, min_support=2)
    generators = find_generators(closed_itemsets, itemset_counts, num_transactions_gens)
    rules = generate_rules_from_generators(generators, closed_itemsets, itemset_counts, num_transactions_gens)

    assert len(rules) == 2
    assert rules[0]['generator'] == frozenset(['b'])
    assert rules[0]['consequent'] == frozenset(['a'])
    assert rules[0]['support'] == 4/6
    assert rules[0]['confidence'] == 1
    assert rules[1]['generator'] == frozenset(['b', 'c'])
    assert rules[1]['consequent'] == frozenset(['a'])
    assert rules[1]['support'] == 2/6
    assert rules[1]['confidence'] == 1


def test_generate_rules_from_generators_bigger_support():
    itemset_counts = count_itemsets(transactions_generators)
    closed_itemsets = find_closed_frequent_itemsets(itemset_counts, min_support=3)
    generators = find_generators(closed_itemsets, itemset_counts, num_transactions_gens)
    rules = generate_rules_from_generators(generators, closed_itemsets, itemset_counts, num_transactions_gens)

    assert len(rules) == 1
    assert rules[0]['generator'] == frozenset(['b'])
    assert rules[0]['consequent'] == frozenset(['a'])
    assert rules[0]['support'] == 4/6
    assert rules[0]['confidence'] == 1


def test_filter_rules_big_support_small_rule_support():
    itemset_counts = count_itemsets(transactions_generators)
    closed_itemsets = find_closed_frequent_itemsets(itemset_counts, min_support=3)
    generators = find_generators(closed_itemsets, itemset_counts, num_transactions_gens)
    rules = generate_rules_from_generators(generators, closed_itemsets, itemset_counts, num_transactions_gens)
    filtered = filter_rules(rules, min_rule_support, min_confidence=0.5)

    assert len(filtered) == 1
    assert filtered[0]['generator'] == frozenset(['b'])
    assert filtered[0]['consequent'] == frozenset(['a'])
    assert filtered[0]['support'] == 4/6
    assert filtered[0]['confidence'] == 1


def test_filter_rules_big_support_big_rule_support():
    itemset_counts = count_itemsets(transactions_generators)
    closed_itemsets = find_closed_frequent_itemsets(itemset_counts, min_support=3)
    generators = find_generators(closed_itemsets, itemset_counts, num_transactions_gens)
    rules = generate_rules_from_generators(generators, closed_itemsets, itemset_counts, num_transactions_gens)
    filtered = filter_rules(rules, min_support=0.9, min_confidence=0.5)

    assert len(filtered) == 0


def test_filter_rules_small_support():
    itemset_counts = count_itemsets(transactions_generators)
    closed_itemsets = find_closed_frequent_itemsets(itemset_counts, min_support=2)
    generators = find_generators(closed_itemsets, itemset_counts, num_transactions_gens)
    rules = generate_rules_from_generators(generators, closed_itemsets, itemset_counts, num_transactions_gens)

    assert len(rules) == 2

    filtered = filter_rules(rules, min_support=0.01, min_confidence=0.5)

    assert len(filtered) == 1
    assert filtered[0]['generator'] == frozenset(['b'])
    assert filtered[0]['consequent'] == frozenset(['a'])
    assert filtered[0]['support'] == 4/6
    assert filtered[0]['confidence'] == 1
