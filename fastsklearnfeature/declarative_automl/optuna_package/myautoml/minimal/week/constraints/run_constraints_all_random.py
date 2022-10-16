from fastsklearnfeature.declarative_automl.optuna_package.myautoml.my_system.ensemble.AutoEnsembleSuccessive import MyAutoML
import optuna
import time
from sklearn.metrics import make_scorer
import numpy as np
from fastsklearnfeature.declarative_automl.optuna_package.myautoml.my_system.Space_GenerationTreeBalance import SpaceGenerator
import copy
from anytree import RenderTree
from sklearn.ensemble import RandomForestRegressor
from optuna.samplers import RandomSampler
import pickle
import fastsklearnfeature.declarative_automl.optuna_package.myautoml.mp_global_vars as mp_glob
from fastsklearnfeature.declarative_automl.optuna_package.myautoml.feature_transformation.FeatureTransformations import FeatureTransformations
from fastsklearnfeature.declarative_automl.optuna_package.myautoml.utils_model_mine import get_data
from fastsklearnfeature.declarative_automl.optuna_package.myautoml.utils_model_mine import data2features
from fastsklearnfeature.declarative_automl.optuna_package.myautoml.utils_model_mine import space2features
from fastsklearnfeature.declarative_automl.optuna_package.myautoml.utils_model_mine import get_feature_names
from fastsklearnfeature.declarative_automl.optuna_package.myautoml.utils_model_mine import ifNull
from fastsklearnfeature.declarative_automl.optuna_package.myautoml.utils_model_mine import generate_parameters_minimal_sample_constraints_all
from optuna.samplers import TPESampler
import multiprocessing as mp
from multiprocessing import Lock
import openml
from sklearn.metrics import balanced_accuracy_score
import multiprocessing
import sklearn
from fastsklearnfeature.declarative_automl.fair_data.test import get_X_y_id
import traceback

class NoDaemonProcess(multiprocessing.Process):
    @property
    def daemon(self):
        return False

    @daemon.setter
    def daemon(self, value):
        pass


class NoDaemonContext(type(multiprocessing.get_context())):
    Process = NoDaemonProcess

# We sub-class multiprocessing.pool.Pool instead of multiprocessing.Pool
# because the latter is only a wrapper function, not a proper class.
class NestablePool(multiprocessing.pool.Pool):
    def __init__(self, *args, **kwargs):
        kwargs['context'] = NoDaemonContext()
        super(NestablePool, self).__init__(*args, **kwargs)

openml.config.apikey = '4384bd56dad8c3d2c0f6630c52ef5567'
openml.config.cache_directory = '/home/neutatz/phd2/cache_openml'

def predict_range(model, X):
    y_pred = model.predict(X)
    return y_pred

my_openml_tasks = [75126, 75125, 75121, 75120, 75116, 75115, 75114, 189859, 189878, 189786, 167204, 190156, 75156, 166996, 190157, 190158, 168791, 146597, 167203, 167085, 190154, 75098, 190159, 75169, 126030, 146594, 211723, 189864, 189863, 189858, 75236, 190155, 211720, 167202, 75108, 146679, 146592, 166866, 167205, 2356, 75225, 146576, 166970, 258, 75154, 146574, 275, 273, 75221, 75180, 166944, 166951, 189828, 3049, 75139, 167100, 75232, 126031, 189899, 75146, 288, 146600, 166953, 232, 75133, 75092, 75129, 211722, 75100, 2120, 189844, 271, 75217, 146601, 75212, 75153, 75109, 189870, 75179, 146596, 75215, 189840, 3044, 168785, 189779, 75136, 75199, 75235, 189841, 189845, 189869, 254, 166875, 75093, 75159, 146583, 75233, 75089, 167086, 167087, 166905, 167088, 167089, 167097, 167106, 189875, 167090, 211724, 75234, 75187, 2125, 75184, 166897, 2123, 75174, 75196, 189829, 262, 236, 75178, 75219, 75185, 126021, 211721, 3047, 75147, 189900, 75118, 146602, 166906, 189836, 189843, 75112, 75195, 167101, 167094, 75149, 340, 166950, 260, 146593, 75142, 75161, 166859, 166915, 279, 245, 167096, 253, 146578, 267, 2121, 75141, 336, 166913, 75176, 256, 75166, 2119, 75171, 75143, 75134, 166872, 166932, 146603, 126028, 3055, 75148, 75223, 3054, 167103, 75173, 166882, 3048, 3053, 2122, 75163, 167105, 75131, 126024, 75192, 75213, 146575, 166931, 166957, 166956, 75250, 146577, 146586, 166959, 75210, 241, 166958, 189902, 75237, 189846, 75157, 189893, 189890, 189887, 189884, 189883, 189882, 189881, 189880, 167099, 189894]

