import os
import time
import json
import requests
import datetime

from multiprocessing.pool import ThreadPool

from app import celery

from config import *

test_data_dir = 'test_data'
test_encounters_file_name = os.path.join(test_data_dir, 'encounters_{}kb.json')

results_dir = 'results'

encounter_ids_file_name = 'encounter_ids.json'
encounters_file_name = 'encounters.json'
save_file_name = os.path.join(results_dir, 'time_save_encounter_{}_{}_{}_{}_{}.txt')
query_file_name = os.path.join(results_dir, 'time_query_encounter_{}_{}_{}_{}_{}.txt')
# DIMENSIONS
# num_threads, num_users, file_size, policy_size, num_attributes

if not os.path.exists(results_dir):
    os.mkdir(results_dir)

@celery.task()
def save_encounter_test(num_threads, num_users, file_size, policy_size, num_attributes):
    with open(test_encounters_file_name.format(file_size), 'r') as encounters_file:
        encounters = json.load(encounters_file)
        
    pool = ThreadPool(num_users)

    transaction_times = []
    encounter_ids = []

    # encounters = encounters[:20]
    def save(encounter):
        start = time.time()
        response = requests.post('{}/encounters/'.format(il_upstream_url), json=encounter, headers=headers, auth=auth)
        end = time.time()
        print(response.status_code)
        transaction_time = end - start
        transaction_times.append(transaction_time)
        encounter_ids.append(response.json()['encounter_id'])

    pool = ThreadPool(num_users)

    test_start_date = datetime.datetime.utcnow()
    for encounter in encounters:
        pool.apply_async(save, (encounter,))

    pool.close()
    pool.join()
    test_end_date = datetime.datetime.utcnow()

    with open(encounter_ids_file_name, 'w') as encounter_ids_file:
        print(len(encounter_ids))
        json.dump(encounter_ids, encounter_ids_file)

    with open(save_file_name.format(num_threads, num_users, file_size, policy_size, num_attributes), 'w') as transaction_times_file:
        total_time = sum(transaction_times)
        num_transactions = len(transaction_times)
        avg_txn_time = total_time/float(num_transactions)
        rate = 1/avg_txn_time
        transaction_times_file.write('Test start: {}\n'.format(test_start_date))
        transaction_times_file.write('Test end: {}\n'.format(test_end_date))
        transaction_times_file.write('Total number of transactions: {}\n'.format(num_transactions))
        transaction_times_file.write('Total time: {}\n'.format(total_time))
        transaction_times_file.write('Average transaction time: {}\n'.format(avg_txn_time))
        transaction_times_file.write('Transactions per second: {}\n'.format(rate))
        transaction_times_file.write('\n')
        transaction_times_file.writelines(["{}\n".format(txn_time) for txn_time in transaction_times])

@celery.task()
def query_encounter_test(num_threads, num_users, file_size, policy_size, num_attributes):
    with open(encounter_ids_file_name, 'r') as encounter_ids_file:
        encounter_ids = json.load(encounter_ids_file)
    os.remove(encounter_ids_file_name)
    
    transaction_times = []
    encounters = []

    def query(encounter_id):
        start = time.time()
        response = requests.get('{}/encounters/{}'.format(il_upstream_url, encounter_id), headers=headers, auth=auth)
        end = time.time()
        print(response.status_code)
        transaction_time = end - start
        transaction_times.append(transaction_time)
        encounters.append(response.json())

    pool = ThreadPool(num_users)
    test_start_date = datetime.datetime.utcnow()
    for encounter_id in encounter_ids:
        pool.apply_async(query, (encounter_id,))

    pool.close()
    pool.join()
    test_end_date = datetime.datetime.utcnow()

    with open(encounters_file_name, 'w') as encounters_file:
        print(len(encounters))
        json.dump(encounters, encounters_file)

    with open(query_file_name.format(num_threads, num_users, file_size, policy_size, num_attributes), 'w') as transaction_times_file:
        total_time = sum(transaction_times)
        num_transactions = len(transaction_times)
        avg_txn_time = total_time/float(num_transactions)
        rate = 1/avg_txn_time
        transaction_times_file.write('Test start: {}\n'.format(test_start_date))
        transaction_times_file.write('Test end: {}\n'.format(test_end_date))
        transaction_times_file.write('Total number of transactions: {}\n'.format(num_transactions))
        transaction_times_file.write('Total time: {}\n'.format(total_time))
        transaction_times_file.write('Average transaction time: {}\n'.format(avg_txn_time))
        transaction_times_file.write('Transactions per second: {}\n'.format(rate))
        transaction_times_file.write('\n')
        transaction_times_file.writelines(["{}\n".format(txn_time) for txn_time in transaction_times])
    os.remove(encounters_file_name)

if __name__ == '__main__':
    print('Saving Encounters...')
    save_encounter_test(1,1,8,1,1)
    print('Querying Encounters...')
    query_encounter_test(1,1,8,1,1)
    print('Done.')