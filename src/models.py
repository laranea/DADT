#!/usr/bin/python3
import numpy as np
import random
import lda
import at
import dadt
import copy
import sys, os
sys.path.append(os.path.abspath("liblinear/python"))
import liblinearutil as ll

def add_fic_authors(doc_authors, n_authors):
    n_docs = len(doc_authors)
    next_fa = n_authors

    doc_authors_new = copy.deepcopy(doc_authors)

    for doc, list in enumerate(doc_authors_new):
        doc_authors_new[doc].append(next_fa)
        next_fa += 1

    return(doc_authors_new, next_fa)

def TOKEN_SVM(matrix, test_matrix, n_authors, doc_authors):
    num_test_docs = test_matrix.shape[0]
    svm_model = ll.train(sum(doc_authors, []), matrix.tolist(), '-c 4')
    p_label, p_acc, p_val = ll.predict(np.random.rand(num_test_docs), test_matrix.tolist(), svm_model)
    return p_label

def LDA_SVM(matrix, test_matrix, n_authors, doc_authors):
    # set parameters
    number_topics = 20
    burn_in = 8  # 0
    alpha = 0.1
    beta = 0.1
    samples = 4
    spacing = 2  # 100
    chains = 2

    num_test_docs = test_matrix.shape[0]

    sampler = lda.LDA(number_topics, alpha, beta)

    print('Starting!')
    theta, phi, likelihood = sampler.train(matrix, burn_in, samples, spacing)
    print('likelihood: ', likelihood)

    theta_test, likelihood = sampler.classify(test_matrix, phi, burn_in, samples, spacing, chains)
    print('likelihood: ', likelihood)

    svm_model = ll.train(sum(doc_authors, []), matrix.tolist(), '-c 4')
    p_label, p_acc, p_val = ll.predict(np.random.rand(num_test_docs), theta_test.tolist(), svm_model)
    return p_label

def AT_SVM(matrix, test_matrix, n_authors, doc_authors):
    # set parameters
    number_topics = 4
    burn_in = 2  # 0
    alpha = 0.1
    beta = 0.1
    samples = 2
    spacing = 2  # 100
    chains = 2

    num_test_docs = test_matrix.shape[0]

    sampler = at.AtSampler(number_topics, n_authors, alpha, beta)

    print('Starting!')
    theta, phi, likelihood = sampler.train(doc_authors, matrix, burn_in, samples, spacing)
    print('theta: ', theta.shape)
    print('phi: ', phi.shape)
    print('likelihood: ', likelihood)

    sampler.n_authors = num_test_docs

    theta_test = sampler.classify(test_matrix, phi, burn_in, samples, spacing, chains)
    print('theta test: ', theta_test.shape)
    print('likelihood: ', likelihood)

    svm_model = ll.train([0,1], theta.tolist(), '-c 4')
    p_label, p_acc, p_val = ll.predict(np.random.rand(num_test_docs), theta_test.tolist(), svm_model)

    return p_label

def AT_P(matrix, test_matrix, n_authors, doc_authors):
    # set parameters
    number_topics = 4
    burn_in = 5 # 0
    alpha = 0.1
    beta = 0.1
    samples = 1 # 0
    spacing = 5  # 100
    chains = 2

    sampler = at.AtSampler(number_topics, n_authors, alpha, beta)

    print('Starting!')
    theta, phi, likelihood = sampler.train(doc_authors, matrix, burn_in, samples, spacing)
    print('theta: ', theta)
    print('phi: ', phi)
    print('likelihood: ', likelihood)

    authors = sampler.at_p(phi, theta, test_matrix)

    return(authors)

def AT_FA_SVM(matrix, test_matrix, n_authors, doc_authors):
    # set parameters
    number_topics = 4
    burn_in = 5  # 0
    alpha = 0.1
    beta = 0.1
    samples = 2
    spacing = 2  # 100
    chains = 2

    num_test_docs = test_matrix.shape[0]

    doc_authors_new, n_authors_new = add_fic_authors(doc_authors, n_authors)

    sampler = at.AtSampler(number_topics, n_authors_new, alpha, beta)

    print('Starting!')
    theta, phi, likelihood = sampler.train(doc_authors_new, matrix, burn_in, samples, spacing)
    print('theta:', theta.shape)
    print('phi:', phi.shape)
    print('likelihood:', likelihood)

    sampler.n_authors = num_test_docs

    theta_test = sampler.classify(test_matrix, phi, burn_in, samples, spacing, chains)
    print('theta test:', theta_test.shape)

    num_training_docs = matrix.shape[0]
    training_matrix = np.zeros((num_training_docs, number_topics * 2))
    for doc in range(num_training_docs):
        training_doc_authors = doc_authors_new[doc]
        vector = np.concatenate(theta[training_doc_authors])
        training_matrix[doc] = vector

    num_test_docs = test_matrix.shape[0]
    test_matrix = np.concatenate((theta_test, theta_test), axis=1)

    svm_model = ll.train(sum(doc_authors, []), matrix.tolist(), '-c 4')
    p_label, p_acc, p_val = ll.predict(np.random.rand(num_test_docs), test_matrix.tolist(), svm_model)

    return p_label

