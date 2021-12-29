from lib.input_output import *

# def learnDictionary(X, nbAtoms, alpha, n_iter):
#     from sklearn.decomposition import MiniBatchDictionaryLearning
#
#     dico = MiniBatchDictionaryLearning(n_components=nbAtoms, alpha=alpha, n_iter=n_iter)
#     D = dico.fit(X).components_
#
#
#     return D

def learnDictionary(X, nbAtoms, alpha, n_iter, fname):
    from sklearn.decomposition import DictionaryLearning
    # , fit_algorithm = 'lars', 'cd'
    dico = DictionaryLearning(n_components=nbAtoms, alpha=alpha, max_iter= 10)

    D = dico.fit(X).components_
    save_object(D, fname)
    return D


