# Dissertation TODO List 📝

This page serves an annotation of the todo list for the dissertation and possibly some meaningfull information on how it is intended to be carried out.

---

- Extract **Lemmatized Text from Corpora** 🟡

    Currently the effort is on parallelizing and carrying out this task in a plausible ammount of time. The idea is to use **NLPyPort** in order to lemmatize the text, and **NLTK** to remove certain stopwords.

    Then develop a **list with the documents cleaned and lemmatized**, a **pandas Dataframe** with **word co-occurrences**, and a **gensim Dictionary** built with cleaned documents.

    - [NLPyPort Paper](http://nlp.dei.uc.pt/index.php/nlpyport-a-ferramenta-de-nlp-para-python/) and [NLPyPort Code](https://github.com/NLP-CISUC/NLPyPort)
    - [Gensim Package](https://pypi.org/project/gensim/) and [Gensim Dictionary](https://radimrehurek.com/gensim/corpora/dictionary.html)

<br/>

- Implement **Latent Semantic Analysis** 🟡
    
    Currently the strategy is to use the **gensim** **Dictionary** in order to develop a **LSA Model**. The model is tested out with various number of topics, and the number that displays higher coherences scores is chosen.

    From the chosen LSA Model, word embeddings can be achieved for each word, in order for the posteriori acquisition of word embeddings.
    ``` python
    # Assuming Dictionary and Model are to be loaded
    dictionary = gensim.corpora.Dictionary.load('./exports/corpora_dictionary.bin')
    model = gensim.models.LsiModel.load('./exports/lsa_best_model.bin')

    # Word associated with a given index can be accessed with
    dictionary.get(index)
    # Word Embeddings without in numpy matrix alike-format, without word index
    model.projection.u 
    ```

    - [Gensim Package](https://pypi.org/project/gensim/), [Gensim Dictionary](https://radimrehurek.com/gensim/corpora/dictionary.html), and [Gensim LSA](https://radimrehurek.com/gensim/models/lsimodel.html)

<br/>

- Implement **Latent Dirichlet Allocation** 🔴

    The implementation will attempt to extract from corpora topics in order to evaluate how closely related to the topics the discourse of the sucject is.

    - [Gensim Package](https://pypi.org/project/gensim/) and [Gensim LDA](https://radimrehurek.com/gensim/models/ldamulticore.html)

<br/>

- Implement **Word2Vec** 🔴

    The implementation will attempt to extract from corpora word embeddings for each word.

    - [Gensim Package](https://pypi.org/project/gensim/) and [Gensim Word2Vec](https://radimrehurek.com/gensim/models/word2vec.html)

<br/>

- Implement **GLoVE Embeddings** 🔴

    The implementation will attempt to extract from corpora word embeddings for each word.

    - [GLoVE Python Package](https://pypi.org/project/glove_python/#description)