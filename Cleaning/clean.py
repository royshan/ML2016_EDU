import pandas as pd 
import numpy as np 
from sklearn.feature_extraction import DictVectorizer



def get_nulls_by_column(ds, filter='only_null'):
    #Return columns and its null count
    if type(ds) != pd.DataFrame:
        raise TypeError('ds must be pd.DataFrame')

    for col in ds.columns:
        null_sum = ds[col].isnull().sum()
        if null_sum or filter != 'only_null':
            print col, ds[col].isnull().sum()


def valid_error_step_duration(ds):
    #Return the index of elements
    #which contain a valid NaN the step was solved
    #correctly by the student.
    if type(ds) != pd.DataFrame:
        raise TypeError('ds must be pd.DataFrame')

    columns = ['error_step_duration','correct_first_attempt']
    ds_sub = ds[columns]

    ESD_null = ds_sub[ds_sub['error_step_duration'].isnull()]
    ESD_missing_null = ESD_null[ESD_null['correct_first_attempt']==1]

    return ESD_missing_null.index

def set_value_for_index_column(ds, index, column, value):
    #Set the same value for all the items in ds.loc[(column,index)] inplace

    if type(ds) != pd.DataFrame:
        raise TypeError('ds must be pd.DataFrame')
    ds[column].ix[index] = value
    

def fill_KC_null(ds, column):
    #Fill null values in KC column by the string 'null_unit'
    #taking unit value from ds['Problem Hierarchy']
    ds_na_KC = ds[ds[column].isnull()]

    units = ds_na_KC['unit']
    units_str = units.astype(str)

    fill_KC = pd.Series(['null_'+s for s in units_str.values],index=units_str.index)

    ds.loc[(ds_na_KC.index,column)] = fill_KC

    return ds


def fill_KC_op_null(ds, skill_column, opportunity_column):
    #skill_column: str
    #opportunity column: str
    KCOP_null = ds[ds[opportunity_column].isnull()]

    group = [skill_column, 'student_id']
    KCOP_null.loc[(KCOP_null.index,opportunity_column)] = KCOP_null.groupby(group).cumcount()+1

    KCOP_null[opportunity_column] = KCOP_null[opportunity_column].astype(str)

    ds.loc[(KCOP_null.index,opportunity_column)] = KCOP_null[opportunity_column]
    return ds
    



def unit_to_int(ds,test = False):
    #Replace unit strings to integers in a one-to-one mapping

    units_str = ds['unit'].unique()
    units_int = range(len(units_str))
    mapping_dict = dict(zip(units_str,units_int))

    if test:       
       return ds.replace({'unit':mapping_dict}) , test.replace({'unit':mapping_dict}) 

    return ds.replace({'unit':mapping_dict})  


def split_problem_hierarchy(ds):
    if type(ds) != pd.DataFrame:
        raise TypeError('ds must be pd.DataFrame')

    hierarchy = ds['Problem Hierarchy']
    ds.drop('Problem Hierarchy',1,inplace=True)

    hierarchy = hierarchy.apply(lambda x: str.split(x,',') )
    unit = pd.Series([u[0] for u in hierarchy.values],index=hierarchy.index)
    section = pd.Series([s[1] for s in hierarchy.values],index=hierarchy.index)

    ds['unit'] = unit
    ds['section'] = section

    return ds

def create_unique_step_id(ds):
    grouped = train.groupby(['unit','section','problem_name', 'step_name'])
    groups = grouped.groups
    unique_step_id = range(len(groups))
    #groups is a dictionary

def create_unique_problem_id(ds):
    ds['problem_id']= ds['problem_name'] + ds['step_name'] 

def create_unique_step_id(ds):
    ds['step_id']= ds['problem_id'] + ds['step_name']







