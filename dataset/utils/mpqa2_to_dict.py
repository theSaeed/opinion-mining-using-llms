# mpqa2_to_dict helps to convert MPQA stand-off format to python dictionaries.
# It provides the following functionalities:
# 1) Clean up the MPQA 2.0 corpus
# 2) Convert an MPQA document to a dictionary
# 3) Convert an entire corpus to a dictionary

import os
import re

HAS_LIST_OF_IDS = [ # These attributes may have any number of ids. (>= 0)
    "nested-source", "attitude-link", "insubstantial",
    "target-speech-link", "target-link"
]

PREFIXES_FOR_LINKS = { # Add a prefix to links
    'nested-source': 'agent-',
    'attitude-link': 'attitude-',
    'target-link': 'target-',
    'target-speech-link': 'target-speech-',
}

class mpqa2_to_dict:
    """
    mpqa2_to_dict helps to clean up the corpus and convert MPQA stand-off format to python dictionaries.
    """

    corpus_name = "" # Name of the corpus from which the documents were drawn.
    mpqa_dir = "database.mpqa.2.0.cleaned" # mpqa root directory

    def __init__(self, corpus_name="", mpqa_dir="database.mpqa.2.0.cleaned"):
        self.corpus_name = corpus_name
        self.mpqa_dir = mpqa_dir

    def __add_prefix_to_links(self, key, val):
        return PREFIXES_FOR_LINKS.get(key, '') + val

    def doc_to_dict(self, docname):
        """
        It converts an MPQA document to a python dictionary.
        :param docname: The name of the document to be converted.
        :return: A python dictionary representing the document.
        """
        # example: ./docs/20011024/21.53.09-11428
        with open(os.path.join(self.mpqa_dir, "docs", docname), encoding="utf8") as doc_file:
            doc_text = doc_file.read()
        
        # example: ./man_anns/20011024/21.53.09-11428/gatesentences.mpqa.2.0
        with open(os.path.join(self.mpqa_dir, "man_anns", docname, "gatesentences.mpqa.2.0")) as sentences_file:
            sentences_lines = sentences_file.readlines()
        # All the other annotation lines with no attributes, have an extra \t
        # at the end of the line except sentences
        # Here we try to add an extra \t manually to the sentences lines
        sentences_lines = [sentence[:-1]+'\t\n' for sentence in sentences_lines]

        # example: ./man_anns/20011024/21.53.09-11428/gateman.mpqa.lre.2.0
        anno_lines = []
        with open(os.path.join(self.mpqa_dir, "man_anns", docname, "gateman.mpqa.lre.2.0")) as anno_file:
            anno_lines = anno_file.readlines()
        anno_lines += sentences_lines # Sentences are also annotation lines

        # Final output
        output = {
            "agent": [],
            "expressive-subjectivity": [],
            "direct-subjective": [],
            "objective-speech-event": [],
            "attitude": [],
            "target": [],
            "target-speech": [],
            "sentence": [],
            "annotations": {}
        }

        # Process all annotation lines
        for anno in anno_lines:
            if len(anno) < 1: # If the line is empty then skip it.
                continue
            if anno[0] == '#': # If it is a comment then skip it.
                continue

            # Parsing the main components of an annotation line.
            line_id, span, data_type, anno_type, attributes = anno.split('\t')
            anno_type = anno_type[5:] # Remove "GATE_" from annotation type
            
            # Skip "inside" & "split" annotations
            if anno_type in ['inside', 'split']:
                continue

            # Converting span to a tuple of ints.
            span = span.split(',')
            span = (int(span[0]), int(span[1]))
            
            # Removes ' \n' at the end of the string.
            attributes = attributes.strip()
            
            # A temporary variable for an annotation line before knowing its ID.
            temp_dict = {
                "anno-type": anno_type,
                "head": doc_text[span[0]:span[1]],
                "line-id": int(line_id),
                "span-in-doc": span,
            }
            
            # Process all attributes
            if len(attributes) != 0:
                # Splits with the whitespaces out of the quotes as the delimeter
                attributes = attributes.strip()
                attributes = re.split(r' (?=([^"]*"[^"]*")*[^"]*$)', attributes)
                for attribute in attributes:
                    key, val = attribute.split('=')
                    key, val = key.strip(), val.strip()
                    val = val[1:-1] # Removes double quotation marks
                    if key in HAS_LIST_OF_IDS:
                        temp_dict[key] = [] if val == "none" or val == "" else [self.__add_prefix_to_links(key, v.strip()) for v in val.split(',')]
                    else:
                        temp_dict[key] = self.__add_prefix_to_links(key, val.strip())

            # We probably know the identifier assigned to the annotation by now
            # except some of the agnets and the sentences
            id = temp_dict.pop("id", line_id)
            if id == '': # Replace empty IDs with line IDs
                id = line_id
            
            # There are some different annotation lines with the same IDs. Here
            # we are trying to differentiate between "some" of these cases,
            # which have different annotation types.
            id = anno_type + '-' + id 

            # Updating the final output
            if id not in output["annotations"]:
                output["annotations"][id] = [temp_dict]
            else:
                output["annotations"][id].append(temp_dict)
            
            if anno_type in output:
                if id not in output[anno_type]:
                    output[anno_type].append(id)
            else: # If there's a new type of annotation, warn us in red!
                output[anno_type] = [id]
                print("\033[91m <UNKNOWN ANNO: {}>\033[00m".format(anno_type))
        
        # Set sentence-id, sentence and span-in-sentence
        for key in output["annotations"].keys():
            for key_i in range(len(output["annotations"][key])): # For duplicated IDs
                if key in output["sentence"]:
                    continue # Skip changing sentences
                # Search for the corresponding sentence
                for sentence_id in output["sentence"]:
                    # Checks if the annotation is whithin this sentence
                    if  output["annotations"][sentence_id][0]["span-in-doc"][0] <= output["annotations"][key][key_i]["span-in-doc"][0]\
                    and output["annotations"][sentence_id][0]["span-in-doc"][1] >= output["annotations"][key][key_i]["span-in-doc"][1]:
                        output["annotations"][key][key_i]["sentence-id"] = sentence_id
                        output["annotations"][key][key_i]["text"] = output["annotations"][sentence_id][0]["head"]
                        output["annotations"][key][key_i]["span-in-sentence"] = (
                            output["annotations"][key][key_i]["span-in-doc"][0] - output["annotations"][sentence_id][0]["span-in-doc"][0],
                            output["annotations"][key][key_i]["span-in-doc"][1] - output["annotations"][sentence_id][0]["span-in-doc"][0]
                        )
                        break

        return output

    def corpus_to_dict(self, doclist=None, doclist_filename='doclist.2.0'):
        """
        It converts an entire list of MPQA documents to a python dictionary.
        :param doclist: The list of document names to be converted. If set, doclist_filename will be ignored.
        :param doclist_filename: The name of the file which contains a list of the document names.
        :return: A python dictionary representing the corpus.
        """
        if doclist is None:
            doclist = self.__doclistfile_to_doclist(doclist_filename)
        output = {
            "corpus": self.corpus_name, # Name of the corpus from which the documents were drawn.
            "doclist": doclist,         # List of the document names.
            "docs": {}                  # Dictionary of document annotations in dictionary format.
        }
        for docname in doclist:
            output["docs"][docname] = self.doc_to_dict(docname)
        return output
    
    def __doclistfile_to_doclist(self, doclist_filename='doclist.2.0'):
        """
        An auxiliary function for converting a file of a list of document names to a list of document names.
        :param doclist_filename: The name of the file which contains a list of the document names.
        :return: A python list containing the document names.
        """
        # example: ./doclist.2.0
        doclist = []
        with open(os.path.join(self.mpqa_dir, doclist_filename)) as doclist_file:
            for doc in doclist_file.readlines():
                doclist.append(doc[:-1]) # Removes \n at the end of the line
        return doclist
