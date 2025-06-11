import argparse
import json
import time
import os
from algorithm import(
    load_data_csv, load_data_txt, count_itemsets,
    find_closed_frequent_itemsets, find_generators,
    generate_rules_from_generators, filter_rules,
    calculate_coverage
)


def load_parameters(filepath='parameters.json'):
    with open(filepath, 'r') as f:
        return json.load(f)


def save_results(rules, statistics_path, output_path, stats):
    os.makedirs(os.path.dirname(statistics_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        for rule in rules:
            line = f"{rule['generator']} => {rule['consequent']}, " \
                   f"support={rule['support']:.4f}, confidence={rule['confidence']:.2f}"
            f.write(line + '\n')

    with open(statistics_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=4)


def main():
    parser = argparse.ArgumentParser(description="Tworzenie nieredundantnych reguł asocjacyjnych")
    parser.add_argument('--input', type=str, help='Ścieżka do pliku wejściowego (CSV lub TXT)')
    parser.add_argument('--output', type=str, default='results/output.txt', help='Ścieżka do pliku wynikowego')
    args = parser.parse_args()

    params = load_parameters()
    input_path = args.input
    output_path = args.output
    stats_path = 'results/statistics.json'

    if not input_path:
        raise ValueError("Musisz podać ścieżkę do pliku wejściowego za pomocą --input")

    if input_path.endswith('.csv'):
        transactions = load_data_csv(input_path)
    elif input_path.endswith('.txt'):
        transactions = load_data_txt(input_path)
    else:
        raise ValueError("Plik wejściowy musi być w formacie .csv lub .txt")

    num_transactions = len(transactions)

    start_time = time.time()

    itemset_counts = count_itemsets(transactions)
    closed_itemsets = find_closed_frequent_itemsets(itemset_counts, params['min_support'])
    generators = find_generators(closed_itemsets, itemset_counts, num_transactions, params['epsilon'])
    rules = generate_rules_from_generators(generators, closed_itemsets, itemset_counts, num_transactions)
    final_rules = filter_rules(rules, params['min_rule_support'], params['min_confidence'])

    end_time = time.time()
    execution_time = end_time - start_time
    coverage = calculate_coverage(final_rules, transactions)

    stats = {
        "min_support": params['min_support'],
        "min_rule_support": params['min_rule_support'],
        "min_confidence": params['min_confidence'],
        "epsilon": params['epsilon'],
        "rules_count": len(final_rules),
        "coverage": round(coverage, 4),
        "execution_time_sec": round(execution_time, 2)
    }

    for rule in final_rules:
        print(f"{rule['generator']} => {rule['consequent']}, "
              f"support={rule['support']}, confidence={rule['confidence']:.2f}")

    print(f"Liczba reguł: {len(final_rules)}")
    print(f"Pokrycie zbioru przez reguły: {coverage:.2%}")
    print(f"Czas wykonania: {execution_time:.2f} sekund")

    save_results(final_rules, stats_path, output_path, stats)


if __name__ == "__main__":
    main()