map_dataset = {}

map_dataset['802'] = 'sex@{female,male}'
map_dataset['42193'] = 'race_Caucasian@{0,1}'
map_dataset['1480'] = 'V2@{Female,Male}'
map_dataset['42178'] = 'gender@STRING'
map_dataset['981'] = 'Gender@{Female,Male}'
map_dataset['40536'] = 'samerace@{0,1}'
map_dataset['40945'] = 'sex@{female,male}'
map_dataset['451'] = 'Sex@{female,male}'
map_dataset['446'] = 'sex@{Female,Male}'
map_dataset['1017'] = 'sex@{0,1}'
map_dataset['957'] = 'Sex@{0,1}'
map_dataset['41430'] = 'SEX@{True,False}'
map_dataset['1240'] = 'sex@{Female,Male}'
map_dataset['1018'] = 'sex@{Female,Male}'
map_dataset['38'] = 'sex@{F,M}'
map_dataset['1003'] = 'sex@{male,female}'
map_dataset['934'] = 'race@{black,white}'

my_openml_tasks_fair = list(map_dataset.keys())



my_scorer = make_scorer(balanced_accuracy_score)


mp_glob.total_search_time = 5*60#60
topk = 20#26 # 20
continue_from_checkpoint = False

starting_time_tt = time.time()

my_lock = Lock()

mgr = mp.Manager()
dictionary = mgr.dict()


my_list_constraints = ['global_search_time_constraint',
                           'global_evaluation_time_constraint',
                           'global_memory_constraint',
                           'global_cv',
                           'global_number_cv',
                           'privacy',
                           'hold_out_fraction',
                           'sample_fraction',
                           'training_time_constraint',
                           'inference_time_constraint',
                           'pipeline_size_constraint',
                           'fairness_constraint',
                           'use_ensemble',
                           'use_incremental_data',
                           'shuffle_validation'
                       ]

feature_names, feature_names_new = get_feature_names(my_list_constraints)

print(len(feature_names_new))

random_runs = (163)


