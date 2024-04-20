from re import A
from mpqa2_to_dict import mpqa2_to_dict
from csds import CSDS, CSDSCollection
from Target import sTarget, eTarget, Target, TargetCollection
from Agent import Agent, AgentCollection

class JSON2CSDS:
    """
    This is a class in order to convert JSON file to CSDS.
    """

    def __init__(self, corpus_name="", mpqa_dir="database.mpqa.2.0.cleaned", talkative=True, mpqa_version=2):
        """
        The init method (constructor) for JSON2CSDS class.
        """
        self.corpus_name = corpus_name
        self.mpqa_dir = mpqa_dir
        self.talkative = talkative
        self.mpqa_version = mpqa_version

    def produce_json_file(self):
        """
        It uses the mpqa2_to_dict or module mpqa3_to_dict in order to convert MPQA to JSON (dict) file.
        :return: A JSON file which is obtained from MPQA corpus.
        """
        result = {}
        if self.mpqa_version == 2:
            m2d = mpqa2_to_dict(self.corpus_name, self.mpqa_dir)
            result = m2d.corpus_to_dict()

        return result
    
    
    def __type_mapper(self, key):
        """
        A mapping between types and their corresponding number based on the enum.
        :param key: type of the annotation.
        :return: Type's corresponding number based on the enum.
        """
        # Currently, it does not do anything special!
        type_map_dict = {
            'sentiment': 'sentiment',
            'arguing': 'arguing',
            'agreement': 'agreement',
            'intention': 'intention',
            'speculation': 'speculation',
            'specilation': 'speculation',
            'other-attitude': 'other_attitude',
            'expressive_subjectivity': 'expressive_subjectivity',
            'objective_speech_event': 'objective_speech_event',
            'direct_subjective': 'direct_subjective',
            'sentence': 'sentence',
            'unknown': 'unknown'
        }
        return type_map_dict[key]

    def __alert_wrong_anno(self, anno, doc_id, error=None):
        """
        It is used for alerting wrong annotation(s).
        :param anno: The annotation that error(s) were happening in its process.
        :param error: The error(s) that happened.
        """
        if self.talkative:
            if str(error) != str("'text'"):
                print('===================\nWrong annotation!!')
                print(anno)
                print('Error details: (doc_id: ', doc_id, ')')
                print(error)
                print(f'Type of error: {error.__class__.__name__}')
                print('===================')
        else:
            pass

    def __go_get_targets(self, annos, target_id):
        """
        It goes after the targets in the target-links and fetches them.
        :param annos: A Python dict which represents all annotations in the doc.
        :param target_id: ID of the target.
        :return: A Python list of the targets.
        """
        targets = annos[target_id]['newETarget-link'] + annos[target_id]['sTarget-link']
        return targets

    def __go_get_targets_mpqa2(self, curr_annot):
        """
        It goes after the targets in the target-links and fetches them.
        :param target_id: ID of the target.
        :return: A Python list of the targets.
        """
        targets = curr_annot['target-link'] if 'target-link' in curr_annot else []
        return targets

    def __add_docname_to_list(self, doc_id, array):
        """
        Add doc_id to the begginging of each element in the array.
        :param doc_id: ID of the doc.
        :param array: Array of strings. (Possibley target/agent ids)
        :return: A python list of altered strings.
        """
        return [f'{doc_id}&&{s}' for s in array]

    def __process_one_agent(self, agent_anno, doc_id, agent_id=""):
        """
        It processes an agent type annotation.
        :param agent_anno: A Python dict which represents an agent annotation.
        :param doc_id: ID of the doc.
        :param agent_id: ID of the agent annotation.
        :return: An Agent object.
        """

        try:
            # Extract features from agent annotation.
            if agent_anno['span-in-doc'][0] == 0 and agent_anno['span-in-doc'][1] == 0:
                its_text = ''
                its_head_start = 0
                its_head_end = 0
                its_sentence_id = 0
            else:
                its_text = agent_anno['text']
                its_head_start = agent_anno['span-in-sentence'][0]
                its_head_end = agent_anno['span-in-sentence'][1]

                if 'sentence-id' in agent_anno:
                    its_sentence_id = doc_id + '&&' + agent_anno['sentence-id']
                else:
                    its_sentence_id = None

            # Create an Agent object based on the values of the agent annotation.
            agent_object = Agent(
                text=its_text,
                head_start=its_head_start,
                head_end=its_head_end,
                head=agent_anno['head'],
                doc_id=doc_id,
                sentence_id=its_sentence_id,
                id=agent_id,
                unique_id=doc_id + '&&' + agent_id
            )

            # Extract the optional attributes' values if they exist
            if 'agent-uncertain' in agent_anno:
                agent_object.agent_uncertain = agent_anno['agent-uncertain']
            if 'nested-source' in agent_anno:
                agent_object.nested_source = self.__add_docname_to_list(doc_id, agent_anno['nested-source'])

        except Exception as err:
            self.__alert_wrong_anno(agent_anno, doc_id, error=err)
            return None

        return agent_object

    def __process_agent(self, agent_annos, doc_id, agent_id=""):
        """
        It processes agent type annotations.
        :param agent_annos: A Python list which represents some agent annotations.
        :param doc_id: ID of the doc.
        :param agent_id: ID of the agent annotations.
        :return: One or several Agent objects.
        """
        all_results = []
        if len(agent_annos) > 1:
            print(f'\033[93m <Warning: Duplicated ID detected: {agent_id} in {doc_id}>\033[00m')
        for i in range(len(agent_annos)):
            if i == 0:
                res = self.__process_one_agent(agent_annos[i], doc_id, agent_id=agent_id)
            else:
                res = self.__process_one_agent(agent_annos[i], doc_id, agent_id=agent_id+"&&"+str(i))
            all_results.append(res)
        return all_results

    def __process_one_es(self, all_anno, es_id, es_anno, doc_id):
        """
        It processes an ES (expressive-subjectivity) type annotation.
        :param all_anno: A Python dict which represents all annotations in the doc.
        :param es_id: ID of the annotation.
        :param es_anno: A Python dict which represents an ES annotation.
        :param doc_id: ID of the doc.
        :return: A CSDS object.
        """

        # Extract features from ES annotation.
        try:
            # All possibilities
            possible = ['positive', 'negative', 'both', 'neutral', 'uncertain', 'pos', 'neg']

            # [WHY] -> needs more commenting
            if 'polarity' in es_anno:
                if es_anno['polarity'].count('-') == 2:
                    its_polarity = es_anno['polarity'].split('-')[1] + '-' + es_anno['polarity'].split('-')[2]
                elif es_anno['polarity'].count('-') == 1:
                    if es_anno['polarity'].split('-')[0] in possible:
                        its_polarity = es_anno['polarity'].split('-')[0] + '-' + es_anno['polarity'].split('-')[1]
                    else:
                        its_polarity = es_anno['polarity'].split('-')[1]
                else:
                    its_polarity = es_anno['polarity']
            elif 'ese-type' in es_anno:
                if es_anno['ese-type'].count('-') == 2:
                    its_polarity = es_anno['ese-type'].split('-')[1] + '-' + es_anno['ese-type'].split('-')[2]
                else:
                    if es_anno['ese-type'].split('-')[0] in possible:
                        its_polarity = es_anno['ese-type'].split('-')[0] + '-' + es_anno['ese-type'].split('-')[1]
                    else:
                        its_polarity = es_anno['ese-type'].split('-')[1]
            else:
                its_polarity = 'nothing'

            # Check 'intensity' which is an optional attribute.
            if 'intensity' in es_anno:
                its_intensity = es_anno['intensity']
            else:
                its_intensity = None

            # Create a CSDS object based on the values of the ES annotation.
            csds_object = CSDS(
                this_text=es_anno['text'],
                this_head_start=es_anno['span-in-sentence'][0],
                this_head_end=es_anno['span-in-sentence'][1],
                this_belief=None,
                this_polarity=its_polarity,
                this_intensity=its_intensity,
                this_annotation_type=self.__type_mapper('expressive_subjectivity'),
                this_target_link=self.__add_docname_to_list(
                    doc_id,
                    self.__go_get_targets(all_anno, es_anno['targetFrame-link']) if self.mpqa_version == 3 else []
                ),
                this_head=es_anno['head'],
                this_doc_id=doc_id,
                this_sentence_id=doc_id + '&&' + es_anno['sentence-id'],
                this_agent_link=self.__add_docname_to_list(
                    doc_id, es_anno['nested-source'] if 'nested-source' in es_anno else []
                ),
                unique_id=doc_id + '&&' + es_id
            )

        except Exception as err:
            self.__alert_wrong_anno(es_anno, doc_id, error=err)
            return None

        return csds_object

    def __process_es(self, all_anno, es_id, es_annos, doc_id):
        """
        It processes ES (expressive-subjectivity) type annotations.
        :param all_anno: A Python dict which represents all annotations in the doc.
        :param es_id: ID of the annotation.
        :param es_annos: A Python list which represents some ES annotations.
        :param doc_id: ID of the doc.
        :return: One or several CSDS objects.
        """
        all_results = []
        if len(es_annos) > 1:
            print(f'\033[93m <Warning: Duplicated ID detected: {es_id} in {doc_id}>\033[00m')
        for i in range(len(es_annos)):
            if i == 0:
                res = self.__process_one_es(all_anno, es_id, es_annos[i], doc_id)
            else:
                res = self.__process_one_es(all_anno, es_id, es_annos[i]+"&&"+str(i), doc_id)
            all_results.append(res)
        return all_results

    def __process_one_att(self, all_anno, att_id, att_anno, doc_id):
        """
        It processes an attitude type annotation.
        :param all_anno: A Python dict which represents all annotations in the doc.
        :param att_id: ID of the annotation.
        :param att_anno: A Python dict which represents an attitude annotation.
        :param doc_id: ID of the doc.
        :return: A CSDS object.
        """
        its_pol = None  # Polarity (default is None)
        its_type = self.__type_mapper('unknown')  # Type (default is unknown)

        if 'sentence-id' in att_anno:
            sent_id = doc_id + '&&' + att_anno['sentence-id']
        else:
            sent_id = None

        if 'intensity' in att_anno:
            inten = att_anno['intensity']
        else:
            inten = None

        # Extract features from attitude annotation.
        try:
            if 'attitude-type' in att_anno:
                if att_anno['attitude-type'].find('other') >= 0:  # [WHY]
                    its_type = self.__type_mapper('other-attitude')
                else:
                    # Extract polarity and type: check all of the cases such as corner cases. [WHY]
                    if att_anno['attitude-type'].find('-') != -1:
                        its_attitude_type = att_anno['attitude-type'].split('-')
                        length = len(its_attitude_type)
                        its_pol = 'positive' if its_attitude_type[length - 1].find('pos') >= 0 else 'negative'
                        its_type = self.__type_mapper('agreement') if its_attitude_type[length - 2].find('agree') >= 0 \
                            else self.__type_mapper(its_attitude_type[length - 2])
                    else:
                        its_type = self.__type_mapper(att_anno['attitude-type'])
            else:
                its_type = self.__type_mapper('unknown')

            # Extract features from attitude annotation.
            csds_object = CSDS(
                this_text=att_anno['text'],
                this_head_start=att_anno['span-in-sentence'][0],
                this_head_end=att_anno['span-in-sentence'][1],
                this_belief=None,
                this_polarity=its_pol,
                this_intensity=inten,
                this_annotation_type=its_type,
                this_target_link=self.__add_docname_to_list(
                    doc_id,
                    self.__go_get_targets(all_anno, att_anno['targetFrame-link']) if self.mpqa_version == 3 else
                    self.__go_get_targets_mpqa2(att_anno)
                ),
                this_head=att_anno['head'],
                this_doc_id=doc_id,
                this_sentence_id=sent_id,
                unique_id=doc_id + '&&' + att_id
            )

        except Exception as err:
            self.__alert_wrong_anno(att_anno, doc_id, error=err)
            return None

        return csds_object

    def __process_att(self, all_anno, att_id, att_annos, doc_id):
        """
        It processes some attitude type annotations.
        :param all_anno: A Python dict which represents all annotations in the doc.
        :param att_id: ID of the annotation.
        :param att_annos: A Python list which represents some attitude annotations.
        :param doc_id: ID of the doc.
        :return: One or several CSDS objects.
        """
        all_results = []
        if len(att_annos) > 1:
            print(f'\033[93m <Warning: Duplicated ID detected: {att_id} in {doc_id}>\033[00m')
        for i in range(len(att_annos)):
            if i == 0:
                res = self.__process_one_att(all_anno, att_id, att_annos[i], doc_id)
            else:
                res = self.__process_one_att(all_anno, att_id+"&&"+str(i), att_annos[i], doc_id)
            all_results.append(res)
        return all_results

    def __process_one_tar(self, tar_anno, tar_id, doc_id):
        """
        It processes a target type annotation (specific for MPQA V2.0).
        :param tar_anno: A Python dict which represents a target annotation.
        :param tar_id: ID of the target.
        :param doc_id: ID of the doc.
        :return: A target object.
        """

        if 'sentence-id' in tar_anno:
            sent_id = doc_id + '&&' + tar_anno['sentence-id']
        else:
            sent_id = None

        try:
            # Extract features from target annotation and create an object from them.
            target_object = Target(
                this_id=tar_id,
                this_sentence_id=sent_id,
                this_text=tar_anno['text'],
                this_head_start=tar_anno['span-in-sentence'][0],
                this_head_end=tar_anno['span-in-sentence'][1],
                this_head=tar_anno['head'],
                this_annotation_type=tar_anno['anno-type'],
                unique_id=doc_id + '&&' + tar_id,
                doc_id=doc_id
            )

        except Exception as err:
            self.__alert_wrong_anno(tar_anno, doc_id, error=err)
            return None

        return target_object

    def __process_tar(self, tar_annos, tar_id, doc_id):
        """
        It processes target type annotations (specific for MPQA V2.0).
        :param tar_annos: A Python list which represents some target annotations.
        :param tar_id: ID of the target.
        :param doc_id: ID of the doc.
        :return: One or several target objects.
        """

        all_results = []
        if len(tar_annos) > 1:
            print(f'\033[93m <Warning: Duplicated ID detected: {tar_id} in {doc_id}>\033[00m')
        for i in range(len(tar_annos)):
            if i == 0:
                res = self.__process_one_tar(tar_annos[i], tar_id, doc_id)
            else:
                res = self.__process_one_tar(tar_annos[i], tar_id+"&&"+str(i), doc_id)
            all_results.append(res)
        return all_results

    def __process_one_tf(self, tf_anno, tf_id, doc_id):
        """
        It processes a target frame type annotation.
        :param tf_anno: A Python dict which represents a targetFrame annotation.
        :param tf_id: ID of the targetFrame.
        :param doc_id: ID of the doc.
        :return: A target (target frame) object.
        """

        if 'sentence-id' in tf_anno:
            sent_id = doc_id + '&&' + tf_anno['sentence-id']
        else:
            sent_id = None

        try:
            # Extract features from target frame annotation and create an object from them.
            target_object = Target(
                this_id=tf_id,
                this_sentence_id=sent_id,
                this_text=tf_anno['text'],
                this_head_start=tf_anno['span-in-sentence'][0],
                this_head_end=tf_anno['span-in-sentence'][1],
                this_head=tf_anno['head'],
                this_annotation_type=tf_anno['anno-type'],
                unique_id=doc_id + '&&' + tf_id,
                doc_id = doc_id
            )

        except Exception as err:
            self.__alert_wrong_anno(tf_anno, doc_id, error=err)
            return None

        return target_object

    def __process_tf(self, tf_annos, tf_id, doc_id):
        """
        It processes target frame type annotations.
        :param tf_annos: A Python list which represents some targetFrame annotations.
        :param tf_id: ID of the targetFrame.
        :param doc_id: ID of the doc.
        :return: One or several target (target frame) objects.
        """

        all_results = []

        if len(tf_annos) > 1:
            print(f'\033[93m <Warning: Duplicated ID detected: {tf_id} in {doc_id}>\033[00m')
        for i in range(len(tf_annos)):
            if i == 0:
                res = self.__process_one_tf(tf_annos[i], tf_id, doc_id)
            else:
                res = self.__process_one_tf(tf_annos[i], tf_id+"&&"+str(i), doc_id)
            all_results.append(res)
        return all_results

    def __process_one_starget(self, starget_anno, starget_id, doc_id):
        """
        It processes a sTarget type annotation.
        :param starget_anno: A Python dict which represents a sTarget annotation.
        :param starget_id: ID of the sTarget.
        :param doc_id: ID of the doc.
        :return: A sTarget object.
        """
        try:
            # Extract features from sTarget annotation and create an object from them.
            starget_object = sTarget(
                this_id=starget_id,
                this_sentence_id=doc_id + '&&' + starget_anno['sentence-id'],
                this_text=starget_anno['text'],
                this_head_start=starget_anno['span-in-sentence'][0],
                this_head_end=starget_anno['span-in-sentence'][1],
                this_head=starget_anno['head'],
                this_annotation_type=starget_anno['anno-type'],
                this_etarget_link=self.__add_docname_to_list(doc_id, starget_anno['eTarget-link']),
                unique_id=doc_id + '&&' + starget_id,
                doc_id=doc_id
            )

            # Check 'target-uncertain' which is an optional attribute.
            if 'target-uncertain' in starget_anno:
                starget_object.target_uncertain = starget_anno['target-uncertain']

        except Exception as err:
            self.__alert_wrong_anno(starget_anno, doc_id, error=err)
            return None

        return starget_object

    def __process_starget(self, starget_annos, starget_id, doc_id):
        """
        It processes sTarget type annotations.
        :param starget_annos: A Python list which represents some sTarget annotations.
        :param starget_id: ID of the sTarget.
        :param doc_id: ID of the doc.
        :return: One or several sTarget objects.
        """

        all_results = []
        if len(starget_annos) > 1:
            print(f'\033[93m <Warning: Duplicated ID detected: {starget_id} in {doc_id}>\033[00m')
        for i in range(len(starget_annos)):
            if i == 0:
                res = self.__process_one_starget(starget_annos[i], starget_id, doc_id)
            else:
                res = self.__process_one_starget(starget_annos[i], starget_id+"&&"+str(i), doc_id)
            all_results.append(res)
        return all_results

    def __process_one_etarget(self, etarget_anno, etarget_id, doc_id):
        """
        It processes an eTarget type annotation.
        :param etarget_anno: A Python dict which represents an eTarget annotation.
        :param etarget_id: ID of the eTarget.
        :param doc_id: ID of the doc.
        :return: An eTarget object.
        """
        try:
            # Extract features from eTarget annotation and create an object from them.
            etarget_object = eTarget(
                this_id=etarget_id,
                this_sentence_id=doc_id + '&&' + etarget_anno['sentence-id'],
                this_text=etarget_anno['text'],
                this_head_start=etarget_anno['span-in-sentence'][0],
                this_head_end=etarget_anno['span-in-sentence'][1],
                this_head=etarget_anno['head'],
                this_annotation_type=etarget_anno['anno-type'],
                this_type_etarget=etarget_anno['type'],
                unique_id=doc_id + '&&' + etarget_id,
                doc_id=doc_id
            )

            # Check 'isNegated' and 'isReferredInSpan' which are optional attributes.
            if 'isNegated' in etarget_anno:
                etarget_object.is_negated = etarget_anno['isNegated']

            if 'isReferredInSpan' in etarget_anno:
                etarget_object.is_referred_in_span = etarget_anno['isReferredInSpan']

        except Exception as err:
            self.__alert_wrong_anno(etarget_anno, doc_id, error=err)
            return None

        return etarget_object

    def __process_etarget(self, etarget_annos, etarget_id, doc_id):
        """
        It processes eTarget type annotations.
        :param etarget_annos: A Python list which represents some eTarget annotations.
        :param etarget_id: ID of the eTarget.
        :param doc_id: ID of the doc.
        :return: One or several eTarget objects.
        """

        all_results = []
        if len(etarget_annos) > 1:
            print(f'\033[93m <Warning: Duplicated ID detected: {etarget_id} in {doc_id}>\033[00m')
        for i in range(len(etarget_annos)):
            if i == 0:
                res = self.__process_one_etarget(etarget_annos[i], etarget_id, doc_id)
            else:
                res = self.__process_one_etarget(etarget_annos[i], etarget_id+"&&"+str(i), doc_id)
            all_results.append(res)
        return all_results

    def __process_one_ds(self, ds_anno, ds_id, doc_id):
        """
        It processes a DS (direct-subjective) type annotation.
        :param ds_anno: A Python dict which represents a DS annotation.
        :param ds_id: ID of the DS (direct-subjective) annotation item.
        :param doc_id: Id of the doc.
        :return: A csds object.
        """

        if 'sentence-id' in ds_anno:
            sent_id = doc_id + '&&' + ds_anno['sentence-id']
        else:
            sent_id = None

        if 'attitude-link' in ds_anno:
            att_link = ds_anno['attitude-link']
        else:
            att_link = []

        if 'intensity' in ds_anno:
            inten = ds_anno['intensity']
        else:
            inten = None

        if 'implicit' in ds_anno:
            imp = ds_anno['implicit']
        else:
            imp = None

        if 'polarity' in ds_anno:
            pol = ds_anno['polarity']
        else:
            pol = None

        if 'expression-intensity' in ds_anno:
            exp_int = ds_anno['expression-intensity']
        else:
            exp_int = None

        if 'nested-source' in ds_anno:
            nested_src = self.__add_docname_to_list(
                doc_id,
                ds_anno['nested-source']
            )
        else:
            nested_src = None

        try:
            ds_object = CSDS(
                this_text=ds_anno['text'],
                this_head_start=ds_anno['span-in-sentence'][0],
                this_head_end=ds_anno['span-in-sentence'][1],
                this_belief=None,
                # or maybe the polarity by getting it via attitude-link?
                this_polarity=pol,
                this_intensity=inten,
                this_annotation_type=self.__type_mapper('direct_subjective'),
                this_expression_intensity=exp_int,
                this_attitude_link=self.__add_docname_to_list(doc_id, att_link),
                this_agent_link=nested_src,
                this_head=ds_anno['head'],
                this_doc_id=doc_id,
                this_sentence_id=sent_id,
                this_implicit=imp,
                unique_id=doc_id + '&&' + ds_id
            )


            return ds_object
        except Exception as err:
            self.__alert_wrong_anno(ds_anno, doc_id, error=err)
            return None

    def __process_ds(self, ds_annos, ds_id, doc_id):
        """
        It processes DS (direct-subjective) type annotations.
        :param ds_annos: A Python list which represents some DS annotations.
        :param ds_id: ID of the DS (direct-subjective) annotation item.
        :param doc_id: Id of the doc.
        :return: One or several csds objects.
        """
        all_results = []
        if len(ds_annos) > 1:
            print(f'\033[93m <Warning: Duplicated ID detected: {ds_id} in {doc_id}>\033[00m')
        for i in range(len(ds_annos)):
            if i == 0:
                res = self.__process_one_ds(ds_annos[i], ds_id, doc_id)
            else:
                res = self.__process_one_ds(ds_annos[i], ds_id+"&&"+str(i), doc_id)
            all_results.append(res)
        return all_results

    def __process_one_ose(self, ose_anno, ose_id, doc_id):
        """
        It processes an OSE type annotation.
        :param ose_anno: A Python dict which represents an OSE annotation.
        :param ose_id: ID of the OSE (objective-speech-event) annotation item.
        :param doc_id: Id of the doc.
        :return: A csds object.
        """
        if 'sentence-id' in ose_anno:
            sent_id = doc_id + '&&' + ose_anno['sentence-id']
        else:
            sent_id = None

        if 'implicit' in ose_anno:
            imp = ose_anno['implicit']
        else:
            imp = None

        try:

            ose_object = CSDS(
                this_text=ose_anno['text'],
                this_head_start=ose_anno['span-in-sentence'][0],
                this_head_end=ose_anno['span-in-sentence'][1],
                this_belief=None,
                this_polarity=None,
                this_intensity=None,
                this_annotation_type=self.__type_mapper('objective_speech_event'),
                this_head=ose_anno['head'],
                this_doc_id=doc_id,
                this_sentence_id=sent_id,
                this_implicit=imp,
                this_agent_link=self.__add_docname_to_list(
                    doc_id, ose_anno['nested-source'] if 'nested-source' in ose_anno else []
                ),
                unique_id=doc_id + '&&' + ose_id
            )
            return ose_object
        except Exception as err:
            self.__alert_wrong_anno(ose_id, doc_id, error=err)
            return None

        return None

    def __process_ose(self, ose_annos, ose_id, doc_id):
        """
        It processes OSE (objective-speech-event) type annotation.
        :param ose_annos: A Python list which represents some OSE annotations.
        :param ose_id: ID of the OSE (objective-speech-event) annotation items.
        :param doc_id: Id of the doc.
        :return: One or several csds objects.
        """

        all_results = []
        if len(ose_annos) > 1:
            print(f'\033[93m <Warning: Duplicated ID detected: {ose_id} in {doc_id}>\033[00m')
        for i in range(len(ose_annos)):
            if i == 0:
                res = self.__process_one_ose(ose_annos[i], ose_id, doc_id)
            else:
                res = self.__process_one_ose(ose_annos[i], ose_id+"&&"+str(i), doc_id)
            all_results.append(res)
        return all_results

    def __process_one_sentence(self, sent_anno, sent_id, doc_id):
        """
        It processes a sentence type annotation.
        :param sent_anno: A Python dict which represents a sentence annotation.
        :param sent_id: ID of the sentence annotation item.
        :param doc_id: Id of the doc.
        :return: A csds object.
        """

        try:
            sent_object = CSDS(
                this_text=sent_anno['head'],
                this_head_start=0,
                this_head_end=sent_anno['span-in-doc'][1]-sent_anno['span-in-doc'][0],
                this_belief=None,
                this_polarity=None,
                this_intensity=None,
                this_annotation_type=sent_anno['anno-type'],
                this_head=sent_anno['head'],
                this_doc_id=doc_id,
                this_sentence_id=doc_id + '&&' + sent_id,
                this_implicit=None,
                unique_id=doc_id + '&&' + sent_id
            )
            return sent_object
        except Exception as err:
            self.__alert_wrong_anno(sent_id, doc_id, error=err)
            return None

        return None

    def __process_sentence(self, sent_annos, sent_id, doc_id):
        """
        It processes sentence type annotations.
        :param sent_annos: A Python list which represents some sentence annotations.
        :param sent_id: ID of the sentence annotation items.
        :param doc_id: Id of the doc.
        :return: One or several csds object.
        """

        all_results = []
        if len(sent_annos) > 1:
            print(f'\033[93m <Warning: Duplicated ID detected: {sent_id} in {doc_id}>\033[00m')
        for i in range(len(sent_annos)):
            if i == 0:
                res = self.__process_one_sentence(sent_annos[i], sent_id, doc_id)
            else:
                res = self.__process_one_sentence(sent_annos[i], sent_id+"&&"+str(i), doc_id)
            all_results.append(res)
        return all_results

    def __csds_object2json(self, csds_object):
        """
        It simply converts a CSDS object to JSON file.
        :param csds_object: The CSDS object.
        :return: A JSON file.
        """
        if csds_object:
            json_file = csds_object.__dict__
            return json_file
        else:
            return {}

    def doc2csds(self, json_file, json_output=False):
        """
        It converts a document annotation from JSON to CSDS and Target and Agent.
        :param json_file: The JSON file which is obtained from MPQA to JSON conversion.
        :param json_output: [WHY]
        :return: A triple of collections:
        1. A CSDS collection (several CSDS objects).
        2. A Target collection (several Target objects).
        3. A Agent collection (several Agent objects).
        """
        # List of all document names extracted from the json file.
        doc_list = json_file['doclist']

        # Retrieve all of the document annotations.
        docs = json_file['docs']

        # In here, we create a CSDS collection that stores the CSDS objects.
        ext_csds_coll = CSDSCollection(self.corpus_name)
        # And here, we create a Target collection that stores the Target objects.
        target_coll = TargetCollection(self.corpus_name)
        # And here, we create an Agent collection that stores the Agent objects.
        agent_coll = AgentCollection(self.corpus_name)

        # Process each document.
        for doc_name in doc_list:
            curr_doc = docs[doc_name]

            # Extracts the list of all annotations.
            annotations = curr_doc['annotations']

            if 'agent' in curr_doc:
                # In the following line of code, we extract the IDs of agent type annotations.
                agent_list = curr_doc['agent']
                # Process each agent item by its corresponding ID.
                for agent_id in agent_list:
                    annotation_item = annotations[agent_id]
                    agent_objects = self.__process_agent(annotation_item, doc_name, agent_id=agent_id)
                    # Store the objects!
                    if agent_objects:
                        for agent_object in agent_objects:
                            if agent_object:
                                agent_coll.add_instance(agent_object)
                    del annotation_item
                del agent_list

            # In the following line of code, we extract the IDs of ES type annotations.
            es_list = curr_doc['expressive-subjectivity']
            # Process each ES item by its corresponding ID.
            for es_id in es_list:
                annotation_item = annotations[es_id]
                csds_objects = self.__process_es(annotations, es_id, annotation_item, doc_name)
                # Store the objects!
                if csds_objects:
                    for csds_object in csds_objects:
                        if csds_object:
                            ext_csds_coll.add_labeled_instance(csds_object)
                    del csds_objects
            del es_list

            # In the following line of code, we extract the IDs of attitude type annotations.
            att_list = curr_doc['attitude']
            # Process each attitude item by its corresponding ID.
            for att_id in att_list:
                annotation_item = annotations[att_id]
                csds_objects = self.__process_att(annotations, att_id, annotation_item, doc_name)
                if csds_objects:
                    for csds_object in csds_objects:
                        if csds_object:
                            ext_csds_coll.add_labeled_instance(csds_object)
                    del csds_objects
            del att_list

            if 'target' in curr_doc:
                # In the following line of code, we extract the IDs of target type annotations.
                # Specific for MPQA V2.0
                tar_list = curr_doc['target']
                # Process each target frame item by its corresponding ID.
                for tar_id in tar_list:
                    annotation_item = annotations[tar_id]
                    tar_objects = self.__process_tar(annotation_item, tar_id, doc_name)
                    # Store the objects.
                    if tar_objects:
                        for tar_object in tar_objects:
                            if tar_object:
                                target_coll.add_instance(tar_object)
                        del tar_objects
                del tar_list

            if 'targetFrame' in curr_doc:
                # In the following line of code, we extract the IDs of target frame type annotations.
                tf_list = curr_doc['targetFrame']
                # Process each target frame item by its corresponding ID.
                for tf_id in tf_list:
                    annotation_item = annotations[tf_id]
                    tf_objects = self.__process_tf(annotation_item, tf_id, doc_name)
                    # Store the objects.
                    if tf_objects:
                        for tf_object in tar_objects:
                            if tf_object:
                                target_coll.add_instance(tf_object)
                        del tf_objects
                del tf_list

            if 'sTarget' in curr_doc:
                # In the following line of code, we extract the IDs of sTarget type annotations.
                starget_list = curr_doc['sTarget']
                # Process each sTarget item by its corresponding ID.
                for starget_id in starget_list:
                    annotation_item = annotations[starget_id]
                    starget_objects = self.__process_starget(annotation_item, starget_id, doc_name)
                    # Store the objects.
                    if starget_objects:
                        for starget_object in starget_objects:
                            if starget_object:
                                target_coll.add_instance(starget_object)
                        del starget_objects
                del starget_list

            if 'eTarget' in curr_doc:
                # In the following line of code, we extract the IDs of eTarget type annotations.
                etarget_list = curr_doc['eTarget']
                # Process each eTarget item by its corresponding ID.
                for etarget_id in etarget_list:
                    annotation_item = annotations[etarget_id]
                    etarget_objects = self.__process_etarget(annotation_item, etarget_id, doc_name)
                    # Store the objects.
                    if etarget_objects:
                        for etarget_object in etarget_objects:
                            if etarget_object:
                                target_coll.add_instance(etarget_object)
                        del etarget_objects
                del etarget_list

            if 'direct-subjective' in curr_doc:
                # In the following line of code, we extract the IDs of DS type annotations
                ds_list = curr_doc['direct-subjective']
                # Process each DS item by its corresponding ID
                for ds_id in ds_list:
                    annotation_item = annotations[ds_id]
                    ds_objects = self.__process_ds(annotation_item, ds_id, doc_name)
                    # Store the objects.
                    if ds_objects:
                        for ds_object in ds_objects:
                            if ds_object:
                                ext_csds_coll.add_labeled_instance(ds_object)
                        del ds_objects
                del ds_list

            if 'objective-speech-event' in curr_doc:
                # In the following line of code, we extract the IDs of OSE type annotations
                ose_list = curr_doc['objective-speech-event']
                # Process each OSE item by its corresponding ID
                for ose_id in ose_list:
                    annotation_item = annotations[ose_id]
                    ose_objects = self.__process_ose(annotation_item, ose_id, doc_name)
                    # Store the objects.
                    if ose_objects:
                        for ose_object in ose_objects:
                            if ose_object:
                                ext_csds_coll.add_labeled_instance(ose_object)
                        del ose_objects
                del ose_list

            if 'sentence' in curr_doc:
                # In the following line of code, we extract the IDs of sentence type annotations
                sentence_list = curr_doc['sentence']
                # Process each sentence item by its corresponding ID
                for sentence_id in sentence_list:
                    annotation_item = annotations[sentence_id]
                    sentence_objects = self.__process_sentence(annotation_item, sentence_id, doc_name)
                    # Store the objects.
                    if sentence_objects:
                        for sentence_object in sentence_objects:
                            if sentence_object:
                                ext_csds_coll.add_labeled_instance(sentence_object)
                        del sentence_objects
                del sentence_list

            del annotations

        if json_output:
            csds_coll_lst = ext_csds_coll.get_all_instances()[0]
            target_coll_lst = target_coll.get_all_instances()
            agent_coll_lst = agent_coll.get_all_instances()

            csds_json_files = list(map(self.__csds_object2json, csds_coll_lst))

            target_json_keys = list(target_coll_lst.keys())
            target_json_values = list(map(self.__csds_object2json, target_coll_lst.values()))
            target_json_files = dict(zip(target_json_keys, target_json_values))

            agent_json_keys = list(agent_coll_lst.keys())
            agent_json_values = list(map(self.__csds_object2json, agent_coll_lst.values()))
            agent_json_files = dict(zip(agent_json_keys, agent_json_values))

            overall_result = {
                'corpus_name': self.corpus_name,
                'csds_objects': csds_json_files,
                'target_objects': target_json_files,
                'agent_objects': agent_json_files
            }
            return overall_result
        else:
            return ext_csds_coll, target_coll, agent_coll

########################
