#!/usr/bin/python3
import numpy as np


def word_indices(vec):
    """
    Turn a document vector of size vocab_size to a sequence
    of word indices. The word indices are between 0 and
    vocab_size-1. The sequence length is equal to the document length.
    """
    for idx in vec.nonzero()[0]:  # if word 5 appears 3 times, returns 5 5 5
        for i in range(int(vec[idx])):
            yield idx


def dtopic_distribution(cooccurrenceence_dtopic_word, cooccurrenceence_doc_dtopic, alpha, beta):
    phi = cooccurrenceence_dtopic_word + beta
    phi /= np.sum(phi, axis=1)[:, np.newaxis]

    theta = cooccurrenceence_doc_dtopic + alpha
    theta /= np.sum(theta, axis=1)[:, np.newaxis]

    return phi, theta

def atopic_distribution(cooccurrenceence_atopic_word, cooccurrenceence_author_atopic, alpha, beta):
    # word topic distribution
    phi = cooccurrenceence_atopic_word + beta
    phi /= np.sum(phi, axis=1)[:, np.newaxis]

    # author topic distribution
    theta = cooccurrenceence_author_atopic + alpha
    theta /= np.sum(theta, axis=1)[:, np.newaxis]

    return phi, theta

def sample_dtopic(doc, word, num_dtopics, cooccurrence_dtopic_word, occurrence_dtopic, cooccurrence_doc_dtopic, number_dwords_per_doc, alpha, beta):
    vocab_size = cooccurrence_dtopic_word.shape[1]

    word_topics = (cooccurrence_dtopic_word[:, word] + beta) / \
                  (occurrence_dtopic + beta * vocab_size)

    document_topics = (cooccurrence_doc_dtopic[doc, :] + alpha) / \
                      (number_dwords_per_doc[doc] + alpha * num_dtopics)

    distribution = document_topics * word_topics
    # normalize to obtain probabilities
    distribution /= np.sum(distribution)

    new_dtopic = np.random.multinomial(1, distribution).argmax()
    return new_dtopic

def dtopic_phi(cooccurrence_dtopic_word, beta):
    phi = (cooccurrence_dtopic_word + beta)
    phi /= np.sum(phi, axis=1)[:, np.newaxis]
    return phi

def dtopic_theta(cooccurrence_doc_dtopic, alpha):
    theta = cooccurrence_doc_dtopic + self.alpha
    theta /= np.sum(theta, axis=1)[:, np.newaxis]
    return theta

def sample_atopic_and_author(doc, word, authors, doc_authors, cooccurrence_atopic_word, occurrence_atopic, cooccurrence_author_atopic, occurrence_author, num_atopics, alpha, beta):
    vocab_size = cooccurrence_atopic_word.shape[1]

    word_topics = (cooccurrence_atopic_word[:, word] + beta) / (occurrence_atopic + beta * vocab_size)

    author_topics = (cooccurrence_author_atopic[authors, :] + alpha) / (occurrence_author[authors].repeat(num_atopics).reshape(len(authors), num_atopics) + alpha * num_atopics)

    distribution = author_topics * word_topics
    # reshape into a looong vector
    distribution = distribution.reshape(len(authors) * num_atopics)
    # normalize to obtain probabilities
    distribution /= np.sum(distribution)
    # distribution *= 0.99
    # if (np.sum(distribution) < 1.0):
    #     print(cooccurrence_atopic_word[:, word])
    #     print(distribution)
    #     print(np.sum(distribution))

    idx = np.random.multinomial(1, distribution).argmax()

    new_author = doc_authors[doc][int(idx / num_atopics)]
    new_topic = idx % num_atopics

    return (new_topic, new_author)

def atopic_phi(cooccurrence_atopic_word, beta):
    phi = (cooccurrence_atopic_word + beta)
    phi /= np.sum(phi, axis=1)[:, np.newaxis]
    return phi

def atopic_theta(cooccurrence_author_atopic, alpha):
    theta = cooccurrence_author_atopic + self.alpha
    theta /= np.sum(theta, axis=1)[:, np.newaxis]
    return theta