def run_AutoML(trial):
    repetitions_count = 10

    space = trial.user_attrs['space']

    print(trial.params)

    #make this a hyperparameter
    search_time = trial.params['global_search_time_constraint']# * 60

    evaluation_time = int(0.1 * search_time)
    if 'global_evaluation_time_constraint' in trial.params:
        evaluation_time = trial.params['global_evaluation_time_constraint']

    memory_limit = 10
    if 'global_memory_constraint' in trial.params:
        memory_limit = trial.params['global_memory_constraint']

    privacy_limit = None
    if 'privacy_constraint' in trial.params:
        privacy_limit = trial.params['privacy_constraint']

    training_time_limit = search_time
    if 'training_time_constraint' in trial.params:
        training_time_limit = trial.params['training_time_constraint']

    inference_time_limit = 60
    if 'inference_time_constraint' in trial.params:
        inference_time_limit = trial.params['inference_time_constraint']

    pipeline_size_limit = 350000000
    if 'pipeline_size_constraint' in trial.params:
        pipeline_size_limit = trial.params['pipeline_size_constraint']

    fairness_limit = 0.0
    if 'fairness_constraint' in trial.params:
        fairness_limit = trial.params['fairness_constraint']

    cv = 1
    number_of_cvs = 1
    hold_out_fraction = None
    if 'global_cv' in trial.params:
        cv = trial.params['global_cv']
        if 'global_number_cv' in trial.params:
            number_of_cvs = trial.params['global_number_cv']
    else:
        hold_out_fraction = trial.params['hold_out_fraction']

    sample_fraction = 1.0
    if 'sample_fraction' in trial.params:
        sample_fraction = trial.params['sample_fraction']

    ensemble_size = 50
    if not trial.params['use_ensemble']:
        ensemble_size = 1

    use_incremental_data = trial.params['use_incremental_data']

    shuffle_validation = False
    if not trial.params['use_ensemble']:
        shuffle_validation = trial.params['shuffle_validation']

    for pre, _, node in RenderTree(space.parameter_tree):
        if node.status == True:
            print("%s%s" % (pre, node.name))

    my_random_seed = int(time.time())
    if 'data_random_seed' in trial.user_attrs:
        my_random_seed = trial.user_attrs['data_random_seed']

    sensitive_attribute_id = None
    try:
        if fairness_limit > 0.0:
            task_id = trial.params['dataset_id_fair']
            X, y, sensitive_attribute_id, categorical_indicator = get_X_y_id(key=task_id)
            X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(X,
                                                                                        y,
                                                                                        random_state=my_random_seed,
                                                                                        stratify=y,
                                                                                        train_size=0.66)

        else:
            task_id = trial.params['dataset_id']
            X_train, X_test, y_train, y_test, categorical_indicator, attribute_names = get_data('data', randomstate=my_random_seed, task_id=task_id)
    except:
        return {'objective': 0.0}

    dynamic_params = []
    for random_i in range(repetitions_count):
        if fairness_limit > 0.0:
            search = MyAutoML(cv=cv,
                              number_of_cvs=number_of_cvs,
                              n_jobs=1,
                              evaluation_budget=evaluation_time,
                              time_search_budget=search_time,
                              space=space,
                              main_memory_budget_gb=memory_limit,
                              differential_privacy_epsilon=privacy_limit,
                              hold_out_fraction=hold_out_fraction,
                              sample_fraction=sample_fraction,
                              training_time_limit=training_time_limit,
                              inference_time_limit=inference_time_limit,
                              pipeline_size_limit=pipeline_size_limit,
                              fairness_limit=fairness_limit,
                              fairness_group_id=sensitive_attribute_id,
                              max_ensemble_models=ensemble_size,
                              use_incremental_data=use_incremental_data,
                              shuffle_validation=shuffle_validation)
        else:
            search = MyAutoML(cv=cv,
                              number_of_cvs=number_of_cvs,
                              n_jobs=1,
                              evaluation_budget=evaluation_time,
                              time_search_budget=search_time,
                              space=space,
                              main_memory_budget_gb=memory_limit,
                              differential_privacy_epsilon=privacy_limit,
                              hold_out_fraction=hold_out_fraction,
                              sample_fraction=sample_fraction,
                              training_time_limit=training_time_limit,
                              inference_time_limit=inference_time_limit,
                              pipeline_size_limit=pipeline_size_limit,
                              max_ensemble_models=ensemble_size,
                              use_incremental_data=use_incremental_data,
                              shuffle_validation=shuffle_validation)

        test_score = 0.0
        try:
            search.fit(X_train, y_train, categorical_indicator=categorical_indicator, scorer=my_scorer)

            search.ensemble(X_train, y_train)
            y_hat_test = search.ensemble_predict(X_test)
            test_score = balanced_accuracy_score(y_test, y_hat_test)
        except:
            pass
        dynamic_params.append(test_score)
    dynamic_values = np.array(dynamic_params)

    if np.sum(dynamic_values) == 0:
        return {'objective': 0.0}

    static_params = []
    for random_i in range(repetitions_count):
        # default params
        gen_new = SpaceGenerator()
        space_new = gen_new.generate_params()
        for pre, _, node in RenderTree(space_new.parameter_tree):
            if node.status == True:
                print("%s%s" % (pre, node.name))

        if fairness_limit > 0.0:
            search_static = MyAutoML(n_jobs=1,
                              time_search_budget=search_time,
                              space=space_new,
                              evaluation_budget=int(0.1 * search_time),
                              main_memory_budget_gb=memory_limit,
                              differential_privacy_epsilon=privacy_limit,
                              hold_out_fraction=0.33,
                              training_time_limit=training_time_limit,
                              inference_time_limit=inference_time_limit,
                              pipeline_size_limit=pipeline_size_limit,
                              fairness_limit=fairness_limit,
                              fairness_group_id=sensitive_attribute_id
                              )
        else:
            search_static = MyAutoML(n_jobs=1,
                                     time_search_budget=search_time,
                                     space=space_new,
                                     evaluation_budget=int(0.1 * search_time),
                                     main_memory_budget_gb=memory_limit,
                                     differential_privacy_epsilon=privacy_limit,
                                     hold_out_fraction=0.33,
                                     training_time_limit=training_time_limit,
                                     inference_time_limit=inference_time_limit,
                                     pipeline_size_limit=pipeline_size_limit
                                     )

        try:
            best_result = search_static.fit(X_train, y_train, categorical_indicator=categorical_indicator, scorer=my_scorer)

            search_static.ensemble(X_train, y_train)
            y_hat_test = search_static.ensemble_predict(X_test)
            test_score_default = balanced_accuracy_score(y_test, y_hat_test)
        except:
            test_score_default = 0.0
            traceback.print_exc()
        static_params.append(test_score_default)

    static_values = np.array(static_params)

    dynamic_values.sort()
    static_values.sort()

    frequency = np.sum(dynamic_values > static_values) / float(repetitions_count)
    return {'objective': frequency}


