from enum import Enum


class TypeTarget(str, Enum):
    ETARGET = 'eTarget'
    STARGET = 'sTarget'
    TARGETFRAME = 'targetFrame'
    TARGET = 'target'


class Target:
    """
    This class is a parent class for eTarget(s) and sTarget(s).
    This class has target_id, span_start and span_end that both eTarget(s) and sTarget(s)
    include these parameters.
    """
    unique_id = -1 # unique id of each annotation
    sentence_id = -1  # index of sentence within document
    doc_id = ""  # ID of the document.
    text = ""  # sentence in which the annotated head occurs
    target_id = ""  # id of eTarget or sTarget
    head_start = -1  # start span of eTarget or sTarget
    head_end = -1  # end span of eTarget or sTarget
    head = ""  # target of annotation within sentence
    annotation_type: TypeTarget  # The type of annotation

    def __init__(self, this_text, this_id, this_head_start, this_head_end, this_annotation_type,
                 this_head="", this_sentence_id=-1, unique_id=-1, doc_id=""):
        """
        The init method (constructor) for Target class.
        """
        self.unique_id = unique_id
        self.target_id = this_id
        self.sentence_id = this_sentence_id
        self.text = this_text
        self.head_start = this_head_start
        self.head_end = this_head_end
        self.head = this_head
        self.annotation_type = TypeTarget(this_annotation_type)
        self.doc_id = doc_id


class eTarget(Target):
    """
    This class is for entity/event level target(s).
    """
    type_etarget = ""  # type of eTarget, possible values: entity, event, other
    is_negated = None  # this is True when eTarget is nagated
    is_referred_in_span = None  # this is optional attribute

    def __init__(self, this_text, this_id, this_head_start, this_head_end, this_annotation_type,
                 this_type_etarget, this_head="", this_sentence_id=-1, this_is_negated=None,
                 this_is_referred_in_span=None, unique_id=-1):
        """
        The init method (constructor) for eTarget class.
        """
        Target.__init__(self, this_text, this_id, this_head_start, this_head_end, this_annotation_type,
                        this_head, this_sentence_id, unique_id)
        self.type_etarget = this_type_etarget
        self.is_negated = this_is_negated
        self.is_referred_in_span = this_is_referred_in_span


class sTarget(Target):
    """
    This class is for span based target(s).
    """
    target_uncertain = ""  # Used when an annotator is uncertain about whether this is the correct target for the attitude.
    etarget_link = []  # consist id of eTarget(s) that coverer by this sTarget span

    def __init__(self, this_text, this_id, this_head_start, this_head_end, this_annotation_type,
                 this_head="", this_sentence_id=-1, this_target_uncertain="",
                 this_etarget_link=[], unique_id=-1):
        """
        The init method (constructor) for sTarget class.
        """
        Target.__init__(self, this_text, this_id, this_head_start, this_head_end, this_annotation_type,
                        this_head, this_sentence_id, unique_id)
        self.target_uncertain = this_target_uncertain
        self.etarget_link = this_etarget_link


class TargetCollection:
    """
    Holds a collection of Target objects for a single corpus, each of which represents
    a single Target annotation in the corpus.
    """

    # A dict which holds target objects which are made from target annotations from the MPQA corpus. This dict's keys
    # are IDs of target objects and its values are the corresponding objects.
    target_instances = {}


    # Name of the corpus from which the objects in this collection were drawn.
    # This collection represents a single corpus.
    corpus = ""

    def __init__(self, this_corpus):
        """
        Stores the name of the corpus from which the objects are drawn.
        :param this_corpus:
        """
        self.target_instances = {}
        self.corpus = this_corpus

    def add_instance(self, new_instance):
        """
        Adds a single Target object to the collection for an actual annotation.
        :param new_instance: The Target object representing the Target annotation.
        :return: None.
        """
        # Add the new Target instance to the collection, indeed using the object's ID to put the object in a dict.
        self.target_instances[new_instance.unique_id] = new_instance

    def get_instance(self, instance_id):
        """
        Returns a single Target object from the collection by its ID, if not exists, None will be returned.
        :param instance_id: The ID of the Target annotation which is desired to be received.
        :return: None.
        """

        # Check if the desired Target object is available in the collection by searching the instance_id in the keys
        # set of target_instances dict.
        if instance_id in self.target_instances.keys():
            # Return the corresponding Target object by using its ID.
            return self.target_instances[instance_id]
        return None

    def get_all_instances(self):
        """
        Returns the list of Target objects.
        :return: A list of Target objects.
        """
        return self.target_instances

    def get_num_instances(self):
        """
        Gets the number of Target objects in this collection corresponding
        to actual annotations in the corpus.
        :return:  An integer, the count of Target objects.
        """
        return len(self.target_instances.keys())


    def del_instance(self, instance_id):
        """
        Deletes a single Target object from the collection by its ID (instance_id).
        :param instance_id: The ID of the Target annotation which is desired to be deleted.
        :return: None.
        """
        # Check if the desired object (which its ID is instance_id) is available in the collection by using the ID.
        if instance_id in self.target_instances.keys():
            # Delete the object which is desired to be deleted.
            del self.target_instances[instance_id]

    def reset_collection(self):
        """
        Reset (set empty) the Target objects collection.
        :return: None.
        """
        self.target_instances = dict()
