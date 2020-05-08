import numpy as np


def normal_dst_from_samples(samples):
    sample_standard_deviation = np.std(samples, axis=0, ddof=1)
    sample_mean = np.mean(samples)
    sample_normal_dst = np.random.normal(loc=sample_mean, scale=sample_standard_deviation, size=None)
    return sample_normal_dst


def best_translation():
    pass

def main():
    # extract standard deviation from a list of values
    A_rank = [0.8, 0.4, 1.2, 3.7, 2.6, 5.8]
    # population standard deviation
    population_standard_deviation = np.std(A_rank, axis=0, ddof=0)
    print(population_standard_deviation)
    # sample standard deviation
    sample_standard_deviation = np.std(A_rank, axis=0, ddof=1)
    print(sample_standard_deviation)
    # mean
    mean = np.mean(A_rank)
    print(mean)
    # generate a random normal distribution of size 2x3 with mean at 1 and standard deviation of 2
    x = np.random.normal(loc=1, scale=2, size=(2, 3))
    print(x)
    # generate a random normal distribution of size 1 with mean at 1 and standard deviation of 2 (the size is the one that we want)
    x = np.random.normal(loc=1, scale=2, size=None)
    print(x)

if __name__ == '__main__':
    main()