def run_AutoML_global(trial_id):
    comparison = run_AutoML(mp_glob.my_trials[trial_id])['objective']

    # get all best validation scores and evaluate them
    feature_list = []
    target_list = []

    feature_list.append(copy.deepcopy(mp_glob.my_trials[trial_id].user_attrs['features']))
    target_list.append(comparison)

    dataset_name = ''
    if 'dataset_id' in mp_glob.my_trials[trial_id].params:
        dataset_name = 'normal_' + str(mp_glob.my_trials[trial_id].params['dataset_id'])
    else:
        dataset_name = 'fair_' + str(mp_glob.my_trials[trial_id].params['dataset_id_fair'])

    return {'feature_l': feature_list,
            'target_l': target_list,
            'group_l': dataset_name,
            'trial_id_l': trial_id}


def calculate_max_std(N, min_value=0, max_value=1):
    max_elements = np.ones(int(N / 2)) * max_value
    min_elements = np.ones(int(N / 2)) * min_value
    return np.std(np.append(min_elements, max_elements))


def sample_configuration(trial):
    try:
        gen = SpaceGenerator()
        space = gen.generate_params()
        space.sample_parameters(trial) # no tuning of the space

        trial.set_user_attr('space', copy.deepcopy(space))

        search_time, evaluation_time, memory_limit, privacy_limit, training_time_limit, inference_time_limit, pipeline_size_limit, cv, number_of_cvs, hold_out_fraction, sample_fraction, task_id, fairness_limit, use_ensemble, use_incremental_data, shuffle_validation = generate_parameters_minimal_sample_constraints_all(
            trial, mp_glob.total_search_time, my_openml_tasks, my_openml_tasks_fair,
            use_training_time_constraint=True,
            use_inference_time_constraint=True,
            use_pipeline_size_constraint=True,
            use_fairness_constraint=True)

        my_random_seed = int(time.time())

        if fairness_limit > 0.0:
            X, y, sensitive_attribute_id, categorical_indicator = get_X_y_id(key=task_id)
            X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(X,
                                                                                        y,
                                                                                        random_state=my_random_seed,
                                                                                        stratify=y,
                                                                                        train_size=0.66)

        else:
            X_train, X_test, y_train, y_test, categorical_indicator, attribute_names = get_data('data', randomstate=my_random_seed, task_id=task_id)

        trial.set_user_attr('data_random_seed', my_random_seed)

        # add metafeatures of data
        my_list_constraints_values = [search_time,
                                      evaluation_time,
                                      memory_limit,
                                      cv,
                                      number_of_cvs,
                                      ifNull(privacy_limit, constant_value=1000),
                                      ifNull(hold_out_fraction),
                                      sample_fraction,
                                      training_time_limit,
                                      inference_time_limit,
                                      pipeline_size_limit,
                                      fairness_limit,
                                      int(use_ensemble),
                                      int(use_incremental_data),
                                      int(shuffle_validation)]

        metafeature_values = data2features(X_train, y_train, categorical_indicator)
        features = space2features(space, my_list_constraints_values, metafeature_values)
        features = FeatureTransformations().fit(features).transform(features, feature_names=feature_names)

        trial.set_user_attr('features', features)
    except:
        traceback.print_exc()
        return None
    return features

def random_config(trial):
    features = sample_configuration(trial)
    if type(features) == type(None):
        return -1 * np.inf
    return 0.0


X_meta = np.empty((0, len(feature_names_new)), dtype=float)
y_meta = []
group_meta = []
aquisition_function_value = []


#path2files = '/home/neutatz/phd2/decAutoML2weeks_compare2default/single_cpu_machine1_4D_start_and_class_imbalance'
path2files = '/home/neutatz/data/my_temp'


if continue_from_checkpoint:
    with open(path2files + '/felix_X_compare_scaled.p', 'rb') as handle:
        X_meta = pickle.load(handle)

    with open(path2files + '/felix_y_compare_scaled.p', 'rb') as handle:
        y_meta = pickle.load(handle)

    with open(path2files + '/felix_group_compare_scaled.p', 'rb') as handle:
        group_meta = pickle.load(handle)

    with open(path2files + '/felix_acquisition function value_scaled.p', 'rb') as handle:
        aquisition_function_value = pickle.load(handle)
