
import vectors

from word2vec import embeddings
from sklearn.cluster import KMeans

lexical_clusters   = None
embedding_clusters = None
skipgram_mappings  = None

def predict_sequence_cluster(chunk):

        global lexical_clusters
        global embedding_clusters
        global skipgram_mappings

        vector = vectors.get_sequence_vectors(chunk, skipgram_mappings, embeddings)

        D = vector.shape[0]

        assert D == 200 or D == 500

        if D == 200:

            return lexical_clusters.predict(vector)[0]

        else:

            return embedding_clusters.predict(vector)[0]


def get_sequence_vector_clusters(chunked_sentences, chunk_indices):

    # TODO: perform this on chunked data...
    # TODO: vectorize this code...

    global skipgram_mappings

    chunk_embeddings = []
    chunk_lexical    = []

    print "getting vectors..."

    j = 1

    n = len(chunked_sentences)

    for l, inds in zip(chunked_sentences, chunk_indices):

        print "{} / {} getting vector".format(j, n)

        j += 1

        for i in inds:

            vector = vectors.get_sequence_vectors(l[i], skipgram_mappings, embeddings)

            D = vector.shape[0]

            print D

            assert D == 200 or D == 500

            if D == 200:
                chunk_lexical.append(vector)
            else:
                chunk_embeddings.append(vector)


    embedding_clusters = KMeans(max_iter=120, n_clusters=min(len(chunk_embeddings), 1024))
    lexical_clusters = KMeans(max_iter=120, n_clusters=min(len(chunk_lexical), 1024))

    print "clustering..."
    embedding_clusters.fit(chunk_embeddings)
    lexical_clusters.fit(chunk_lexical)

    return embedding_clusters, lexical_clusters



