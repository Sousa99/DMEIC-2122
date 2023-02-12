from typing import List

# Local Modules - Abstraction
import modules_abstraction.module_parser            as module_parser
import modules_abstraction.module_models            as module_models
import modules_abstraction.module_featureset        as module_featureset
# Local Modules - Features
import modules_features.module_sound_features       as module_sound_features
import modules_features.module_speech_features      as module_speech_features
import modules_features.module_structure_features   as module_structure_features
import modules_features.module_content_features     as module_content_features
import modules_features.module_entirety_features    as module_entirety_features

# =================================== INITIALIZE MODEL ===================================

arguments = module_parser.get_arguments()
parallelization = arguments.parallelization_key
print_variations = arguments.print_variations

if parallelization is None: model = module_models.SequentialModel(arguments)
else: model = module_models.ParallelModel(arguments)

# =================================== COMPUTE FEATURES ===================================

feature_sets = []
if parallelization is None or parallelization == module_models.PARALLEL_FEATURE_EXTRACTION:

    # =========================================== Get Features for FeatureSet ===========================================

    sound_feature_set = module_sound_features.SoundFeatureSet()
    speech_feature_set = module_speech_features.SpeechFeatureSet()
    structure_feature_set = module_structure_features.StructureFeatureSet()
    content_feature_set = module_content_features.ContentFeatureSet()
    entirety_feature_set = module_entirety_features.EntiretyFeatureSet()

    all_feature_set = module_featureset.MergedFeatureSetAbstraction([
        sound_feature_set,
        speech_feature_set,
        structure_feature_set,
        content_feature_set,
        entirety_feature_set
    ])

    # Feature Sets
    feature_sets : List[module_featureset.FeatureSetAbstraction] = [all_feature_set]

    # =========================================== Init Execution of Feature Sets ===========================================

    if not print_variations:

        model.init_execution()

        sound_feature_set.init_execution(model.subjects_paths, model.PREFERENCE_AUDIO_TRACKS,
            model.PREFERENCE_TRANS, model.EXTENSION_TRANS, model.subjects_infos, model.GENERAL_DROP_COLUMNS)
        sound_feature_set.develop_static_df()
        print(" -------------------- ")

        speech_feature_set.init_execution(model.subjects_paths, model.PREFERENCE_AUDIO_TRACKS,
            model.PREFERENCE_TRANS, model.EXTENSION_TRANS, model.subjects_infos, model.GENERAL_DROP_COLUMNS)
        speech_feature_set.develop_static_df()
        print(" -------------------- ")

        structure_feature_set.init_execution(model.subjects_paths, model.PREFERENCE_AUDIO_TRACKS,
            model.PREFERENCE_TRANS, model.EXTENSION_TRANS, model.subjects_infos, model.GENERAL_DROP_COLUMNS)
        structure_feature_set.develop_static_df()
        print(" -------------------- ")

        content_feature_set.init_execution(model.subjects_paths, model.PREFERENCE_AUDIO_TRACKS,
            model.PREFERENCE_TRANS, model.EXTENSION_TRANS, model.subjects_infos, model.GENERAL_DROP_COLUMNS)
        content_feature_set.develop_static_df()
        print(" -------------------- ")

        entirety_feature_set.init_execution(model.subjects_paths, model.PREFERENCE_AUDIO_TRACKS,
            model.PREFERENCE_TRANS, model.EXTENSION_TRANS, model.subjects_infos, model.GENERAL_DROP_COLUMNS)
        entirety_feature_set.develop_static_df()
        print(" -------------------- ")

        # All Features Dataframe
        all_feature_set.init_execution(model.subjects_paths, model.PREFERENCE_AUDIO_TRACKS,
            model.PREFERENCE_TRANS, model.EXTENSION_TRANS, model.subjects_infos, model.GENERAL_DROP_COLUMNS)

        for feature_set in feature_sets: feature_set.develop_static_df()

# ============================================ MAIN EXECUTION ============================================

model.execute(feature_sets)