else:
    #cold start - random sampling
    study_random = optuna.create_study(direction='maximize', sampler=RandomSampler(seed=42))
    study_random.optimize(random_config, n_trials=random_runs, n_jobs=1)

    mp_glob.my_trials = []
    trial_id2aqval = {}
    counter_trial_id = 0
    for u_trial in study_random.trials:
        if u_trial.value == 0.0: #prune failed configurations
            mp_glob.my_trials.append(u_trial)
            trial_id2aqval[counter_trial_id] = 0.0
            counter_trial_id += 1

    with NestablePool(processes=topk) as pool:
        results = pool.map(run_AutoML_global, range(len(mp_glob.my_trials)))

    for result_p in results:
        for f_progress in range(len(result_p['feature_l'])):
            X_meta = np.vstack((X_meta, result_p['feature_l'][f_progress]))
            y_meta.append(result_p['target_l'][f_progress])
            group_meta.append(result_p['group_l'])
            aquisition_function_value.append(trial_id2aqval[result_p['trial_id_l']])

    print('done')


class Objective(object):
    def __call__(self, trial):
        features = sample_configuration(trial)
        if type(features) == type(None):
            return -1 * np.inf

        return 1

def get_best_trial():
    while True:
        sampler = RandomSampler()
        study_uncertainty = optuna.create_study(direction='maximize', sampler=sampler)
        my_objective = Objective()
        study_uncertainty.optimize(my_objective, n_trials=1, n_jobs=1)
        if study_uncertainty.best_value > 0.0:
            break
    return study_uncertainty.best_trial

def sample_and_evaluate(my_id1):
    if time.time() - starting_time_tt > 60*60*24*14:
        return -1

    X_meta = copy.deepcopy(dictionary['X_meta'])
    y_meta = copy.deepcopy(dictionary['y_meta'])

    # how many are there
    my_len = min(len(X_meta), len(y_meta))
    X_meta = X_meta[0:my_len, :]
    y_meta = y_meta[0:my_len]

    #assert len(X_meta) == len(y_meta), 'len(X) != len(y)'

    try:
        best_trial = get_best_trial()
        features_of_sampled_point = best_trial.user_attrs['features']

        result = run_AutoML(best_trial)
        actual_y = result['objective']
    except Exception as e:
        print('catched: ' + str(e))
        return 0

    my_lock.acquire()
    try:
        X_meta = dictionary['X_meta']
        dictionary['X_meta'] = np.vstack((X_meta, features_of_sampled_point))

        y_meta = dictionary['y_meta']
        y_meta.append(actual_y)
        dictionary['y_meta'] = y_meta

        #assert len(X_meta) == len(y_meta), 'len(X) != len(y)'

        group_meta = dictionary['group_meta']

        dataset_name = ''
        if 'dataset_id' in best_trial.params:
            dataset_name = 'normal_' + str(best_trial.params['dataset_id'])
        else:
            dataset_name = 'fair_' + str(best_trial.params['dataset_id_fair'])

        group_meta.append(dataset_name)
        dictionary['group_meta'] = group_meta

        #assert len(X_meta) == len(group_meta), 'len(X) != len(group)'

        aquisition_function_value = dictionary['aquisition_function_value']
        aquisition_function_value.append(best_trial.value)
        dictionary['aquisition_function_value'] = aquisition_function_value

        #assert len(X_meta) == len(aquisition_function_value), 'len(X) != len(acquisition)'
    except Exception as e:
        print('catched: ' + str(e))
    finally:
        my_lock.release()

    return 0

assert len(X_meta) == len(y_meta)

dictionary['X_meta'] = X_meta
dictionary['y_meta'] = y_meta
dictionary['group_meta'] = group_meta
dictionary['aquisition_function_value'] = aquisition_function_value

with NestablePool(processes=topk) as pool:
    results = pool.map(sample_and_evaluate, range(100000))

print('storing stuff')

with open('/home/neutatz/data/my_temp/felix_X_compare_scaled.p', "wb") as pickle_model_file:
    pickle.dump(dictionary['X_meta'], pickle_model_file)

with open('/home/neutatz/data/my_temp/felix_y_compare_scaled.p', "wb") as pickle_model_file:
    pickle.dump(dictionary['y_meta'], pickle_model_file)

with open('/home/neutatz/data/my_temp/felix_group_compare_scaled.p', "wb") as pickle_model_file:
    pickle.dump(dictionary['group_meta'], pickle_model_file)

with open('/home/neutatz/data/my_temp/felix_acquisition function value_scaled.p', "wb") as pickle_model_file:
    pickle.dump(dictionary['aquisition_function_value'], pickle_model_file)
