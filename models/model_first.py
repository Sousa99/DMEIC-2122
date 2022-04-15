import pandas as pd

# Local Modules - Abstraction
import modules_abstraction.module_parser    as module_parser
import modules_abstraction.module_models    as module_models
# Local Modules - Features
import modules_features.module_sound_features   as module_sound_features
import modules_features.module_speech_features  as module_speech_features
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
    sound_features_df = module_sound_features.sound_analysis(model.subjects_paths, model.PREFERENCE_AUDIO_TRACKS)
    speech_features_df = module_speech_features.speech_analysis(model.subjects_paths, model.PREFERENCE_AUDIO_TRACKS, model.PREFERENCE_TRANS, model.EXTENSION_TRANS)
    # All Features Dataframe
    all_features_df = module_aux.join_dataframes(sound_features_df, speech_features_df)
    
    # Specify specific drop features
    sound_drop_columns = ['Audio Path', 'Audio File', 'Audio File Path']
    speech_drop_columns = ['Audio Path', 'Audio File', 'Audio File Path', 'Trans Path', 'Trans File', 'Trans File Path', 'Trans Info']
    all_features_drop_columns = ['Audio Path', 'Audio File', 'Audio File Path', 'Trans Path', 'Trans File', 'Trans File Path', 'Trans Info']

    # Create feature set
    sound_features = [column for column in sound_features_df.columns.values if column not in sound_drop_columns + model.GENERAL_DROP_COLUMNS]
    speech_features = [column for column in speech_features_df.columns.values if column not in speech_drop_columns + model.GENERAL_DROP_COLUMNS]
    all_features = [column for column in all_features_df.columns.values if column not in all_features_drop_columns + model.GENERAL_DROP_COLUMNS]

    sound_features_info = { 'features': sound_features_df, 'drop_columns': sound_drop_columns, 'feature_columns': sound_features }
    speech_features_info = { 'features': speech_features_df, 'drop_columns': speech_drop_columns, 'feature_columns': speech_features }
    all_features_info = { 'features': all_features_df, 'drop_columns': all_features_drop_columns, 'feature_columns': all_features }

    features_infos = { 'Sound': sound_features_info, 'Speech': speech_features_info, 'Sound + Speech': all_features_info }

# ============================================ MAIN EXECUTION ============================================

model.execute(features_infos)
