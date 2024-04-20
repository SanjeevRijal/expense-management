from model import *


def bill_detail():
    """this will calculate how much each person spend in total"""
    all_individual_bill_amounts = {}
    bills = Bill.query.all()

    for bill in bills:
        spender_name = bill.what_amount.name
        if spender_name not in all_individual_bill_amounts:
            all_individual_bill_amounts[spender_name] = [bill.amount]
        else:
            all_individual_bill_amounts[spender_name].append(bill.amount)

    user_spend = {keys:sum(value) for keys, value in all_individual_bill_amounts.items()}
    return user_spend


def bill_share_with():
    """this will calculate how much each person is liable to pay"""

    individual_bill_sharing_details = {}
    bill_amount_to_share = {}
    split_amount_per_bill_id = {}
    to_share_amounts = {}

    split_bills = Split.query.all()

    for split_bill in split_bills:
        sharing_name = split_bill.split_among.name
        if split_bill.bill_id not in individual_bill_sharing_details:
            individual_bill_sharing_details[split_bill.bill_id] = [sharing_name]
        else:
            individual_bill_sharing_details[split_bill.bill_id].append(sharing_name)

        if split_bill.bill_id not in bill_amount_to_share:
            bill_amount_to_share[split_bill.bill_id] = split_bill.bill_detail.amount

    how_many_splits_bills = {f'{keys}':len(value) for keys, value in individual_bill_sharing_details.items()}

    for keys, value in how_many_splits_bills.items():
        for keys1, value1 in bill_amount_to_share.items():
            if int(keys) == int(keys1):
                split_amount_per_bill_id[keys] = float(value1/value)

    for key, sharing_with in individual_bill_sharing_details.items():
        for split_key, split_amount in split_amount_per_bill_id.items():
            if int(key) == int(split_key):
                for each in sharing_with:
                    if each not in to_share_amounts:
                        to_share_amounts[each] = [split_amount]
                    else:
                        to_share_amounts[each].append(split_amount)

    to_pay_final = {keys:sum(value) for keys, value in to_share_amounts.items()}
    return to_pay_final
