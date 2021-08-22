import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    prob_cache = []
    # sort people into people_with_parents and people_without_parents
    people_with_parents = {}
    people_without_parents = {}
    for person, values in people.items():
        if values['mother'] == None and values['father'] == None:
            people_without_parents[person] = values
        else:
            people_with_parents[person] = values


    # calculate probabilities of people_without_parents first
    for person, values in people_without_parents.items():

        
        # if want to calculate probability of one_gene
        if person in one_gene:
            gene = 1
        elif person in two_genes:
            gene = 2
        else:
            gene = 0
        if person in have_trait:
            trait = True
        else:
            trait = False
        prob_cache.append(PROBS["gene"][gene] * PROBS["trait"][gene][trait])


    # calculate probabilities of people_with_parents 
    for person, values in people_with_parents.items():
        # probability of getting it from father
        father_name = values['father']
        if father_name in two_genes:
            father_prob = 1 - PROBS["mutation"]
        elif father_name in one_gene:
            father_prob = 0.5
        else:
            father_prob = PROBS['mutation']
            
        # probability of getting from mother
        mother_name = values['mother']
        # if mother has X genes
        if mother_name in two_genes:
            mother_prob = 1 - PROBS["mutation"]
        elif mother_name in one_gene:
            mother_prob = 0.5
        else:
            mother_prob = PROBS['mutation']
            
        # probability of child with X gene
        if person in one_gene:
            child_gene = 1
            gene_prob = father_prob * (1-mother_prob) + mother_prob*(1-father_prob)
        elif person in two_genes:
            child_gene = 2
            gene_prob = father_prob * mother_prob
        else:
            child_gene = 0
            gene_prob = (1 - father_prob) * (1-mother_prob)

    
        # probability of trait given X copy of gene
        if person in have_trait:
            prob = gene_prob * PROBS['trait'][child_gene][True]
        else: 
            prob = gene_prob * PROBS['trait'][child_gene][False]
        prob_cache.append(prob)

    
    
    result = 1
    for x in prob_cache:
        result = result*x
    return result

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person, values in probabilities.items():
        # if want to calculate probability of one_gene
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p
        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p




def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """

    for person, values in probabilities.items():
        for item, itemvalues in values.items():
            sum_of_val = 0
            for k,v in itemvalues.items():
                sum_of_val += v
            for k,v in itemvalues.items():
                itemvalues[k] = v/sum_of_val

            
if __name__ == "__main__":
    main()
