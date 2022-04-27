from typing import List

# Local Modules - Abstraction
import modules_abstraction.module_parser        as module_parser
import modules_abstraction.module_models        as module_models
import modules_abstraction.module_featureset    as module_featureset
# Local Modules - Features
import modules_features.module_sound_features   as module_sound_features
import modules_features.module_speech_features  as module_speech_features

# =================================== INITIALIZE MODEL ===================================

arguments = module_parser.get_arguments()
parallelization = arguments.parallelization_key

if parallelization is None: model = module_models.SequentialModel(arguments)
else: model = module_models.ParallelModel(arguments)

# =================================== COMPUTE FEATURES ===================================

feature_sets = None
if parallelization is None or parallelization == module_models.PARALLEL_FEATURE_EXTRACTION:

    # Get Features Dataframes
    sound_feature_set = module_sound_features.SoundFeatureSet(model.subjects_paths, model.PREFERENCE_AUDIO_TRACKS,
        model.PREFERENCE_TRANS, model.EXTENSION_TRANS, model.subjects_infos, model.GENERAL_DROP_COLUMNS)
    sound_feature_set.develop_static_df()
    print(" -------------------- ")

    speech_feature_set = module_speech_features.SpeechFeatureSet(model.subjects_paths, model.PREFERENCE_AUDIO_TRACKS,
        model.PREFERENCE_TRANS, model.EXTENSION_TRANS, model.subjects_infos, model.GENERAL_DROP_COLUMNS)
    speech_feature_set.develop_static_df()
    print(" -------------------- ")

    # All Features Dataframe
    all_feature_set = module_featureset.MergedFeatureSetAbstraction([sound_feature_set, speech_feature_set],
        model.subjects_paths, model.PREFERENCE_AUDIO_TRACKS,
        model.PREFERENCE_TRANS, model.EXTENSION_TRANS, model.subjects_infos, model.GENERAL_DROP_COLUMNS)

    feature_sets : List[module_featureset.FeatureSetAbstraction] = [sound_feature_set, speech_feature_set, all_feature_set]
    for feature_set in feature_sets: feature_set.develop_static_df()

# ============================================ MAIN EXECUTION ============================================

model.execute(feature_sets)