def learn(matrix, doc_authors, num_dtopics, num_atopics, num_authors, alpha_a, beta_a, alpha_d, beta_d, eta, delta_A, delta_D, burn_in, samples, spacing):
    num_docs, num_words = matrix.shape

    # Initialize matricies
    cooccurrence_dtopic_word = np.zeros((num_dtopics, num_words))
    cooccurrence_atopic_word = np.zeros((num_atopics, num_words))
    cooccurrence_author_atopic = np.zeros((num_authors, num_atopics))
    prior_author = np.zeros((num_authors))  # only used in classifier
    cooccurrence_document_dtopic = np.zeros((num_docs, num_dtopics))

    occurrence_atopic = np.zeros((num_atopics))
    occurrence_dtopic = np.zeros((num_dtopics))
    occurrence_author = np.zeros((num_authors))

    num_dwords_per_doc = np.zeros((num_docs))

    document_atopic_dtopic_ratio = np.zeros((num_docs))
    document_word_topic = {}  # index : (doc, word-index) value: (1 for atopic 0 for dtopic, topic)
    authors = {}

    for doc in range(num_docs):
        document_atopic_dtopic_ratio[doc] = np.random.beta(delta_A, delta_D)
        # i is a number between 0 and doc_length-1
        # w is a number between 0 and vocab_size-1
        for i, word in enumerate(word_indices(matrix[doc, :])):
            # choose an arbitrary topic as first topic for word i
            is_atopic = np.random.binomial(1, document_atopic_dtopic_ratio[doc])
            if (is_atopic):
                atopic = np.random.randint(num_atopics)
                author = doc_authors[doc][np.random.randint(len(doc_authors[doc]))]
                occurrence_atopic[atopic] += 1
                occurrence_author[author] += 1
                # print(doc,i,is_atopic,atopic) #doc 0, i 0, is_atopic 1, atopic 8
                document_word_topic[(doc, i)] = (is_atopic, atopic)
                cooccurrence_atopic_word[(atopic, word)] += 1
                cooccurrence_author_atopic[(author, atopic)] += 1
                authors[(doc, i)] = author
            else:
                dtopic = np.random.randint(num_dtopics)
                cooccurrence_dtopic_word[(dtopic, word)] += 1
                cooccurrence_document_dtopic[(doc, dtopic)] += 1
                occurrence_dtopic[dtopic] += 1
                num_dwords_per_doc[doc] += 1
                # print(doc,i,is_atopic,dtopic)
                document_word_topic[(doc, i)] = (is_atopic, dtopic)

    print(document_word_topic[(0,0)])

    taken_samples = 0

    it = 0  # iterations
    atopic_theta_sampled = 0;
    atopic_phi_sampled = 0;
    dtopic_theta_sampled = 0;
    dtopic_phi_sampled = 0;
    while taken_samples < samples:
        print('Iteration ', it)
        for doc in range(num_docs):  # all documents
            for i, word in enumerate(word_indices(matrix[doc, :])):
                old_is_atopic, old_topic = document_word_topic[(doc, i)]
                # print(it,doc,i)
                # print("old y, old topic",old_is_atopic, old_topic)

                if (old_is_atopic):
                    # print(document_word_topic[(0,0)])
                    old_author = authors[(doc, i)]
                    cooccurrence_atopic_word[(old_topic, word)] -= 1
                    cooccurrence_author_atopic[(old_author, old_topic)] -= 1
                    occurrence_atopic[old_topic] -= 1
                    occurrence_author[old_author] -= 1
                    # print(cooccurrence_atopic_word[np.where(cooccurrence_atopic_word < 0)])
                    # print(np.where(cooccurrence_atopic_word < 0))
                    # # print(cooccurrence_atopic_word)
                    # print(document_word_topic[(0,0)])
                else:
                    # print(document_word_topic[(0,0)])
                    cooccurrence_dtopic_word[(old_topic, word)] -= 1
                    cooccurrence_document_dtopic[(doc, old_topic)] -= 1
                    occurrence_dtopic[old_topic] -= 1
                    num_dwords_per_doc[doc] -= 1
                    # print(document_word_topic[(0,0)])

                is_atopic = np.random.binomial(1, document_atopic_dtopic_ratio[doc])

                if (is_atopic):
                    new_atopic, new_author = sample_atopic_and_author(doc, word, doc_authors[doc], doc_authors, cooccurrence_atopic_word, occurrence_atopic,  cooccurrence_author_atopic, occurrence_author, num_atopics, alpha_a, beta_a)

                    occurrence_atopic[new_atopic] += 1
                    occurrence_author[new_author] += 1
                    document_word_topic[(doc, i)] = (is_atopic, new_atopic)
                    cooccurrence_atopic_word[(new_atopic, word)] += 1
                    cooccurrence_author_atopic[(new_author, new_atopic)] += 1
                    authors[(doc, i)] = new_author
                else:
                    new_dtopic = sample_dtopic(doc, word, num_dtopics, cooccurrence_dtopic_word, occurrence_dtopic, cooccurrence_document_dtopic, num_dwords_per_doc, alpha_d, beta_d)

                    cooccurrence_dtopic_word[(new_dtopic, word)] += 1
                    cooccurrence_document_dtopic[(doc, new_dtopic)] += 1
                    occurrence_dtopic[new_dtopic] += 1
                    num_dwords_per_doc[doc] += 1
                    document_word_topic[(doc, i)] = (is_atopic, new_dtopic)

                # print(document_word_topic[(0,0)])

        if it >= burn_in:
            it_after_burn_in = it - burn_in
            if (it_after_burn_in % spacing) == 0:
                print('    Sampling!')
                atopic_phi_sampled += atopic_phi(cooccurrence_atopic_word, beta_a)
                atopic_theta_sampled += atopic_theta(cooccurrence_author_atopic, alpha_a)
                dtopic_phi_sampled += dtopic_phi(cooccurrenceence_dtopic_word, beta_d)
                dtopic_theta_sampled += dtopic_theta(cooccurrenceence_doc_dtopic, alpha_d)
                taken_samples += 1
        it += 1

    atopic_phi_sampled /= taken_samples
    atopic_theta_sampled /= taken_samples
    dtopic_phi_sampled /= taken_samples
    dtopic_theta_sampled /= taken_samples


def classify(matrix, burn_in, samples, spacing, alpha, beta, eta, delta_A, delta_D):
    print("error: not yet implemented")
    return [0]