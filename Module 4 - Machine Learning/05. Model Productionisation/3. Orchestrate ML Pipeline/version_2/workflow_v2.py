from typing import Any, Dict, List
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from prefect import task, Flow


######################################################################
# pip install prefect
# pip install "prefect[viz]"
#
# 1. Decorate each helper function with @task
# 2. Define the complete Flow
# 3. Run the flow. Note that you can also schedule it for later.
# 4. For Viz add 'flow.visualize()'
######################################################################


@task
def load_data(path: str) -> pd.DataFrame:
    data = pd.read_csv(path)
    return data

@task
def remove_unwanted_cols(data: pd.DataFrame, unwanted_cols: List) -> pd.DataFrame:
    data.drop(unwanted_cols, axis=1, inplace=True)
    return data

@task
def get_classes(data: pd.DataFrame, target_col: str) -> List[str]:
    return list(data[target_col].unique())

@task
def rescale_numerical_columns(data: pd.DataFrame, target_col: str) -> pd.DataFrame:
    
    X = data.drop([target_col], axis=1)
    # scaling the numerical features
    scaler = StandardScaler()

    # column names are (annoyingly) lost after Scaling
    # (i.e. the dataframe is converted to a numpy ndarray)
    data_rescaled = pd.DataFrame(scaler.fit_transform(X), 
                                        columns = X.columns, 
                                        index = X.index)

    return data_rescaled

@task
def split_data(input: pd.DataFrame, output: pd.Series, test_data_ratio: float) -> Dict[str, Any]:
   
    X_tr, X_te, y_tr, y_te = train_test_split(input, output, test_size=test_data_ratio, random_state=0)
    
    return {'X_TRAIN': X_tr, 'Y_TRAIN': y_tr, 'X_TEST': X_te, 'Y_TEST': y_te}

# Defining the complete Flow
with Flow('data-engineer') as flow:
    # Define Parameters
    target_col = 'Species'
    unwanted_cols = ['Id']
    test_data_ratio = 0.2

    # Run Functions
    data = load_data(path='data/iris.csv')

    # Workflow
    remove_unwanted_cols(data=data, unwanted_cols=unwanted_cols)
    numerical_data = rescale_numerical_columns(data=data, target_col=target_col)
    classes = get_classes(data=data, target_col=target_col)
    train_test_dict = split_data(input=numerical_data, output=data[target_col], test_data_ratio=test_data_ratio)
    
flow.run()
