class autocorrect():

    def __init__(self, min_threshold):
        assert isinstance(min_threshold, int)
        assert min_threshold >= 0, "Assign a value greater or equal to zero"
        self.min_threshold = min_threshold

    def _check_prepare_text(self, text):
        "Checks input data (text) and converts it to string if necessary"

        if isinstance(text, list):
            text = ' '.join([str(x) for x  in text])
            return text
        elif isinstance(text, str):
            return text
        else:
            raise TypeError("Input either a list of strings or a string")

    def learn(self, text):
        "Learn word distribution given input data"

        from collections import Counter

        text = self._check_prepare_text(text)

        self.words = self._get_words(text)
        self.letters = self._get_letters(text)
        self.word_freq = Counter(self.words)
        self.lookup = self._prune_dictionary(dictionary=self.word_freq, threshold=self.min_threshold)
        self.lookup_wordset = set(self.lookup.keys())

    def print_summary(self):
        "Prints a short summary of reference data"

        assert hasattr(self, "words"), "Input reference data using the .learn() method"

        print("Number of words: {}\n\n".format(len(self.words)))
        print("Number of letters other than ascii characters: {}\n\n{}\n".format(len(self.letters),self.letters))

        print("Most common words:\n")
        for word_tup in self.word_freq.most_common()[:20]:
            print(word_tup)

    def save_state(self,path):

        with open(path, "w") as f:
            for k,v in  self.word_freq.items():
                f.write( "{}\t{}\n".format(k,v))

    def read_state(self,path):

        from collections import Counter
        state = {}

        with open(path, "r") as f:
            for line in f.read().split("\n"):
                if not line == '':
                    k,v = line.split("\t")
                    state[k] = int(v)

        self.words = state.keys()
        self.letters = self._get_letters(' '.join(state.keys()))
        self.word_freq = Counter(state)
        self.lookup = self._prune_dictionary(dictionary=self.word_freq, threshold=self.min_threshold)
        self.lookup_wordset = set(self.lookup.keys())



    def update(self, text):
        "Updating reference data with new (additional text)"
        from collections import Counter

        text = self._check_prepare_text(text)

        new_words = self._get_words(text)
        self.words += new_words
        new_letters = self._get_letters(text)
        self.letters = ''.join(list(set(self.letters + new_letters)))
        new_word_freq = Counter(self.words)

        self.word_freq.update(new_word_freq)
        self.lookup = self._prune_dictionary(dictionary=self.word_freq, threshold=self.min_threshold)
        self.lookup_wordset = set(self.lookup.keys())


    def _prune_dictionary(self, dictionary, threshold):
        return {w : dictionary[w] for w in dictionary if dictionary[w] >= threshold}

    def _get_words(self, text):
        "Helper function, returns words in text"
        import re

        return re.findall(r'\w+', text.lower())

    def _get_letters(self, text):
        "Helper function, returns letters in text"
        import re


        words = self._get_words(text)
        letters = list(''.join(words))

        letters = list(set(letters))

        return ''.join(letters)

    def _pr_word(self, word, N = None):
        "Probability of `word`."

        if N == None:
            N =  sum(self.lookup.values())

        return self.lookup[word]/float(N)

    def _candidates(self, word):
        "Generate possible spelling corrections for word."
        return (self._known([word]) or self._known(self._edit_dist1(word)) or self._known(self._edit_dist2(word)) or [word])

    def _known(self, words):
        "The subset of `words` that appear in the dictionary of WORDS."
        return set(w for w in words if w in self.lookup_wordset)


    def _edit_dist2(self, word):
        "All edits that are two edits away from `word`."
        return (e2 for e1 in self._edit_dist1(word) for e2 in self._edit_dist1(e1))

    def _edit_dist1(self, word):
        "All edits that are one edit away from `word`."
        import string
        letters    = list(set(string.ascii_lowercase + self.letters))
        splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]


        deletes    = [L + R[1:]               for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
        inserts    = [L + c + R               for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def _correction(self, word):
        "Most probable spelling correction for word."
        try:
            return max(self._candidates(word), key=self._pr_word)
        except KeyError:
            return word

    def correct(self, string):
        """
        Most probable spelling correction for words in the string.

        You might need to run:
        > import nltk
        > nltk.download('perluniprops')
        """

        import re
        from nltk.tokenize import word_tokenize
        from nltk.tokenize.treebank import TreebankWordDetokenizer

        d = TreebankWordDetokenizer()
        words = word_tokenize(string)

        corrected = [self._correction(word) if bool(re.search(r'\w+', word)) else word for word in words]

        return d.detokenize(corrected)
