import pandas as pd

# Local Modules
import module_models
import module_exporter
import module_sound_features
import module_speech_features

# =================================== FLAGS PARSING ===================================

args = module_models.get_arguments()

# =================================== MAIN EXECUTION ===================================

# Concat Information
subject_info = module_models.get_subjects_info()
subject_paths = module_models.get_subjects_paths()


preference_audio_tracks = module_models.get_preference_audio_tracks()
preference_transcriptions = module_models.get_preference_transcriptions()
transcriptions_extension = module_models.get_transcription_extension()
# Get Features
sound_features_df = module_sound_features.sound_analysis(subject_paths, preference_audio_tracks)
speech_features_df = module_speech_features.speech_analysis(subject_paths, preference_audio_tracks, preference_transcriptions, transcriptions_extension)
# All Features
all_features_df = pd.merge(sound_features_df, speech_features_df, left_index=True, right_index=True, how='outer', suffixes=('', '_duplicate'))
all_features_df = all_features_df.drop(all_features_df.filter(regex='_duplicate$').columns.tolist(), axis=1)

# ===================================== DROP FEATURES =====================================
sound_drop_columns = ['Audio Path', 'Audio File', 'Audio File Path']
speech_drop_columns = ['Audio Path', 'Audio File', 'Audio File Path', 'Trans Path', 'Trans File', 'Trans File Path', 'Trans Info']
all_features_drop_columns = ['Audio Path', 'Audio File', 'Audio File Path', 'Trans Path', 'Trans File', 'Trans File Path', 'Trans Info']

# ============================================ FEATURE SETS ============================================
general_drop_columns = module_models.get_general_drop_columns()
sound_features = [column for column in sound_features_df.columns.values if column not in sound_drop_columns + general_drop_columns]
speech_features = [column for column in speech_features_df.columns.values if column not in speech_drop_columns + general_drop_columns]
all_features = [column for column in all_features_df.columns.values if column not in all_features_drop_columns + general_drop_columns]

sound_features_info = { 'features': sound_features_df, 'drop_columns': sound_drop_columns, 'feature_columns': sound_features }
speech_features_info = { 'features': speech_features_df, 'drop_columns': speech_drop_columns, 'feature_columns': speech_features }
all_features_info = { 'features': all_features_df, 'drop_columns': all_features_drop_columns, 'feature_columns': all_features }

features_info = { 'Sound': sound_features_info, 'Speech': speech_features_info, 'Sound + Speech': all_features_info }

# ============================================ STUDY FEATURE SETS ============================================
module_models.study_feature_sets(features_info, subject_info)

# ================================================= VARIATIONS TO STUDY =================================================
variations_to_test = module_models.generate_variations(features_info)
variations_results = []

# ================================================= STUDY VARIATIONS =================================================
print()
print("🚀 Running solution variations ...")
for variation in variations_to_test: module_models.run_variation(variation, subject_info, variations_results)

module_exporter.change_current_directory()
# Summary of All Variations
variations_results_df = pd.DataFrame(variations_results)
module_exporter.export_csv(variations_results_df, 'results', False)