def renamer(data_frame):
    data_renamed = data_frame.rename(columns={'Row': 'row', 'Anon Student Id': 'student_id',
                                            'Problem Name': 'problem_name','Problem View': 'view', 'Step Name': 'step_name',
                                            'Step Start Time': 'start_time', 'First Transaction Time': 'first_trans_time',
                                            'Correct Transaction Time': 'correct_trans_time', 'Step End Time': 'end_time',
                                            'Step Duration (sec)': 'step_duration', 'Correct Step Duration (sec)':'correct_step_duration',
                                            'Error Step Duration (sec)':'error_step_duration','Correct First Attempt':'correct_first_attempt',
                                            'Incorrects':'incorrects', 'Hints':'hints', 'Corrects':'corrects',
                                            'KC(SubSkills)':'kc_subskills', 'Opportunity(SubSkills)':'opp_subskills',
                                            'KC(KTracedSkills)':'k_traced_skills', 'Opportunity(KTracedSkills)':'opp_k_traced', 
                                            'KC(Rules)': 'kc_rules', 'Opportunity(Rules)': 'opp_rules'})
    return data_renamed




def sparse_kc_skills(ds, skill_column, opportunity_column):

    #Create temporal columns
    ds.loc[:,'KCop'] = np.array(ds[opportunity_column].str.split('~~'))
    ds.loc[:,'KCop'] = map(list_string_to_int, ds['KCop'])
    ds.loc[:,'KC'] = ds[skill_column].str.split('~~')
    ds.loc[:,'KCzip'] = map(zip,ds.KC,ds.KCop)
    ds.loc[:,'KCdict'] = ds.KCzip.map(dict)

    #Create sparse matrix
    #sparse_ds = pd.DataFrame(list(ds['KCdict']), index = ds.index)
    list_dicts = list(ds['KCdict'])
    v = DictVectorizer(sparse=True)
    sparse_ds = v.fit_transform(list_dicts)
    #Remove temporal columns
    ds.drop('KCop',1, inplace = True)
    ds.drop('KC',1, inplace=True)
    ds.drop('KCzip',1, inplace=True)
    ds.drop('KCdict',1, inplace=True)

    return sparse_ds, v


def list_string_to_int(string_list):
    '''Convert a list of strings to a list of integers'''
    return map(int, string_list)

def create_target_to_one_negative_one(ds):
    ds['y_one_negative_one'] = ds.correct_first_attempt
    mapping_dict = {0:-1}
    return ds.replace({'y_one_negative_one':mapping_dict})

def main():
    
    train = pd.read_csv('./Datasets/algebra_2008_2009/algebra_2008_2009_train.txt', sep='\t')
    test = pd.read_csv('./Datasets/algebra_2008_2009/algebra_2008_2009_test.txt', sep='\t')

    #Dataset contains a column called Error Step Duration which can be NaN
    #if there is a missing value or if the step was solved correctly (valid NaN). 
    #Set the value of valid NaNs to -1
    train = renamer(train)
    set_value_for_index_column(train, valid_error_step_duration(train), 'error_step_duration',-1)    
    train = split_problem_hierarchy(train)
    train = unit_to_int(train)

    train = fill_KC_null(train, 'kc_subskills')
    train = fill_KC_null(train, 'k_traced_skills')
    train = fill_KC_null(train, 'kc_rules')

    train = fill_KC_op_null(train, 'kc_subskills', 'opp_subskills')
    train = fill_KC_op_null(train, 'k_traced_skills', 'opp_k_traced')
    train = fill_KC_op_null(train, 'kc_rules', 'opp_rules')

    create_unique_problem_id(train)
    create_unique_step_id(train)

    train = create_target_to_one_negative_one(train)



    #train.to_csv('./Datasets/algebra_2008_2009/22042016_train.txt', sep='\t')
    #train1 = pd.read_csv('./Datasets/algebra_2008_2009/22042016_train.txt', sep='\t', index_col=0)
    #train = pd.read_csv('./Datasets/algebra_2008_2009/22042016_train.txt', sep='\t', index_col=0)

    subskills_sparse, subskills_vectorizer = sparse_kc_skills(train, 'kc_subskills','opp_subskills')
    k_traced_sparse, k_traced_vectorizer = sparse_kc_skills(train, 'k_traced_skills','opp_k_traced')
    kc_rules_sparse, kc_rules_vectorizer = sparse_kc_skills(train, 'kc_rules','opp_rules')

    



if __name__ == '__main__':
    main()




#subtrain[subtrain.opp_subskills.isnull()].groupby(['kc_subskills','student_id'])
#train['cuenta'] = train[train.opp_subskills.isnull()].groupby(['kc_subskills','student_id']).cumcount()+1