def AT_FA_P1(matrix, test_matrix, n_authors, doc_authors):
    # set parameters
    number_topics = 4
    burn_in = 2 # 0
    alpha = 0.1
    beta = 0.1
    samples = 2
    spacing = 1  # 100
    chains = 2

    doc_authors_new, n_authors_new = add_fic_authors(doc_authors, n_authors)

    sampler = at.AtSampler(number_topics, n_authors_new, alpha, beta)

    print('Starting!')
    theta, phi, likelihood = sampler.train(doc_authors_new, matrix, burn_in, samples, spacing)
    print('theta: ', theta)
    print('phi: ', phi)
    print('likelihood: ', likelihood)

    sampler.n_authors = n_authors

    authors = sampler.at_p(phi, theta, test_matrix)

    return(authors)

def AT_FA_P2(matrix, test_matrix, n_authors, doc_authors):
    # set parameters
    number_topics = 4
    burn_in = 2  # 0
    alpha = 0.1
    beta = 0.1
    samples = 2
    spacing = 2  # 100
    chains = 2

    doc_authors_new, n_authors_new = add_fic_authors(doc_authors, n_authors)

    sampler = at.AtSampler(number_topics, n_authors_new, alpha, beta)

    print('Starting!')
    theta, phi, likelihood = sampler.train(doc_authors_new, matrix, burn_in, samples, spacing)
    print('theta: ', theta)
    print('phi: ', phi)
    print('likelihood: ', likelihood)

    sampler.n_authors = n_authors

    authors = sampler.at_fa_p2(phi, theta, test_matrix, samples, burn_in, spacing)

    return(authors)

def DADT_SVM(matrix, test_matrix, n_authors, doc_authors, vocab, stopwords):
    # set parameters
    num_atopics = 15
    num_dtopics = 5
    burn_in = 1  # 1000
    alpha_a = min(0.1, 5/num_atopics)
    alpha_d = min(0.1, 5/num_dtopics)
    eta = 1
    epsilon = 0.009
    delta_a = 4.889
    delta_d = 1.222
    samples = 2
    spacing = 1 # 100
    test_samples = 2#10
    test_burn_in = 3#10
    test_spacing = 2#10
    chains = 1#2

    num_test_docs = test_matrix.shape[0]

    beta_a = np.array([0.01 + epsilon if word in stopwords else 0.01 for word in vocab])
    beta_d = np.array([0.01 - epsilon if word in stopwords else 0.01 for word in vocab])

    print('Starting!')
    (atopic_phi_sampled, atopic_theta_sampled, dtopic_phi_sampled, dtopic_theta_sampled, pi_sampled, chi) = dadt.train(matrix, vocab, doc_authors, num_dtopics, num_atopics, n_authors, alpha_a, beta_a, alpha_d, beta_d, eta, delta_a, delta_d, burn_in, samples, spacing)

    print("Testing")

    (dtopic_theta_test, atopic_theta_test, pi_test ) = dadt.classify(test_matrix, chains, test_burn_in, test_samples, test_spacing, num_dtopics, num_atopics, alpha_a, alpha_d, beta_a, beta_d, eta, delta_a, delta_d, dtopic_phi_sampled, atopic_phi_sampled)

    print("Main")
    num_training_docs = matrix.shape[0]
    num_test_docs = test_matrix.shape[0]
    training_matrix = np.zeros((num_training_docs, num_atopics + num_dtopics))
    for doc in range(num_training_docs):
        training_doc_author = doc_authors[doc][0]
        vector = np.concatenate((dtopic_theta_sampled[doc],atopic_theta_sampled[training_doc_author]))
        training_matrix[doc] = vector

    svm_test_matrix = np.zeros((num_test_docs, num_atopics + num_dtopics))

    for doc in range(num_test_docs):
        vector = np.concatenate((dtopic_theta_test[doc],atopic_theta_test[doc]))
        svm_test_matrix[doc] = vector

    svm_model = ll.train(sum(doc_authors, []), matrix.tolist(), '-c 4')
    p_label, p_acc, p_val = ll.predict(np.random.rand(num_test_docs), svm_test_matrix.tolist(), svm_model)
    return p_label

def DADT_P(matrix, test_matrix, n_authors, doc_authors, vocab, stopwords):
    # set parameters
    num_atopics = 15
    num_dtopics = 5
    burn_in = 1  # 1000
    alpha_a = min(0.1, 5/num_atopics)
    alpha_d = min(0.1, 5/num_dtopics)
    eta = 1
    epsilon = 0.009
    delta_a = 4.889
    delta_d = 1.222
    samples = 2
    spacing = 1 # 100
    test_samples = 2
    test_burn_in = 3
    test_spacing = 2
    chains = 2

    beta_a = np.array([0.01 + epsilon if word in stopwords else 0.01 for word in vocab])
    beta_d = np.array([0.01 - epsilon if word in stopwords else 0.01 for word in vocab])

    print('Starting!')
    (atopic_phi_sampled, atopic_theta_sampled, dtopic_phi_sampled, dtopic_theta_sampled, pi_sampled, chi) = dadt.train(matrix, vocab, doc_authors, num_dtopics, num_atopics, n_authors, alpha_a, beta_a, alpha_d, beta_d, eta, delta_a, delta_d, burn_in, samples, spacing)

    print("Classifying")

    (atopic_theta_test, dtopic_theta_test, pi_test ) = dadt.classify(matrix, chains, test_burn_in, test_samples, test_spacing, num_dtopics, num_atopics, alpha_a, alpha_d, beta_a, beta_d, eta, delta_a, delta_d, dtopic_phi_sampled, atopic_phi_sampled)

    print("Deciding")

    authors = dadt.dadt_p(test_matrix, n_authors, atopic_phi_sampled, dtopic_phi_sampled, atopic_theta_sampled, dtopic_theta_test, pi_test, chi)

    return(authors)