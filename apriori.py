import time
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules
from algorithm import load_data_csv


def apriori_results(transactions, min_support=0.1, min_confidence=0.1):
    start_time = time.time()
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    df = pd.DataFrame(te_ary, columns=te.columns_)

    frequent_itemsets = apriori(df, min_support=min_support, use_colnames=True, max_len=3)


    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    end_time = time.time()

    covered_transactions = set()

    for i, transaction in enumerate(transactions):
        transaction_set = set(transaction)
        for _, rule in rules.iterrows():
            rule_items = set(rule['antecedents']) | set(rule['consequents'])
            if rule_items.issubset(transaction_set):
                covered_transactions.add(i)
                break

    coverage = len(covered_transactions) / len(transactions) if transactions else 0

    for _, rule in rules.iterrows():
        antecedent = ', '.join(rule['antecedents'])
        consequent = ', '.join(rule['consequents'])
        print(f"{{{antecedent}}} => {{{consequent}}}, "
            f"support={rule['support']:.4f}, confidence={rule['confidence']:.2f}")

    print(f"\n\nAPRIORI:\n")
    print('Liczba reguł: ', len(rules))
    print(f"Pokrycie zbioru przez reguły: {coverage:.2%}")
    print(f"Czas wykonania: {end_time - start_time:.2f} sekund")


transactions = load_data_csv("data/Groceries_dataset.csv")
apriori_results(transactions, 0.0008, 0.01)
# print(len(transactions))
# print(transactions[0])
