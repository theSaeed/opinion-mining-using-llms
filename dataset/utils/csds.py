# Cognitive States Data Structure (CSDS): Represents information about
# the writer's cognitive state and the text from which we have gleaned
# this information.
# Basic information per CSDS instance:
# - the text
# - the proposition in the text about which we record the cognitive state;
#     we represent this by the start and end of the syntactic headword of the
#     proposition
# - the belief value; the values used are corpus-specific (or experiment-specific),
#     for example CB, NCB, ROB, NA
# - the sentiment value; the values used are corpus-specific (or experiment-specific),
#     for example pos, neg

# Many more fields will be added as we go along.

from itertools import chain
from enum import Enum


class Type(str, Enum):
    SENTIMENT = 'sentiment'
    ARGUING = 'arguing'
    AGREEMENT = 'agreement'
    INTENTION = 'intention'
    SPECULATION = 'speculation'
    OTHER_ATTITUDE = 'other_attitude'
    EXPRESSIVE_SUBJECTIVITY = 'expressive_subjectivity'
    OBJECTIVE_SPEECH_EVENT = 'objective_speech_event'
    DIRECT_SUBJECTIVE = 'direct_subjective'
    SENTENCE = 'sentence'
    UNKNOWN = 'unknown'


class CSDS:
    """
    Cognitive States Data Structure (CSDS): Represents information about 
    the writer's cognitive state and the text from which we have gleaned 
    this information.
    
    List of Changes CSDS for MPQA:
        1. added polarity. Its possible values:positive, negative, both, neutral,
        uncertain-positive, uncertain-negative, uncertain-both, uncertain-neutral.
        2. added intensity. Its possible values: low, medium, high, extreme.
        3. added Enum for Type of annotation.
        4. added target_link that contains a list of the id of e/sTargets.
        5. added unique_id to each annotation
    """
    unique_id = -1  # unique id of each annotation
    doc_id = -1  # unique index of origin document within corpus, value: name of doc.
    sentence_id = -1  # index of sentence within document.
    text = ""  # sentence in which the annotated head occurs.
    head_start = -1  # offset within sentence of start of head word of proposition.
    head_end = -1  # offset of end of head word of proposition.
    head = ""  # target of annotation within sentence.
    belief = ""  # belief value (values are corpus-specific).
    sentiment = ""  # sentiment value (values are corpus-specific).
    polarity = ""  # polarity of the type of annotation.
    intensity = ""  # intensity of the type of annotation.
    annotation_type: Type  # The type of annotation.
    target_link = []  # A list that contains the IDs of e/sTargets.
    attitude_link = [] # A list which contains the IDs of attitudes.
    nested_source_link = []  # A list that contains the IDs of nested-souces.
    expression_intensity = None  # An attribute for expression intensity.
    implicit = None  # An attribute for implicit feature of the direct subjective annotation type.

    def __init__(
            self, this_text, this_head_start, this_head_end, this_belief, this_polarity, this_intensity,
            this_annotation_type, this_expression_intensity=None, this_implicit=None, this_target_link=[],
            this_attitude_link=[], this_agent_link=[], this_head="", this_doc_id=-1,
            this_sentence_id=-1, unique_id=-1
    ):
        self.unique_id = unique_id
        self.doc_id = this_doc_id
        self.sentence_id = this_sentence_id
        self.text = this_text
        self.head_start = this_head_start
        self.head_end = this_head_end
        self.head = this_head
        self.belief = this_belief
        self.polarity = this_polarity
        self.intensity = this_intensity
        self.annotation_type = Type(this_annotation_type)
        self.target_link = this_target_link
        self.attitude_link = this_attitude_link
        self.nested_source_link = this_agent_link
        self.expression_intensity = this_expression_intensity
        self.implicit = this_implicit

    def get_info_short(self):
        return (
            f"<CSDS Doc: {self.doc_id} Sentence: {self.sentence_id} Head: {self.head_start} "
            f"Text {self.text} Head: {self.head} Belief: {self.belief}"
        )

    def get_marked_text(self):
        # puts stars around annotated snippet
        new_sentence = self.text[0:self.head_start] + "* " + self.text[self.head_start:self.head_end] + \
                       " *" + self.text[self.head_end: len(self.text)]
        return new_sentence

    def get_belief(self):
        return self.belief

    def get_doc_id(self):
        return self.doc_id


