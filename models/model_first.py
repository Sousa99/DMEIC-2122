import pandas as pd

# Local Modules
import module_models
import module_sound_features
import module_speech_features


# =================================== INITIALIZE MODEL ===================================

model = module_models.SequentialModel()

# =================================== COMPUTE FEATURES ===================================

# Get Features Dataframes
sound_features_df = module_sound_features.sound_analysis(model.subjects_paths, model.PREFERENCE_AUDIO_TRACKS)
speech_features_df = module_speech_features.speech_analysis(model.subjects_paths, model.PREFERENCE_AUDIO_TRACKS, model.PREFERENCE_TRANS, model.EXTENSION_TRANS)
# All Features Dataframe
all_features_df = pd.merge(sound_features_df, speech_features_df, left_index=True, right_index=True, how='outer', suffixes=('', '_duplicate'))
all_features_df = all_features_df.drop(all_features_df.filter(regex='_duplicate$').columns.tolist(), axis=1)

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

model.load_features_infos(features_infos)
model.study_feature_sets()
model.run_variations()