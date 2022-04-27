# Dissertation TODO List 📝

This page serves an annotation of the todo list for the dissertation and possibly some meaningfull information on how it is intended to be carried out.

---

- Implement **Latent Dirichlet Allocation** 🟡

    The implementation will attempt to extract from corpora topics in order to evaluate how closely related to the topics the discourse of the sucject is.
    The extraction of a LDA model from corpus has already been acomplished but this model is not yet used for feature extraction. 

    - [Gensim Package](https://pypi.org/project/gensim/) and [Gensim LDA](https://radimrehurek.com/gensim/models/ldamulticore.html)

<br/>

- Implement **GLoVE Embeddings** 🔴

    The implementation will attempt to extract from corpora word embeddings for each word.

    - [GLoVE Python Package](https://pypi.org/project/glove_python/#description)

<br/>

- Implement **Latent Content Analysis** 🟡

    Following the methodology of Rezaii et al. the model will atempt to evaluate how different the semantics of each groups is. For this purpose it is requried to exist an already defined sepparation of the dataset inton train and test.