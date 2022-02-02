
# =================================== PRIVATE METHODS ===================================

# =================================== PUBLIC METHODS ===================================

def pivot_on_column(data, index, pivot_column, features, join_columns):

    data_pivot = data.pivot(index, pivot_column, features)
    data_pivot.columns =[' '.join([s1, join_columns, s2]) for (s1,s2) in data_pivot.columns.tolist()]
    data_pivot = data_pivot.reset_index()
    data_pivot = data_pivot.set_index(index)

    return data_pivot
