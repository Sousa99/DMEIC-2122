import pandas as pd

# Local Modules
import module_parser
import module_models
import module_structure_features
import module_content_features

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
    # all_features_df = pd.merge(structure_features_df, content_features_df, left_index=True, right_index=True, how='outer', suffixes=('', '_duplicate'))
    # all_features_df = all_features_df.drop(all_features_df.filter(regex='_duplicate$').columns.tolist(), axis=1)

    # Specify specific drop features
    structure_drop_columns = ['Trans Path', 'Trans File', 'Trans File Path', 'Trans Info', 'Word Graph', 'Word Graph - WCC', 'Word Graph - SCC']
    # content_drop_columns = ['Audio Path', 'Audio File', 'Audio File Path', 'Trans Path', 'Trans File', 'Trans File Path', 'Trans Info']
    # all_features_drop_columns = ['Audio Path', 'Audio File', 'Audio File Path', 'Trans Path', 'Trans File', 'Trans File Path', 'Trans Info']

    # Create feature set
    structure_features = [column for column in structure_features_df.columns.values if column not in structure_drop_columns + model.GENERAL_DROP_COLUMNS]
    # content_features = [column for column in content_features_df.columns.values if column not in content_drop_columns + model.GENERAL_DROP_COLUMNS]
    # all_features = [column for column in all_features_df.columns.values if column not in all_features_drop_columns + model.GENERAL_DROP_COLUMNS]

    structure_features_info = { 'features': structure_features_df, 'drop_columns': structure_drop_columns, 'feature_columns': structure_features }
    # content_features_info = { 'features': content_features_df, 'drop_columns': content_drop_columns, 'feature_columns': content_features }
    # all_features_info = { 'features': all_features_df, 'drop_columns': all_features_drop_columns, 'feature_columns': all_features }

    #features_infos = { 'Structure': structure_features_info, 'Content': content_features_info, 'Structure + Content': all_features_info }

# ============================================ TEST ZONE ============================================

print(structure_features_df[structure_features])

# ============================================ MAIN EXECUTION ============================================

#model.execute(features_infos)