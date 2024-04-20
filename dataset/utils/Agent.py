class Agent:
    """
    This class is used for agent annotation type.
    """

    unique_id = -1 # unique id of each annotation
    id = ""  # ID of this agent.
    nested_source = []  # The nested-source is a list of agent IDs beginning with the writer and ending with
    # the ID for the immediate agent being referenced.
    agent_uncertain = ""  # Used when the annotator is uncertain whether the agent is the correct source of a
    # private state/speech event.
    doc_id = ""  # ID of the document.
    sentence_id = -1  # index of sentence within document.
    text = ""  # sentence in which the annotated head occurs.
    head_start = -1  # start span of agent.
    head_end = -1  # end span of agent.
    head = ""  # target of annotation.

    def __init__(self, id="", agent_uncertain="", text="", head_start=-1, head_end=-1,
                 head="", doc_id="", sentence_id=-1, nested_source=[], unique_id=-1):
        """
        The init method (constructor) for Agent class.
        """
        self.unique_id = unique_id
        self.id = id
        self.agent_uncertain = agent_uncertain
        self.doc_id = doc_id
        self.sentence_id = sentence_id
        self.text = text
        self.head_start = head_start
        self.head_end = head_end
        self.head = head
        self.nested_source = nested_source


class AgentCollection:
    """
    Holds a collection of Agent objects for a single corpus, each of which represents
    a single Agent annotation in the corpus.
    """
    # A dict which holds agent objects which are made from agent annotations from the MPQA corpus.
    # This dict's keys are IDs of agent objects and its values are the corresponding objects.
    agent_instances = {}

    # Name of the corpus from which the objects in this collection were drawn.
    # This collection represents a single corpus.
    corpus = ""

    def __init__(self, this_corpus):
        """
        Stores the name of the corpus from which the objects are drawn.
        :param this_corpus:
        """
        self.agent_instances = {}
        self.corpus = this_corpus

    def add_instance(self, new_instance):
        """
        Adds a single Agent object to the collection for an actual annotation.
        :param new_instance: The Agent object representing the Agent annotation.
        :return: None.
        """
        # Add the new agent instance to the collection, indeed using the object's ID to put the object in a dict.
        self.agent_instances[new_instance.unique_id] = new_instance

    def get_instance(self, instance_id):
        """
        Returns a single Agent object from the collection by its ID, if not exists, None will be returned.
        :param instance_id: The ID of the Agent annotation which is desired to be received.
        :return: None.
        """
        # Check if the desired agent object is available in the collection by searching the instance_id in the keys
        # set of agent_instances dict.
        if instance_id in self.agent_instances.keys():
            # Return the corresponding agent object by using its ID.
            return self.agent_instances[instance_id]
        return None

    def get_all_instances(self):
        """
        Returns the list of Agent objects.
        :return: A list of Agent objects.
        """
        return self.agent_instances

    def get_num_instances(self):
        """
        Gets the number of Agent objects in this collection corresponding
        to actual annotations in the corpus.
        :return:  An integer, the count of Agent objects.
        """
        return len(self.agent_instances.keys())

    def del_instance(self, instance_id):
        """
        Deletes a single Agent object from the collection by its ID.
        :param instance_id: The ID of the Agent annotation which is desired to be deleted.
        :return: None.
        """
        # Check if the desired object (which its ID is instance_id) is available in the collection by using the ID.
        if instance_id in self.agent_instances.keys():
            # Delete the object which is desired to be deleted.
            del self.agent_instances[instance_id]

    def reset_collection(self):
        """
        Reset (set empty) the Agent objects collection.
        :return: None.
        """
        self.agent_instances = dict()
