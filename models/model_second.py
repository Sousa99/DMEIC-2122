import pandas as pd

# Local Modules - Abstraction
import modules_abstraction.module_parser    as module_parser
import modules_abstraction.module_models    as module_models
# Local Modules - Features
import modules_features.module_structure_features   as module_structure_features
import modules_features.module_content_features     as module_content_features
# Local Modules - Auxiliary
import modules_aux.module_aux   as module_aux

# =================================== INITIALIZE MODEL ===================================

arguments = module_parser.get_arguments()
parallelization = arguments.parallelization_key

if parallelization is None: model = module_models.SequentialModel(arguments)
else: model = module_models.ParallelModel(arguments)

# =================================== COMPUTE FEATURES ===================================

features_infos = None
if parallelization is None or parallelization == module_models.PARALLEL_FEATURE_EXTRACTION:
    
    # Get Features Dataframes
    structure_features_df = module_structure_features.structure_analysis(model.subjects_paths, model.PREFERENCE_TRANS, model.EXTENSION_TRANS)
    #content_features_df = module_content_features.content_analysis(model.subjects_paths, model.PREFERENCE_TRANS, model.EXTENSION_TRANS)
    # All Features Dataframe
    all_features_df = pd.DataFrame()
    # all_features_df = module_aux.join_dataframes(structure_features_df, content_features_df)

    # Specify specific drop features
    structure_drop_columns = ['Trans Path', 'Trans File', 'Trans File Path', 'Trans Info', 'Lemmatized Text', 'Lemmatized Filtered Text',
        'Word Graph', 'Word Graph - WCC', 'Word Graph - SCC', 'Word Graph - LWCC', 'Word Graph - LSCC',
        'LSA - Word Groups', 'LSA - Embedding per Word Groups', 'LSA - Embedding Groups',
        'Vector Unpacking - Word Groups', 'Vector Unpacking - Embedding per Word Groups', 'Vector Unpacking - Embedding Groups']
    # content_drop_columns = ['Audio Path', 'Audio File', 'Audio File Path', 'Trans Path', 'Trans File', 'Trans File Path', 'Trans Info']
    # all_features_drop_columns = ['Audio Path', 'Audio File', 'Audio File Path', 'Trans Path', 'Trans File', 'Trans File Path', 'Trans Info']

    # Create feature set
    structure_features = [column for column in structure_features_df.columns.values if column not in structure_drop_columns + model.GENERAL_DROP_COLUMNS]
    # content_features = [column for column in content_features_df.columns.values if column not in content_drop_columns + model.GENERAL_DROP_COLUMNS]
    # all_features = [column for column in all_features_df.columns.values if column not in all_features_drop_columns + model.GENERAL_DROP_COLUMNS]

    structure_features_info = { 'features': structure_features_df, 'drop_columns': structure_drop_columns, 'feature_columns': structure_features }
    # content_features_info = { 'features': content_features_df, 'drop_columns': content_drop_columns, 'feature_columns': content_features }
    # all_features_info = { 'features': all_features_df, 'drop_columns': all_features_drop_columns, 'feature_columns': all_features }

    features_infos = { 'Structure': structure_features_info }
    #features_infos = { 'Structure': structure_features_info, 'Content': content_features_info, 'Structure + Content': all_features_info }

# ============================================ TEST ZONE ============================================

# ============================================ MAIN EXECUTION ============================================

model.execute(features_infos)