class CSDSCollection:
    """
    Holds a collection of CSDS objects for a single corpus, each of which represents
    a single example in the corpus.
    Each example consists of a sentence in the corpus, together with a label
    annotating a word or phrase in the sentence, which is called the head.
    A single collection represents an entire corpus.
    Maintains separate lists of CSDS objects whose labels correspond
    to actual annotations and to default pseudo-annotations (for un-annotated
    tokens), respectively.  The pseudo-annotation appears as the 'O' label here.
    The client code determines whether to populate the second list.
    """
    # List of examples from the corpus that were originally annotated with a real label.
    labeled_instances = []

    # List of examples consisting of non-annotated words with the "O" pseudo-label.
    o_instances = []

    # Name of the corpus from which the examples in this collection were drawn.
    # This collection represents a single corpus.
    corpus = ""

    def __init__(self, this_corpus):
        """
        Stores the name of the corpus from which the examples are drawn.
        :param this_corpus:
        """
        self.labeled_instances = []
        self.o_instances = []
        self.corpus = this_corpus

    def add_labeled_instance(self, new_instance):
        """
        Adds a single CSDS object to the collection for an actual annotation.
        :param new_instance: The CSDS object representing the example.
        :return: None.
        """
        self.labeled_instances.append(new_instance)

    def add_o_instance(self, new_instance):
        """
        Adds a single CSDS object to the collection for an un-annotated word.
        :param new_instance: The CSDS object representing the example.
        :return: None.
        """
        self.o_instances.append(new_instance)

    def add_list_of_labeled_instances(self, list_of_new_instances):
        """
        Adds a list of CSDS objects to this collection, where each
        CSDS object corresponds to an actual annotation in the corpus.
        :param list_of_new_instances: List of CSDS objects with a label based on an annotation.
        :return: None.
        """
        self.labeled_instances.extend(list_of_new_instances)

    def add_list_of_o_instances(self, list_of_new_instances):
        """
        Adds a list of CSDS objects to this collection, where each
        CSDS object corresponds to word in the corpus that has not been annotated.
        :param list_of_new_instances: List of CSDS objects with the 'O' label.
        :return: None.
        """
        self.o_instances.extend(list_of_new_instances)

    def get_all_instances(self):
        """
        Returns two lists of CSDS objects:
        1. The first corresponding to actual annotations in the corpus
        2. The second corresponding to non-annotated words in the corpus.
        :return: A pair of lists of CSDS objects.
        """
        return self.labeled_instances, self.o_instances

    def get_next_instance(self):
        """
        Provides for iteration over all CSDS objects in the collection.
        :return: An iterator that includes all internal lists of CSDS objects.
        """
        return chain(self.labeled_instances, self.o_instances)

    def get_next_labeled_instance(self):
        """
        Provides for iteration over only those CSDS objects in the collection
        that correspond to annotations in the corpus.
        :return: An iterator that includes only the list of labeled instances.
        """
        for instance in self.labeled_instances:
            yield instance

    def get_next_o_instance(self):
        """
        Provides for iteration over only those CSDS objects in the collection
        that correspond to words not annotated in the corpus.
        :return: An iterator that includes only the list of instances labeled 'O.'
        """
        for instance in self.o_instances:
            yield instance

    def get_num_labeled_instances(self):
        """
        Gets the number of CSDS objects in this collection corresponding
        to actual annotations in the corpus.
        :return:  An integer, the count of labeled CSDS objects.
        """
        return len(self.labeled_instances)

    def get_o_instances_length(self):
        """
            Gets the number of CSDS objects in this collection corresponding
            to un-annotated instances of words in the corpus.
            :return:  An integer, the count of 'O'-labeled CSDS objects.
            """
        return len(self.o_instances)

    def get_info_short(self):
        """
        Gets a brief string representation of this collection.
        :return: A string containing essential details about this collection.
        """
        return (
            f"<CSDS collection from \"{self.corpus}\": {str(len(self.labeled_instances))} "
            f"labeled_instances>"
        )

    def get_info_long(self):
        """
        Gets a detailed string representation of the collection.
        :return: A string including representations of each labeled instance in the collection.
        """
        message = (
            f"<CSDS collection from \"{self.corpus}\": {str(len(self.labeled_instances))} "
            f"labeled_instances:\n"
        )
        for instance in self.labeled_instances:
            message += f"   {instance.get_info_short()}\n"
        message += ">\n"
        return message
